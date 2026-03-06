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
        Schema::table('scenarios', function (Blueprint $table) {
            $table->unsignedBigInteger('parent_id')->nullable()->after('data');
            $table->foreign('parent_id')->references('id')->on('scenarios');
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::table('scenarios', function (Blueprint $table) {
            $table->dropForeign(['parent_id']);
        });
    }
};
