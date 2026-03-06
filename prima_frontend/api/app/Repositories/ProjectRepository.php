<?php

namespace App\Repositories;

use App\Models\DatasetJson;
use App\Models\Project;
use App\Models\Well;
use Illuminate\Pagination\LengthAwarePaginator;
use Illuminate\Support\Collection;

class ProjectRepository
{
    protected array $baseModelFields = ['priority_score', 'efficiency_score', 'well_rank', 'well_id'];

    public function searchWellsAndDatasets(
        Project $project,
        int $perPage,
        int $page,
        string $sortOrder,
        $sortField,
        $addedDatasetWellIds = null,
        $addedWellIds = null
    ) {
        $isBaseModelSortField = in_array($sortField, $this->baseModelFields);
        if (! is_null($sortField)) {
            $sortField = $isBaseModelSortField ? $sortField : 'json.'.$sortField;
        }
        $sortInt = $sortOrder === 'asc' ? 1 : -1;

        // If the sort field is a field on the Well mongoDB record
        $wells = $project->wells()
            ->orderBy($sortField, $sortOrder)
            ->when($sortField !== 'well_id', function ($query) {
                return $query->orderBy('well_id', 'asc');
            })->get();

        // If wells from other projects have been reassigned
        if ($addedWellIds) {
            $addedWells = $project->scenario
                ->wells()
                ->filter(fn ($well) => in_array($well->well_id, $addedWellIds))
                ->sortBy($sortField, $sortInt)
                ->when($sortField !== 'well_id', function ($query) {
                    return $query->sortBy('well_id', 1);
                });

            $wells = $wells->concat($addedWells)->unique('well_id');
        }

        $wells = $wells->load('datasetJson')->sortBy($sortField, $sortInt);

        // If there are added well IDs, retrieve them
        if ($addedDatasetWellIds) {
            $addedDatasetWells = DatasetJson::whereIn('json.well_id', $addedDatasetWellIds)
                ->where('dataset_id', $project->scenario->dataset_id)
                ->get();

            // Combine original wells with added wells
            $combinedWells = $wells->concat($addedDatasetWells)->unique('json.well_id')->sortBy('json.well_rank');
        } else {
            $combinedWells = $wells;
        }

        return $this->loadAndPaginateData($combinedWells, $sortField, $sortOrder, $page, $perPage, $project);
    }

    // Given combined wells, load any extra fields needed and return a paginated version.
    private function loadAndPaginateData(
        Collection $combinedWells,
        string $sortField,
        string $sortOrder,
        int $page,
        int $perPage,
        ?Project $project = null
    ): LengthAwarePaginator {
        if (! str_starts_with($sortField, 'json.')) {
            $sortField = str_replace('json.', '', $sortField);
            $combinedWells->load(['datasetJson']);
        }

        $sortedWells = $combinedWells->sortBy(
            function ($well) use ($sortField) {
                if ($well instanceof DatasetJson && ! str_starts_with($sortField, 'json.')) {
                    return (int) data_get($well, 'json.'.$sortField);
                } else {
                    return data_get($well, $sortField);
                }
            },
            SORT_REGULAR,
            $sortOrder === 'desc'
        );

        $startingPoint = ($page * $perPage) - $perPage;
        $slicedWells = $sortedWells->slice($startingPoint, $perPage);

        // Map the collection to return the desired JSON structure
        $convertedData = $slicedWells->map(function ($well) use ($project) {
            $data = [...$well->json,
                'id' => $well->id,
                'well_rank' => $well->well_rank,
                'priority_score' => $well->priority_score,
                'efficiency_score' => $well->efficiency_score,
            ];

            if ($well instanceof Well) {
                // NOTE: This was changed specifically for overrides, it made break other functionality
                if ($project) {
                    $data['projects'] = collect([$project]);
                } else {
                    $data['projects'] = $well->getProjects();
                }

                $data['project_id'] = $project?->id;
            }

            return $data;
        })->values();

        $paginatedData = new \Illuminate\Pagination\LengthAwarePaginator(
            $convertedData, // Items for the current page
            $combinedWells->count(), // Total number of items
            $perPage, // Items per page
            $page, // Current page
        );

        return $paginatedData;
    }
}
