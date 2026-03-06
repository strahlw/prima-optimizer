<?php

namespace App\Actions;

use App\Enum\ScenarioStatus;
use App\Enum\ScenarioType;
use App\Models\Scenario;
use App\Models\User;
use App\Types\RankOnlyScenarioData;
use Illuminate\Support\Facades\DB;

class CreateRankOnlyScenario
{
    /**
     * Create a new rank-only scenario.
     *
     * @param  \App\Types\RankOnlyScenarioData  $data
     */
    public function execute(
        RankOnlyScenarioData $scenarioData,
        User $user,
        int $organizationId,
        ?int $copyParentId
    ): Scenario {
        try {
            $scenario = Scenario::create([
                'name' => $scenarioData->general_specifications->name,
                'user_id' => $user->id,
                'organization_id' => $organizationId,
                'status' => ScenarioStatus::PUBLISHED,
                'data' => (array) $scenarioData,
                'dataset_id' => $scenarioData->general_specifications->dataset_id,
                'status_by_id' => $user->id,
                'copy_parent_id' => $copyParentId,
            ]);

            $scenario->addTypePivotEntries([ScenarioType::WELL_RANKING]);

            return $scenario;
        } catch (\Exception $e) {
            DB::rollBack();
            throw $e;
        }
    }
}
