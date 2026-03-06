<?php

use App\Enum\ScenarioType as EnumScenarioType;
use App\Models\ScenarioType;
use Illuminate\Database\Migrations\Migration;

return new class extends Migration
{
    /**
     * Run the migrations.
     */
    public function up(): void
    {
        $oldType = ScenarioType::where('name', 'MCW Ranking')->first();
        if ($oldType) {
            $oldType->update(['name' => EnumScenarioType::WELL_RANKING]);
        }
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        $oldType = ScenarioType::where('name', EnumScenarioType::WELL_RANKING)->first();
        if ($oldType) {
            $oldType->update(['name' => 'MCW Ranking']);
        }
    }
};
