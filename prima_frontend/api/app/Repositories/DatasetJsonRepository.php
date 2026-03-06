<?php

namespace App\Repositories;

use App\Models\Dataset;
use App\Models\DatasetImportColumn;
use App\Models\DatasetJson;
use Illuminate\Pagination\LengthAwarePaginator;
use Illuminate\Support\Collection;
use Illuminate\Support\Str;

class DatasetJsonRepository
{
    protected RankingRepository $rankingRepository;

    protected array $keyToLabelArray;

    public function __construct(RankingRepository $rankingRepository)
    {
        $this->keyToLabelArray = DatasetImportColumn::all()->flatMap(function (DatasetImportColumn $column) {
            return [$column->key => $column->label];
        })->toArray();

        $this->rankingRepository = $rankingRepository;
    }

    public function convertModelToArray(DatasetJson $datasetJson): array
    {
        $data = collect($datasetJson->json)->flatMap(function ($item, string $key) {
            if (array_key_exists($key, $this->keyToLabelArray)) {
                return [$key => ['value' => $item, 'label' => $this->keyToLabelArray[$key]]];
            }

        });

        return $data->toArray();
    }

    public function sortDatasetJsonWells(
        Dataset $dataset,
        $sortField,
        string $sortOrder,
        array $wellTypes,
        ?int $perPage = null,
        ?int $page = null,
        ?string $taskId = null
    ): LengthAwarePaginator|Collection {
        $paginate = ! is_null($perPage) && ! is_null($page);
        if ($taskId) {
            // If the task ID is provided, it is assumed the field doesn't exist on raw data, and the order of ranked data must be followed.
            $paginatedRankData = $this->rankingRepository->baseModelSortFieldSearch(
                $sortField,
                $sortOrder,
                $taskId,
                $wellTypes,
                $perPage,
                $page
            );

            $rawData = $paginate ? $paginatedRankData->getCollection() : $paginatedRankData;

            $datasetJsonIds = $rawData->pluck('dataset_json_id')->toArray();
            $records = DatasetJson::whereIn('id', $datasetJsonIds)->get();
            $orderedRecords = $records->sortBy(function ($record) use ($datasetJsonIds) {
                return array_search($record->id, $datasetJsonIds);
            });

            if (! $paginate) {
                return $orderedRecords;
            }

            $paginatedRankData->setCollection($orderedRecords);

            return $paginatedRankData;
        } else {
            $sortField = str_starts_with($sortField, 'json.') ? $sortField : 'json.'.$sortField;

            // Fetch paginated data
            $rawData = DatasetJson::where('dataset_id', $dataset->id)
                ->when($wellTypes, function ($query) use ($wellTypes) {
                    $query->whereIn('json.well_type', $wellTypes);
                })
                ->orderBy($sortField, $sortOrder)
                ->when($sortField !== 'json.well_id', function ($query) {
                    return $query->orderBy('json.well_id', 'asc');
                })
                ->when($perPage || $page, function ($query) use ($perPage, $page) {
                    return $query->paginate($perPage, ['*'], 'page', $page);
                });

            if (! $paginate) {
                return $rawData->get();
            }

            return $rawData;
        }
    }

    public function searchDatasetJsonWells(
        Dataset $dataset,
        ?int $perPage,
        ?int $page,
        $sortField,
        string $sortOrder,
        array $wellTypes,
        ?bool $mapOnly = false,
        ?string $taskId = null
    ) {
        if (! is_null($sortField) && is_null($taskId)) {
            $sortField = 'json.'.Str::snake($sortField);
        } else {
            $sortField = Str::snake($sortField);
        }

        if ($mapOnly) {
            $array = DatasetJson::where('dataset_id', $dataset->id)
                ->select(['json.well_id', 'json.latitude', 'json.longitude', 'json.well_name', 'json.well_type', 'json.operator_name'])
                ->get()
                ->map(function (DatasetJson $json) {
                    return $this->convertModelToArray($json);
                })->toArray();

            return $array;
        } else {
            $paginatedData = $this->sortDatasetJsonWells($dataset, $sortField, $sortOrder, $wellTypes, $perPage, $page, $taskId);

            $convertedData = $paginatedData->getCollection()->map(function (DatasetJson $json) {
                return $this->convertModelToArray($json);
            });

            // Replace the paginated data collection with the converted array
            $paginatedData->setCollection($convertedData);

            return $paginatedData;
        }

    }
}
