<?php

use App\Models\DatasetImportColumn;
use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    /**
     * Run the migrations.
     */
    public function up(): void
    {
        Schema::table('dataset_import_columns', function (Blueprint $table) {
            DatasetImportColumn::create([
                'label' => 'Priority Scores User Input',
                'key' => 'priority_scores_user_input',
                'order' => 53,
                'priority' => 'Optional',
                'rules' => [],
                'validation_messages' => [],
            ]);
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::table('dataset_import_columns', function (Blueprint $table) {
            DB::table('dataset_import_columns')->where('key', 'priority_scores_user_input')->delete();
        });
    }
};
