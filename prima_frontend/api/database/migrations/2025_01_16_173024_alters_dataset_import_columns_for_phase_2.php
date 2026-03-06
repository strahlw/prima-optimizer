<?php

use App\Enum\DatasetImportColumnPriority;
use App\Models\DatasetImportColumn;
use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Artisan;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    /**
     * Run the migrations.
     */
    public function up(): void
    {
        Schema::table('dataset_import_columns', function (Blueprint $table) {
            $table->integer('order')->nullable()->after('key'); // Add a field for ordering headings on the export sheet
            $table->enum('priority', DatasetImportColumnPriority::values())->nullable()->after('required');
        });

        DatasetImportColumn::truncate();

        Artisan::call('db:seed', ['--class' => 'DatasetImportColumnPhase2Seeder']);
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::table('dataset_import_columns', function (Blueprint $table) {
            $table->dropColumn('order');
            $table->dropColumn('priority');
        });

        DatasetImportColumn::truncate();

        Artisan::call('db:seed', ['--class' => 'DatasetImportColumnSeederArchive']);
    }
};
