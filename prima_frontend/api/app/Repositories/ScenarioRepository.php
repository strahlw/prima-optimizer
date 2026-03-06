<?php

namespace App\Repositories;

use App\Enum\ScenarioStatus;
use App\Enum\TaskStatus;
use App\Exceptions\PrimoApiException;
use App\Models\DatasetJson;
use App\Models\Project;
use App\Models\Scenario;
use App\Models\Task;
use App\Models\User;
use App\Models\Well;
use App\Services\PrimoApiService;
use App\Types\GeneralSpecifications;
use App\Types\RankOnlyScenarioData;
use App\Types\RecommendationOnlyScenarioData;
use App\Types\ScenarioData;
use App\Types\ScenarioOverrideData;
use Illuminate\Support\Collection;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Log;

class ScenarioRepository
{
    public PrimoApiService $primoApiService;

    public function __construct(PrimoApiService $primoApiService)
    {
        $this->primoApiService = $primoApiService;
    }

    public function getProjectsAndWellCounts(Collection $scenarios)
    {
        return $scenarios->map(function (Scenario $scenario) {
            $scenario['projects'] = $scenario->projects->map(function (Project $project) {
                $project->append('wellCount');

                return $project;
            });

            return $scenario;
        });
    }

    public function getFormattedProjectsAndScores(Scenario $scenario, bool $mapOnly = false)
    {
        $mappedProjects = $scenario->projects->map(function (Project $project) use ($mapOnly) {
            $project->append('wellCount');
            $project->append('parentProjectDifferentials');
            $mappedWells = $project->getWells()->map(function (Well $well) use ($mapOnly) {
                if ($mapOnly) {
                    return [
                        'id' => $well->well_id,
                        'well_id' => $well->well_id,
                        'longitude' => $well->json['longitude'],
                        'latitude' => $well->json['latitude'],
                        'well_name' => $well->json['well_name'] ?? '',
                        'well_type' => $well->json['well_type'],
                        'projects' => $well->getProjects(),
                        'operator_name' => $well->json['operator_name'],
                    ];
                } else {
                    return [
                        // 'id' => $well->json['well_id'],
                        // 'scenario_id' => $well->scenario_id,
                        // 'project_id' => $well->project_id,
                        // ...$well->json,
                    ];
                }

            });

            return [
                ...$project->toArray(),
                'wells' => $mappedWells,
            ];
        });

        $scenario->setRelation('projects', $mappedProjects);
        $scenario['latitude'] = (float) $scenario->organization->latitude;
        $scenario['longitude'] = (float) $scenario->organization->longitude;
        $scenario->load('dataset');
        $scenario->load('user');
        $scenario->load('copyParent');

        return $scenario;
    }

    public function createRanking(ScenarioData|RankOnlyScenarioData|RecommendationOnlyScenarioData $scenarioData)
    {
        try {
            $this->primoApiService->verifyConnection();
            $response = $this->primoApiService->runRanking($scenarioData);
            if ($response->status === TaskStatus::SUCCESS) {
                return $response->taskId; // return task id to send to FE
            }

        } catch (\Exception $e) {
            throw $e;
        }
    }

    public function getScenariosByUserRole(
        User $user,
        int $perPage = 10,
        int $page = 1,
        ?int $organizationId = null,
        ?array $filters = null,
        ?int $scenarioId = null
    ) {
        $baseQuery = Scenario::where('status', ScenarioStatus::PUBLISHED)
            ->when(! $user->hasRole('super-admin'), fn ($q) => $q->where('organization_id', $user->organization_id))
            ->when($organizationId, fn ($q) => $q->where('organization_id', $organizationId))
            ->when($filters, function ($q) use ($filters) {
                $filterCount = count($filters);
                $q->whereHas('types', function ($subQ) use ($filters) {
                    $subQ->whereIn('name', $filters);
                }, '=', $filterCount)
                    ->whereDoesntHave('types', function ($subQ) use ($filters) {
                        $subQ->whereNotIn('name', $filters);
                    });
            });

        if ($scenarioId) {
            $targetScenario = (clone $baseQuery)->where('id', $scenarioId)->first();

            if (! $targetScenario) {
                return null;
            }

            $countBefore = (clone $baseQuery)
                ->where('id', '<', $targetScenario->id)
                ->count();

            $page = intdiv($countBefore, $perPage) + 1;
        }

        $paginatedScenarios = (clone $baseQuery)
            ->with(['user', 'parent', 'copyParent', 'types'])
            ->paginate($perPage, ['*'], 'page', $page);

        $transformedData = $this->getProjectsAndWellCounts($paginatedScenarios->getCollection());

        return [
            'data' => $transformedData,
            'meta' => [
                'current_page' => $paginatedScenarios->currentPage(),
                'last_page' => $paginatedScenarios->lastPage(),
                'per_page' => $paginatedScenarios->perPage(),
                'total' => $paginatedScenarios->total(),
                'from' => $paginatedScenarios->firstItem(),
                'to' => $paginatedScenarios->lastItem(),
            ],
        ];
    }

    public function killOptimization(Scenario $scenario, User $user): Scenario
    {
        DB::beginTransaction();

        try {
            $this->primoApiService->verifyConnection();
            $this->primoApiService->killOptimization($scenario->task->task_id);

            $scenario->task->update([
                'status' => TaskStatus::KILLED,
                'status_by_id' => $user->id,
            ]);

            $scenario->update(['status' => ScenarioStatus::KILLED, 'status_by_id' => $user->id]);

            DB::commit();

            return $scenario;
        } catch (PrimoApiException $e) {
            DB::rollBack();
            throw $e;
        } catch (\Exception $e) {
            DB::rollBack();
            Log::error("An error occurred while killing scenario $scenario->id: {$e->getMessage()} {$e->getTraceAsString()}");
            throw $e;
        }
    }

    public function searchAvailableWellIds(
        $query,
        Scenario $scenario,
        array $includedWellIds = [],
        array $inactiveProjectIds = [],
        array $excludedDatasetWellIds = [],
        array $reassignedWellIds = [],
        array $wellTypes = []
    ): array {
        // TODO: Determine if the team needs every well to be returned
        // When utilizing Scenario Overrides, search all available Well Ids for the Scenario
        $inactiveProjectWellIds = Project::whereIn('id', $inactiveProjectIds)
            ->get()
            ->flatMap(function ($project) {
                return $project->getWells()->pluck('id');
            });

        $activeProjects = collect();

        $activeProjectWellIds = $scenario->projects->filter(function (Project $project) use ($inactiveProjectIds) {
            return ! in_array($project->id, $inactiveProjectIds);
        })->map(function ($project) use (&$activeProjects) {
            $activeProjects->push($project);

            return $project->getWells()->pluck('id');
        })->flatten()->toArray();

        $includedWellIds = $activeProjects->flatMap(function (Project $project) use ($includedWellIds) {
            return $project->getWells()->filter(function (Well $well) use ($includedWellIds) {
                return in_array($well->well_id, $includedWellIds);
            })->pluck('id');
        })->toArray();

        // Perform 2 queries to ensure that the pool from the frontend action is prioritized
        $wellPool = Well::whereNotIn('well_id', $reassignedWellIds)
            ->whereIn('id', [...$includedWellIds, ...$inactiveProjectWellIds])
            ->get();

        // For now as we are limiting to 30, only take up to 30 when loading relationship
        $wellPool = $wellPool->take(30)->map(function (Well $well) {
            $well->append('json');
            $well->projects = $well->getProjects();

            return $well;
        });

        $wellIdsToExclude = Well::whereIn('id', [...$includedWellIds, ...$reassignedWellIds, ...$inactiveProjectWellIds, ...$excludedDatasetWellIds, ...$activeProjectWellIds])
            ->get()
            ->pluck('well_id')
            ->toArray();

        $otherWells = DatasetJson::where('dataset_id', $scenario->dataset_id)
            ->whereIn('json.well_type', $wellTypes)
            ->whereNotIn('json.well_id', array_merge($wellIdsToExclude, $excludedDatasetWellIds)) // Exclude wells that are already reassigned to projects
            ->get();

        // Merge the collections, with included wells appearing first
        $datasets = $wellPool->merge($otherWells)->unique('json.well_id');

        $filteredResults = $datasets->filter(function ($dataset) use ($query) {
            // Assuming json.well_id is stored as a long and you're searching against its string representation
            // Convert the well_id to string and check if it contains the query
            return strpos((string) $dataset->json['well_id'], $query) !== false;
        })->map(function ($dataset) use ($scenario) {
            $data = [...$dataset->json];

            if ($dataset instanceof Well) {
                $data = [...$data,
                    'id' => $dataset->id,
                    'well_rank' => $dataset->well_rank,
                    'priority_score' => $dataset->priority_score,
                    'efficiency_score' => $dataset->efficiency_score,
                    'projects' => $dataset->getProjects()->filter(fn ($project) => $project->scenario_id === $scenario->id)->values(),
                ];
            }

            return $data;
        });

        return $filteredResults->take(30)->values()->toArray();
    }

    public function overrideScenario(ScenarioOverrideData $overrideData, Scenario $parentScenario, User $user)
    {
        // Step 1: Create Child Scenario
        // Step 2: Send Details to Primo API

        // No use of trasnaction due to issues rising with Python DB entries
        // TODO: look into cleaning up newly create mongodb records

        $childScenario = null;

        try {
            $this->primoApiService->verifyConnection();

            // Create a non-referencing copy
            $childData = array_merge((array) $overrideData, $parentScenario->data);
            $childData['name'] = $overrideData->name;
            $childData['general_specifications']['name'] = $overrideData->name;

            $childScenario = Scenario::create([
                'name' => $childData['name'],
                'user_id' => $user->id,
                'organization_id' => $parentScenario->organization_id,
                'status_by_id' => $user->id,
                'status' => ScenarioStatus::PUBLISHED,
                'dataset_id' => $parentScenario->dataset_id,
                'parent_id' => $parentScenario->id,
                'data' => $childData,
            ]);

            $childScenario->addTypePivotEntries($parentScenario->types->pluck('name')->toArray());

            $this->primoApiService->createOverrideScenario($parentScenario, $childScenario, $this->convertOverrideDataToRequestObject($overrideData));

            return $childScenario->id;
        } catch (\Exception $e) {
            // Delete child Scenario, projects, and pivot table records
            if ($childScenario) {
                if ($childScenario->projects) {
                    foreach ($childScenario->projects as $project) {
                        $project->delete();
                    }
                }
                if ($childScenario->types) {
                    foreach ($childScenario->types as $type) {
                        $childScenario->types()->detach($type->id);
                    }
                }
                $childScenario->forceDelete();
            }

            Log::error('Error inside overrideScenario method');
            Log::error($e->getMessage());
            throw $e;
        }
    }

    private function convertOverrideDataToRequestObject(ScenarioOverrideData $overrideData): array
    {
        // TODO: Future Phase
        $projectsLock = [];

        return collect([
            'projects_remove' => $overrideData->projects_remove,
            'wells_remove' => $overrideData->wells_remove ?? [],
            'projects_lock' => $projectsLock,
            'wells_lock' => [],
            'wells_reassign_from' => $overrideData->wells_reassign_from ?? [],
            'wells_reassign_to' => $overrideData->wells_reassign_to ?? [],
        ])->toArray();
    }

    public function getAvailableFactors(GeneralSpecifications $scenarioData)
    {
        try {
            $this->primoApiService->verifyConnection();

            return $this->primoApiService->getAvailableFactors($scenarioData);
        } catch (\Exception $e) {
            throw $e;
        }
    }
}
