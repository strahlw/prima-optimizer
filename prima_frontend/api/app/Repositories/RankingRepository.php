<?php

namespace App\Repositories;

use App\Models\Ranking;
use Illuminate\Pagination\LengthAwarePaginator;
use Illuminate\Support\Collection;
use Illuminate\Support\Str;

class RankingRepository
{
    public function baseModelSortFieldSearch(
        string $sortField,
        string $sortOrder,
        string $taskId,
        array $wellTypes,
        ?int $perPage = null,
        ?int $page = null,
    ): Collection|LengthAwarePaginator {
        $paginate = ! is_null($perPage) && ! is_null($page);
        $rankingData = Ranking::where('task_id', $taskId)
            ->when(! empty($wellTypes), function ($query) use ($wellTypes) {
                $query->whereHas('datasetJson', function ($query) use ($wellTypes) {
                    $query->whereIn('json.well_type', $wellTypes);
                });
            })
            ->with('datasetJson')
            ->orderBy($sortField, $sortOrder)
            ->when($sortField !== 'well_rank', function ($query) {
                return $query->orderBy('well_rank', 'asc');
            })
            ->when($paginate, function ($query) use ($perPage, $page) {
                return $query->paginate($perPage, ['*'], 'page', $page);
            });

        $rankingCollection = $paginate ? $rankingData->getCollection() : $rankingData->get();

        $convertedData = $rankingCollection->map(function ($ranking) {
            $json = array_merge($ranking->datasetJson->json, $ranking->toArray());

            array_walk_recursive($json, function (&$value) {
                if (is_float($value) && (is_nan($value) || is_infinite($value))) {
                    $value = null;
                }
            });

            return $json;
        });

        if ($paginate) {
            $rankingData->setCollection($convertedData);

            return $rankingData;
        }

        return $convertedData;
    }

    public function datasetJsonFieldSearch(
        string $sortField,
        string $sortOrder,
        string $taskId,
        array $wellTypes,
        ?int $perPage = null,
        ?int $page = null,
    ): array {
        $rankingData = Ranking::raw(function ($collection) use ($taskId, $sortField, $sortOrder, $wellTypes, $perPage, $page) {
            $pipeline = [
                ['$match' => ['task_id' => $taskId]], // Match task_id
                [
                    '$lookup' => [
                        // Join datasetJson
                        'from' => 'dataset_jsons', // Name of the related collection
                        'let' => ['localField' => ['$toObjectId' => '$dataset_json_id']], // Convert localField to ObjectID
                        'pipeline' => [
                            [
                                '$match' => [
                                    '$expr' => [
                                        '$eq' => ['$_id', '$$localField'], // Match _id with converted localField
                                    ],
                                ],
                            ],
                        ],
                        'as' => 'datasetJson',
                    ],
                ],
                ['$unwind' => '$datasetJson'],
                // TODO: Verify "Gas and Oil" is actually working as expected
                ['$match' => ['datasetJson.json.well_type' => ['$in' => empty($wellTypes) ? ['Oil', 'Gas', 'Gas and Oil'] : $wellTypes]]], // Match well_type
                [
                    '$sort' => [
                        // Sort by nested field
                        'datasetJson.json.'.$sortField => $sortOrder == 'desc' ? -1 : 1,
                        'datasetJson.json.well_rank' => 1, // Secondary sort by well_rank
                    ],
                ],
            ];

            if ($perPage > 0) {
                $pipeline[] = [
                    '$facet' => [
                        'data' => [
                            ['$skip' => $perPage * ($page - 1)],
                            ['$limit' => $perPage],
                        ],
                        'total' => [['$count' => 'count']],
                    ],
                ];
            } else {
                $pipeline[] = [
                    '$facet' => [
                        'data' => [
                            // If no pagination, just pass through all data
                            ['$match' => (object) []], // Match everything, effectively a pass-through
                        ],
                    ],
                ];
            }

            return $collection->aggregate($pipeline);
        });

        $result = iterator_to_array($rankingData);

        // Convert results to array and handle float values
        $convertedData = array_map(function ($ranking) {
            $rankingArray = json_decode(json_encode($ranking), true); // Convert BSON to PHP array
            $json = array_merge($rankingArray['datasetJson']['json'], $rankingArray);
            array_walk_recursive($json, function (&$value) {
                if (is_float($value) && (is_nan($value) || is_infinite($value))) {
                    $value = null;
                }
            });

            return $json;
        }, iterator_to_array($result[0]['data'] ?? []));

        $convertedData['total'] = $result[0]['total'][0]['count'] ?? null;

        return $convertedData;
    }

    public function getRankingData(
        string $taskId,
        int $perPage,
        int $page,
        string $sortField,
        string $sortOrder,
        array $wellTypes,
    ): LengthAwarePaginator {
        $baseModelFields = array_keys(Ranking::where('task_id', $taskId)->first()->toArray());
        $isBaseModelSortField = in_array(Str::snake($sortField), $baseModelFields);
        $sortOrder = strtolower($sortOrder) === '-1' ? 'desc' : 'asc';

        if (! is_null($sortField)) {
            $sortField = Str::snake($sortField);
        }

        if ($isBaseModelSortField) {
            return $this->baseModelSortFieldSearch(
                $sortField,
                $sortOrder,
                $taskId,
                $wellTypes,
                $perPage,
                $page
            );
        } else {
            $convertedData = $this->datasetJsonFieldSearch($sortField, $sortOrder, $taskId, $wellTypes, $perPage, $page);
            $total = $convertedData['total'];

            $paginatedData = new LengthAwarePaginator($convertedData, $total, $perPage, $page);

            return $paginatedData;
        }
    }
}
