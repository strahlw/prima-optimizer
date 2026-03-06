<?php

use App\Enum\ScenarioType as ScenarioTypeEnum;
use App\Models\ScenarioType;
use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    /**
     * Run the migrations.
     */
    public function up(): void
    {
        Schema::create('scenario_types', function (Blueprint $table) {
            $table->id();
            $table->string('name')->unique();
            $table->timestamps();
        });

        // Seed initial scenario types
        ScenarioType::create([
            'name' => ScenarioTypeEnum::PROJECT_RECOMMENDATIONS,
        ]);
        ScenarioType::create([
            'name' => ScenarioTypeEnum::PROJECT_COMPARISONS,
        ]);
        ScenarioType::create([
            'name' => ScenarioTypeEnum::WELL_RANKING,
        ]);
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('scenario_types');
    }
};
