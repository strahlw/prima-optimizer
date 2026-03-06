<?php

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
        Schema::create('scenario_scenario_type', function (Blueprint $table) {
            $table->foreignId('scenario_id')->constrained()->onDelete('cascade');
            $table->foreignId('scenario_type_id')->constrained()->onDelete('cascade');
            $table->primary(['scenario_id', 'scenario_type_id']);
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('scenario_scenario_type');
    }
};
