<?php

namespace App\Repositories;

use App\Models\Dataset;
use App\Models\DatasetImportColumn;
use App\Models\DatasetJson;
use App\Models\User;
use App\Services\PrimoApiService;
use Exception;
use Illuminate\Http\UploadedFile;
use Illuminate\Support\Facades\Log;

class DataImportRepository
{
    public function storeDatasetUpload(UploadedFile $file, int $organizationId, bool $additional = false): string
    {
        $fileOriginalName = $file->getClientOriginalName();
        if ($additional) {
            $path = $file->storeAs('/'.$organizationId.'/additional', $fileOriginalName, 'tmp');
        } else {
            if (app()->environment('local')) {
                $path = $file->storeAs('/'.$organizationId, $fileOriginalName, 'shared');
            } else {
                $path = $file->storeAs('/'.$organizationId, $fileOriginalName, 'tmp');
            }
        }

        return $path;
    }

    public function processDatasetUpload(
        UploadedFile $file,
        int $organizationId,
        User $user,
        string $filePath,
        bool $additional = false
    ): array {
        $datasetId = null;
        $dataset = null;
        $path = null;
        $apiService = app()->make(PrimoApiService::class);

        try {
            $fileOriginalName = $file->getClientOriginalName();
            $dataset = Dataset::create([
                'organization_id' => $organizationId,
                'uploaded_by_id' => $user->id,
                'name' => $fileOriginalName,
                'file_path' => $filePath,
                'additional' => $additional,
            ]);
            $datasetId = $dataset->id;

            if (! $additional) {
                $responseData = $apiService->uploadDataset($filePath, $datasetId);
                if ($responseData && $responseData->contains_ranking) {
                    $dataset->update(['contains_ranking' => true]);
                }
            }

            return ['path' => $path, 'dataset' => $dataset];
        } catch (Exception $error) {

            if ($datasetId) {
                DatasetJson::where('dataset_id', $datasetId)->forceDelete();
            }

            if ($dataset) {
                $dataset->forceDelete();
            }

            Log::error('Error processing dataset upload: '.$error->getMessage());
            throw $error;
        }
    }

    private function normalizeString($string): string
    {
        // Replace any non-alphanumeric characters except spaces
        $normalized = preg_replace("/\[[^\]]*\]|\s|[^\w\-]/", '', strtolower($string));

        // Remove spaces to concatenate words
        return str_replace(' ', '', $normalized);
    }

    public function getHeadingMapping(): array
    {
        return DatasetImportColumn::all()->mapWithKeys(function (DatasetImportColumn $column) {
            return [
                $this->normalizeString($column->label) => $column->key,
            ];
        })->toArray();
    }

    public function formatHeadingRow(?string $value): ?string
    {
        try {
            // Normalize the input value
            $normalizedValue = $this->normalizeString($value);

            // TODO: Allow dynamically setting alternate headings for specific datasets

            // Get heading mapping from the dataset import columns
            $headingMapping = $this->getHeadingMapping();

            // Return the mapped key if available
            return $headingMapping[$normalizedValue] ?? null;
        } catch (\Exception $e) {
            // Log the exception if needed
            Log::error('Error formatting heading row: '.$e->getMessage());

            return null;
        }
    }

    public function transformImportColumnErrors(array $errors): array
    {
        // Fetch labels from the database (assuming you have a `key` and `label` column)
        $labelMap = DatasetImportColumn::pluck('label', 'key')->toArray();

        // Transform the error messages
        return array_map(function ($error) use ($labelMap) {
            // Iterate over each key in the labelMap and replace in the error message
            foreach ($labelMap as $key => $label) {
                // Use str_replace to replace snake_case with the human-readable label
                $error = str_replace($key, $label, $error);
            }

            return $error;
        }, $errors);
    }
}
