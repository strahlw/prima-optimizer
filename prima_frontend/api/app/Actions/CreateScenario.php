<?php

namespace App\Actions;

use App\Enum\ScenarioStatus;
use App\Enum\TaskStatus;
use App\Models\Scenario;
use App\Models\Task;
use App\Models\User;
use App\Services\PrimoApiService;
use App\Types\RecommendationOnlyScenarioData;
use App\Types\ScenarioData;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Log;

class CreateScenario
{
    public function __construct(public PrimoApiService $primoApiService) {}

    /**
     * Create a new scenario. Send the scenario to the Primo API and create a task.
     *
     * @param  ScenarioData|RecommendationOnlyScenarioData  $scenarioData  The data for the scenario.
     * @param  User  $user  The user creating the scenario.
     * @param  int  $organizationId  The ID of the organization.
     * @return Scenario The created scenario.
     */
    public function execute(
        ScenarioData|RecommendationOnlyScenarioData $scenarioData,
        User $user,
        int $organizationId,
        array $types,
        ?int $copyParentId
    ): Scenario {
        DB::beginTransaction();

        try {
            $this->primoApiService->verifyConnection();

            $scenario = Scenario::create([
                'name' => $scenarioData->general_specifications->name,
                'user_id' => $user->id,
                'organization_id' => $organizationId,
                'status' => ScenarioStatus::PROCESSING,
                'data' => (array) $scenarioData,
                'dataset_id' => $scenarioData->general_specifications->dataset_id,
                'status_by_id' => $user->id,
                'copy_parent_id' => $copyParentId,
            ]);

            $scenario->addTypePivotEntries($types);

            $response = $this->primoApiService->runOptimization($scenarioData, $scenario->id);

            if ($response->status === TaskStatus::PENDING || $response->status === TaskStatus::PROCESSING) {
                Task::create([
                    'task_id' => $response->taskId,
                    'status' => $response->status,
                    'scenario_id' => $scenario->id,
                    'status_by_id' => $user->id,
                ]);

                DB::commit();

                return $scenario;
            }

            // If the Scenario fails the submission to the Primo API:
            $scenario->update(['status' => ScenarioStatus::FAILURE]);
            Log::error("Scenario submission failed: {$response->msg}");

            DB::commit();
            throw new \Exception("Scenario submission failed: {$response->msg}");
        } catch (\Exception $e) {
            DB::rollBack();
            throw $e;
        }
    }
}
