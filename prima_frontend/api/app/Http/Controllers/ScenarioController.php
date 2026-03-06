<?php

namespace App\Http\Controllers;

use App\Actions\CreateRankOnlyScenario;
use App\Actions\CreateScenario;
use App\Actions\RankExistingScenario;
use App\Enum\ScenarioStatus;
use App\Enum\ScenarioType;
use App\Exceptions\OverrideScenarioValidationException;
use App\Http\Requests\CreateGeneralSpecificationsRequest;
use App\Http\Requests\CreateScenarioRequest;
use App\Http\Requests\OverrideScenarioRequest;
use App\Http\Requests\SearchAvailableWellsRequest;
use App\Http\Requests\UpdateScenarioNameRequest;
use App\Jobs\PollTask;
use App\Models\Project;
use App\Models\Ranking;
use App\Models\Scenario;
use App\Repositories\ProjectRepository;
use App\Repositories\RankingRepository;
use App\Repositories\ScenarioRepository;
use App\Types\EfficiencyFactors;
use App\Types\GeneralSpecifications;
use App\Types\ImpactFactors;
use App\Types\RankOnlyScenarioData;
use App\Types\RecommendationOnlyScenarioData;
use App\Types\ScenarioData;
use App\Types\UseCases;
use Exception;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Log;
use Illuminate\Support\Str;

class ScenarioController extends Controller
{
    public function __construct(protected ScenarioRepository $scenarioRepository) {}

    /**
     * Display a listing of the resource.
     */
    public function index(Request $request)
    {
        $user = $request->user();

        try {
            if ($user->hasRole('super-admin')) {
                $scenarios = Scenario::with(['user', 'dataset', 'types'])->get();

                return response()->json($scenarios);
            } elseif ($user->hasRole('org-admin')) {
                $scenarios = Scenario::where('organization_id', $user->organization_id)->with(['user', 'dataset', 'types'])->get();

                return response()->json($scenarios);
            }
            $scenarios = $user->scenarios()->with(['user', 'dataset', 'types'])->get();

            return response()->json($scenarios);
        } catch (Exception $e) {
            Log::error($e->getMessage());

            return response()->json(['message' => 'An error occurred while fetching the users scenarios'], 500);
        }

    }

    /**
     * Store a newly created resource in storage.
     */
    public function store(CreateScenarioRequest $request)
    {
        try {
            $validated = $request->validated();
            $useCases = $validated['use_cases']['cases'] ?? [];

            if (count($useCases) === 1 && in_array(ScenarioType::PROJECT_RECOMMENDATIONS, $useCases)) {
                $scenarioData = new RecommendationOnlyScenarioData(
                    new GeneralSpecifications(...$validated['general_specifications']),
                    new EfficiencyFactors(...$validated['efficiency_factors']),
                    new UseCases(...$validated['use_cases'])
                );
            } else {
                $scenarioData = new ScenarioData(
                    new GeneralSpecifications(...$validated['general_specifications']),
                    new ImpactFactors(...$validated['impact_factors']),
                    new EfficiencyFactors(...$validated['efficiency_factors']),
                    new UseCases(...$validated['use_cases'])
                );
            }

            $scenario = app()->make(CreateScenario::class)->execute(
                $scenarioData,
                $request->user(),
                $validated['general_specifications']['organization_id'],
                $useCases,
                $validated['copy_parent_id'] ?? null
            );

            PollTask::dispatch($scenario->task);

            return response()->json($scenario, 201);
        } catch (Exception $e) {
            Log::error('Error creating scenario: '.$e->getMessage());
            Log::error($e->getTraceAsString());

            return response()->json(['message' => $e->getMessage()], 500);
        }
    }

    public function storeRankOnly(CreateScenarioRequest $request)
    {
        try {
            $validated = $request->validated();

            $scenarioData = new RankOnlyScenarioData(
                new GeneralSpecifications(...$validated['general_specifications']),
                new ImpactFactors(...$validated['impact_factors']),
                new UseCases(...$validated['use_cases'])
            );

            $scenario = app()->make(CreateRankOnlyScenario::class)->execute(
                $scenarioData,
                $request->user(),
                $validated['general_specifications']['organization_id'],
                $validated['copy_parent_id'] ?? null
            );

            return response()->json($scenario, 201);
        } catch (Exception $e) {
            Log::error('Error creating rank-only scenario: '.$e->getMessage());
            Log::error($e->getTraceAsString());

            return response()->json(['message' => $e->getMessage()], 500);
        }
    }

    public function rank(CreateScenarioRequest $request)
    {
        try {
            $validated = $request->validated();

            $scenarioData = new ScenarioData(new GeneralSpecifications(...$validated['general_specifications']), new ImpactFactors(...$validated['impact_factors']), new EfficiencyFactors(...$validated['efficiency_factors']), new UseCases(...$validated['use_cases']));

            $taskId = $this->scenarioRepository->createRanking($scenarioData, $request->user(), $validated['general_specifications']['organization_id'] || $validated['general_specifications']['organization_id']);

            return response()->json(['taskId' => $taskId], 201);
        } catch (Exception $e) {
            Log::error('Error creating scenario: '.$e->getMessage());
            Log::error($e->getTraceAsString());

            return response()->json(['message' => $e->getMessage()], 500);
        }
    }

    /**
     * Display the specified resource.
     */
    public function show(string $id) {}

    public function publish(Scenario $scenario, Request $request)
    {
        try {
            if ($request->user()->cannot('update', $scenario)) {
                return response()->json(['message' => 'Unauthorized to publish this scenario'], 403);
            }

            $scenario->update(['status' => ScenarioStatus::PUBLISHED]);

            return response()->json(['message' => 'Success']);

        } catch (\Exception $e) {
            return response()->json(['message' => $e->getMessage()], 500);
        }

    }

    /**
     * Remove the specified resource from storage.
     */
    public function destroy(Request $request, Scenario $scenario)
    {
        try {
            if ($request->user()->cannot('update', $scenario)) {
                return response()->json(['message' => 'Unauthorized to delete this scenario'], 403);
            }

            $scenario->delete();

            return response()->json(['message' => 'Success']);
        } catch (\Exception $e) {
            return response()->json(['message' => $e->getMessage()], 500);
        }
    }

    public function getPublishedScenarios(Request $request)
    {
        try {
            $perPage = $request->input('per_page', 10);
            $page = $request->input('page', 1);
            $organizationId = $request->input('organization_id');
            $filters = $request->array('filters');
            $scenarioId = (int) $request->input('scenario_id');
            $scenarios = $this->scenarioRepository->getScenariosByUserRole($request->user(), $perPage, $page, $organizationId, $filters, $scenarioId);

            return response()->json($scenarios, 200);
        } catch (\Exception $e) {
            Log::error('Error fetching published scenarios: '.$e->getMessage());

            return response()->json(['message' => $e->getMessage()], 500);
        }
    }

    public function kill(Request $request, Scenario $scenario)
    {
        try {
            if ($request->user()->cannot('update', $scenario)) {
                return response()->json(['message' => 'Unauthorized to kill this scenario optimization'], 403);
            }

            $this->scenarioRepository->killOptimization($scenario, $request->user());

            return response()->json(['message' => 'Success']);
        } catch (\Exception $e) {
            Log::error($e);

            return response()->json(['message' => $e->getMessage()], 500);
        }
    }

    public function getProjects(Request $request, Scenario $scenario)
    {
        try {
            return response()->json($this->scenarioRepository->getFormattedProjectsAndScores($scenario->load('parent'), $request->query('mapOnly')), 200);
        } catch (\Exception $e) {
            Log::error("Error fetching projects for scenario: {$scenario->id}".$e->getMessage());

            return response()->json(['message' => $e->getMessage()], 500);
        }
    }

    public function getProjectWells(Request $request, string $projectId, ProjectRepository $repository)
    {
        try {
            $project = Project::find($projectId);

            if (! $project) {
                return response()->json(['message' => 'Project not found'], 404);
            }

            $perPage = $request->query('rows', 10);
            $page = $request->query('page', 1);
            $sortOrder = $request->query('sortOrder') === '-1' ? 'desc' : 'asc';
            $sortField = $request->query('sortField');

            if ($sortField) {
                $sortField = Str::snake($sortField);
            }

            // A string well_id will fail for mongoDB where clauses
            $addedDatasetWellIds = array_map('intval', $request->query('addedDatasetWellIds', []));
            $addedWellIds = $request->query('addedWellIds');

            $paginatedData = $repository->searchWellsAndDatasets(
                $project,
                $perPage,
                $page,
                $sortOrder,
                $sortField,
                $addedDatasetWellIds,
                $addedWellIds
            );

            return response()->json($paginatedData);
        } catch (\Exception $e) {
            Log::error($e);

            return response()->json(['message' => 'Error fetching project wells'], 500);
        }
    }

    public function searchAvailableWells(SearchAvailableWellsRequest $request, Scenario $scenario, ScenarioRepository $repository)
    {
        $query = $request->input('query');
        $includedWellIds = $request->input('included_well_ids', []); // Wells that were part of a project but have been added to the pool
        $inactiveProjectIds = $request->input('inactive_project_ids', []);
        $excludedDatasetWellIds = $request->input('excluded_dataset_well_ids', []);
        $reassignedWellIds = $request->input('reassigned_well_ids', []);
        $wellTypes = $request->input('well_types', []);

        try {
            return response()->json($repository->searchAvailableWellIds($query, $scenario, $includedWellIds, $inactiveProjectIds, $excludedDatasetWellIds, $reassignedWellIds, $wellTypes));
        } catch (\Exception $e) {
            Log::error($e);

            return response()->json(['message' => 'Error searching available wells'], 500);
        }
    }

    public function override(OverrideScenarioRequest $request, Scenario $scenario, ScenarioRepository $repository)
    {
        try {
            $overrideData = $request->convertToOverrideData();

            return response()->json(['scenario_id' => $repository->overrideScenario($overrideData, $scenario, $request->user())]);
        } catch (\Exception $e) {
            Log::error($e);

            if ($e instanceof OverrideScenarioValidationException) {
                return response()->json(['message' => $e->getMessage()], 422);
            } else {
                return response()->json(['message' => 'An error occurred while overriding the scenario'], 500);
            }
        }
    }

    public function getRankingData(Request $request, string $taskId, RankingRepository $repository)
    {
        try {
            $perPage = (int) $request->query('rows', 20);
            $page = $request->query('page');
            $sortOrder = $request->query('sortOrder', 'asc');
            $sortField = $request->query('sortField', 'well_id');
            $wellTypes = $request->query('wellType', []);

            $paginatedData = $repository->getRankingData(
                $taskId,
                $perPage,
                $page,
                $sortField,
                $sortOrder,
                $wellTypes,
            );

            return response()->json($paginatedData);
        } catch (\Exception $e) {
            Log::error($e);

            return response()->json(['message' => 'Error fetching project wells'], 500);
        }
    }

    public function deleteRankingData(string $taskId)
    {
        try {
            $deletedRows = Ranking::where('task_id', $taskId)->delete();
            if ($deletedRows > 0) {
                return response()->json(['message' => 'Ranking data deleted successfully'], 200);
            } else {
                return response()->json(['message' => 'No ranking data found for the given task ID'], 404);
            }
        } catch (\Exception $e) {
            return response()->json(['message' => 'An error occurred while deleting the ranking data'], 500);
        }
    }

    public function getInitialVisibleWells(Request $request, ProjectRepository $repository)
    {
        try {
            // Setup default loading params
            $result = [];
            $perPage = 20;
            $page = 1;
            $sortOrder = 'asc';
            $sortField = 'well_rank';
            $first = 0;

            // For each project map the paginated data in scenarioId => [$projects] format
            collect($request->all())->each(function ($projectIds, $scenarioId) use ($repository, $perPage, $page, $sortOrder, $sortField, $first, &$result) {
                collect($projectIds)->each(function ($projectId) use ($repository, $perPage, $page, $sortOrder, $sortField, $first, $scenarioId, &$result) {
                    $paginatedData = $repository->searchWellsAndDatasets(Project::find($projectId), $perPage, $page, $sortOrder, $sortField, [], [], $first);
                    $result[$scenarioId][$projectId] = $paginatedData;
                });
            });

            return response()->json($result);
        } catch (\Exception $e) {
            Log::error($e);

            return response()->json(['message' => 'Error fetching initial visible wells'], 500);
        }
    }

    public function rankExistingScenario(Request $request, Scenario $scenario)
    {
        try {
            $taskId = app()->make(RankExistingScenario::class)->execute($scenario);

            return response()->json(['taskId' => $taskId], 201);
        } catch (Exception $e) {
            Log::error('Error ranking existings scenario: '.$e->getMessage());
            Log::error($e->getTraceAsString());

            return response()->json(['message' => $e->getMessage()], 500);
        }
    }

    public function updateName(UpdateScenarioNameRequest $request, Scenario $scenario)
    {
        try {
            if ($request->user()->cannot('update', $scenario)) {
                return response()->json(['message' => 'Unauthorized to update this scenario'], 403);
            }

            $validated = $request->validated();
            $name = $validated['name'];

            $data = $scenario->data;
            $data['name'] = $name;
            $data['general_specifications']['name'] = $name;
            $scenario->data = $data;
            $scenario->name = $name;
            $scenario->save();

            return response()->json($scenario, 200);
        } catch (Exception $e) {
            Log::error('Error updating scenario name: '.$e->getMessage());
            Log::error($e->getTraceAsString());

            return response()->json(['message' => $e->getMessage()], 500);
        }
    }

    public function getScenarioParams(Scenario $scenario)
    {
        try {
            return response()->json($scenario, 200);
        } catch (Exception $e) {
            Log::error('Error fetching scenario params: '.$e->getMessage());
            Log::error($e->getTraceAsString());

            return response()->json(['message' => 'An error occurred while fetching the scenario params'], 500);
        }
    }

    public function checkName(Request $request)
    {
        $request->validate([
            'name' => 'required|string',
            'organizationId' => 'required|integer',
        ]);

        $exists = Scenario::where('name', $request->name)
            ->where('organization_id', $request->organizationId)
            ->exists();

        return response()->json(['unique' => ! $exists]);
    }

    public function getAvailableFactors(CreateGeneralSpecificationsRequest $request)
    {
        try {
            $validated = $request->validated();
            $scenarioData = new GeneralSpecifications(...$validated['general_specifications']);

            $response = $this->scenarioRepository->getAvailableFactors($scenarioData);

            return response()->json($response, 200);
        } catch (Exception $e) {
            Log::error('Error getting available factors: '.$e->getMessage());
            Log::error($e->getTraceAsString());

            return response()->json(['message' => $e->getMessage()], 500);
        }
    }
}
