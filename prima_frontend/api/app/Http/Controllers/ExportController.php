<?php

namespace App\Http\Controllers;

use App\Exports\ScenarioProjectsExport;
use App\Exports\UsersExport;
use App\Http\Requests\DownloadProjectsRequest;
use App\Http\Requests\ExportRankedWellsRequest;
use App\Http\Requests\ExportRawDataRequest;
use App\Models\Scenario;
use App\Repositories\ExportRepository;
use Carbon\Carbon;
use Exception;
use Illuminate\Support\Facades\Log;
use Illuminate\Support\Facades\Storage;
use Maatwebsite\Excel\Excel as ExcelExcel;
use Maatwebsite\Excel\Facades\Excel;

class ExportController extends Controller
{
    public function exportRankedData(ExportRankedWellsRequest $request)
    {
        try {
            return Excel::download(
                $this->parseRequestToExportRepository($request)->generateRankedWellsExport(),
                now()->toDateTimeLocalString().' - '.$request->user()->name.'.xlsx'
            );
        } catch (\Exception $e) {
            Log::error('Error downloading ranked wells: '.$e->getMessage());
            Log::error($e->getTraceAsString());

            return response()->json(['message' => 'Failed to export ranked wells.', 'error' => $e->getMessage()], 500);
        }
    }

    public function exportRawData(ExportRawDataRequest $request)
    {
        try {
            return Excel::download(
                $this->parseRequestToExportRepository($request)->generateRawDataExport(),
                now()->toDateTimeLocalString().' - '.$request->user()->name.'.xlsx'
            );
        } catch (\Exception $e) {
            Log::error('Error downloading raw well data: '.$e->getMessage());
            Log::error($e->getTraceAsString());

            return response()->json(['message' => 'Failed to export raw well data.', 'error' => $e->getMessage()], 500);
        }
    }

    public function exportScenarioRanking(Scenario $scenario, ExportRankedWellsRequest $request)
    {
        try {
            return Excel::download(
                $this->parseRequestToExportRepository($request, $scenario)->generateScenarioRankedWellsExport(),
                now()->toDateTimeLocalString().' - '.$request->user()->name.'.xlsx'
            );
        } catch (\Exception $e) {
            Log::error('Error downloading ranked wells: '.$e->getMessage());
            Log::error($e->getTraceAsString());

            return response()->json(['message' => 'Failed to export ranked wells.', 'error' => $e->getMessage()], 500);
        }
    }

    public function downloadProjects(DownloadProjectsRequest $request)
    {
        $validated = $request->validated();
        $path = $validated['image']->store('temp');
        $scenario = Scenario::findOrFail($validated['scenario_id']);

        try {
            return (new ScenarioProjectsExport(
                $path,
                json_decode($validated['project_id_color_map']) ?? [],
                $validated['width'],
                $validated['height'],
                $scenario,
            ))->download(now()->toDateTimeLocalString().' - '.$request->user()->name.'.xlsx');

        } catch (Exception $error) {
            Log::error('Error downloading projects: '.$error->getMessage());
            Log::error($error->getTraceAsString());

            return response()->json(['message' => $error->getMessage()], 500);
        } finally {
            // Delete the temporary file
            if ($path) {
                Storage::delete($path);
            }
        }
    }

    public function exportUserList()
    {
        try {
            return Excel::download(new UsersExport, 'users-list_'.config('app.env').' - '.Carbon::now()->format('Y-m-d').'.csv', ExcelExcel::CSV);
        } catch (Exception $error) {
            Log::error('Error downloading user list: '.$error->getMessage());
            Log::error($error->getTraceAsString());

            return response()->json(['message' => $error->getMessage()], 500);
        }
    }

    private function parseRequestToExportRepository(
        ExportRankedWellsRequest|ExportRawDataRequest $request,
        ?Scenario $scenario = null
    ): ExportRepository {
        $validated = $request->validated();

        return new ExportRepository(
            $validated['columns'],
            $validated['sort_field'],
            $validated['sort_order'],
            $validated['well_type'],
            $request instanceof ExportRankedWellsRequest ? $validated['task_id'] : $validated['dataset_id'],
            $request instanceof ExportRawDataRequest ? $validated['task_id'] : null,
            $scenario ?? null
        );
    }
}
