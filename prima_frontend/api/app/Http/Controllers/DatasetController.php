<?php

namespace App\Http\Controllers;

use App\Exceptions\PrimoValidationException;
use App\Exports\WellDataImportTemplate;
use App\Http\Requests\StoreDatasetRequest;
use App\Jobs\DeleteFile;
use App\Models\Dataset;
use App\Models\Organization;
use App\Repositories\DataImportRepository;
use App\Repositories\DatasetJsonRepository;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Log;
use Illuminate\Support\Facades\Storage;
use Maatwebsite\Excel\Facades\Excel;

class DatasetController extends Controller
{
    public function index(Request $request)
    {
        $organizationId = $request->query('organization_id') ? (int) $request->query('organization_id') : null;
        $mustContainRanking = $request->boolean('ranking');
        $all = $request->boolean('all', false);
        $user = $request->user();

        if ($organizationId && ! ($user->hasRole('super-admin') || $user->organization_id === $organizationId)) {
            return response()->json(['message' => 'Unauthorized'], 403);
        }

        $baseQuery = fn () => Dataset::when(! $all, function ($q) use ($mustContainRanking) {
            $q->where('contains_ranking', $mustContainRanking);
        })->with(['user', 'organization']);

        if ($organizationId) {
            $datasets = $baseQuery()->where('organization_id', $organizationId)->get();

            return response()->json($datasets, 200);
        }

        if ($user->hasRole('super-admin')) {
            $datasets = $baseQuery()->get()->groupBy(fn (Dataset $d) => $d->organization->name);

            return response()->json($datasets, 200);
        }

        $datasets = $baseQuery()->where('organization_id', $user->organization_id)->get();
        $organizationName = Organization::find($user->organization_id)?->name ?? 'Unknown';

        return response()->json([$organizationName => $datasets], 200);
    }

    public function show(Request $request, Dataset $dataset, DatasetJsonRepository $repository)
    {
        try {
            $perPage = $request->query('rows');
            $page = $request->query('page');
            $sortOrder = $request->query('sortOrder', 'asc');
            $sortField = $request->query('sortField', 'json.well_id');
            $wellTypes = $request->query('wellType', []);
            $taskId = $request->query('taskId');
            $mapOnly = $request->query('mapOnly'); // Retrieve only map-necessary fields
            $sortOrder = strtolower($sortOrder) === '-1' ? 'desc' : 'asc';

            $results = $repository->searchDatasetJsonWells(
                $dataset,
                $perPage,
                $page,
                $sortField,
                $sortOrder,
                $wellTypes,
                $mapOnly,
                $taskId
            );

            if (is_array($results)) {
                return response()->json(['data' => $results], 200);
            } else {
                return response()->json($results);
            }

            return response()->json(['data' => $results], 200);
        } catch (\Exception $e) {
            Log::error($e);

            return response()->json(['message' => 'Error fetching dataset wells'], 500);
        }
    }

    public function store(StoreDatasetRequest $request, DataImportRepository $repository)
    {
        $user = $request->user();

        if (! $user->hasRole('super-admin') && ! $request->input('organization_id') === $user->organization_id) {
            return response()->json(['message' => 'Unauthorized'], 403);
        }

        $file = $request->file('file');
        $additional = $request->input('additional');
        $organizationId = (int) $request->input('organization_id');
        $filePath = $repository->storeDatasetUpload($file, $organizationId, $additional);
        $response = null;

        try {
            $result = $repository->processDatasetUpload($file, $organizationId, $user, $filePath, $additional);
            $dataset = $result['dataset'];

            $response = response()->json(['message' => "Dataset file uploaded {$request->file('file')->getClientOriginalName()}.", 'files' => [$dataset->name]], 201);
        } catch (PrimoValidationException $e) {
            return response()->json(['message' => 'Validation failed', 'errors' => explode('<br>', $e->getMessage())], 403);
        } catch (\Exception $e) {
            Log::error($e);

            return response()->json(['message' => 'Error uploading file'], 500);
        } finally {
            if ($filePath) {
                if (app()->environment('local')) {
                    DeleteFile::dispatch(Storage::disk('shared')->path($filePath));
                } else {
                    DeleteFile::dispatch('tmp/'.$filePath);
                }
            }
            if ($response) {
                return $response;
            }
        }
    }

    public function getTemplate()
    {
        try {
            return Excel::download(new WellDataImportTemplate, 'well_data_template.xlsx', \Maatwebsite\Excel\Excel::XLSX);
        } catch (\Exception $e) {
            Log::error($e);

            return response()->json(['message' => 'Error downloading template'], 500);
        }
    }
}
