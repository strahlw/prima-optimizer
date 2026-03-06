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
        Schema::create('projects', function (Blueprint $table) {
            $table->id();
            $table->unsignedBigInteger('scenario_id');
            $table->float('impact_score');
            $table->float('efficiency_score');
            $table->unsignedBigInteger('parent_project_id')->nullable();
            $table->timestamps();
            $table->string('object_id')->nullable(); // Old object id field from the original mongoDB setup.

            $table->foreign('scenario_id')->references('id')->on('scenarios');
            $table->foreign('parent_project_id')->references('id')->on('projects');
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        // Drop foreign
        Schema::table('projects', function (Blueprint $table) {
            $table->dropForeign(['scenario_id']);
            $table->dropForeign(['parent_project_id']);
        });

        Schema::dropIfExists('projects');
    }
};
