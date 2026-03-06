<?php

use App\Enum\ScenarioType as EnumScenarioType;
use App\Models\Scenario;
use App\Models\ScenarioType;
use Illuminate\Database\Migrations\Migration;
use Illuminate\Support\Facades\DB;

return new class extends Migration
{
    /**
     * Run the migrations.
     */
    public function up(): void
    {
        $projectRecommendationsTypeId = ScenarioType::getIdByType(EnumScenarioType::PROJECT_RECOMMENDATIONS);
        $wellRankingTypeId = ScenarioType::getIdByType(EnumScenarioType::WELL_RANKING);

        if (! $wellRankingTypeId) {
            // Handle old type
            $oldRankingName = ScenarioType::where('name', 'MCW Ranking')->first();
            if ($oldRankingName) {
                $oldRankingName->update(['name' => EnumScenarioType::WELL_RANKING]);
                $wellRankingTypeId = $oldRankingName->id;
            }
        }

        // This assumes that at the time of migration, Project Comparisons is not a valid feature.
        Scenario::all()->each(function (Scenario $scenario) use ($projectRecommendationsTypeId, $wellRankingTypeId) {
            DB::table('scenario_scenario_type')->insert([
                'scenario_id' => $scenario->id,
                'scenario_type_id' => $wellRankingTypeId,
            ]);

            if (! array_key_exists('efficiency_factors', $scenario->data)) {
                return;
            }

            DB::table('scenario_scenario_type')->insert([
                'scenario_id' => $scenario->id,
                'scenario_type_id' => $projectRecommendationsTypeId,
            ]);
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        DB::statement('SET FOREIGN_KEY_CHECKS=0;');
        DB::table('scenario_scenario_type')->truncate();
        DB::statement('SET FOREIGN_KEY_CHECKS=1;');
    }
};
