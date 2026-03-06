<?php

use App\Models\DatasetImportColumn;
use Illuminate\Database\Migrations\Migration;
use Illuminate\Support\Facades\Artisan;

return new class extends Migration
{
    /**
     * Run the migrations.
     */
    public function up(): void
    {
        DatasetImportColumn::truncate();
        Artisan::call('db:seed', ['--class' => 'DatasetImportColumnPhase3Seeder']);
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        DatasetImportColumn::truncate();

        Artisan::call('db:seed', ['--class' => 'DatasetImportColumnPhase2Seeder']);
    }
};
