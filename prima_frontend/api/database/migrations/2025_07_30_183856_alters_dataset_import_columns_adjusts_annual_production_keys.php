<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Support\Facades\DB;

return new class extends Migration
{
    /**
     * Run the migrations.
     */
    public function up(): void
    {
        DB::table('dataset_import_columns')->where('key', 'annual_gas_production')->update(['key' => 'ann_gas_production']);
        DB::table('dataset_import_columns')->where('key', 'annual_oil_production')->update(['key' => 'ann_oil_production']);
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        DB::table('dataset_import_columns')->where('key', 'ann_gas_production')->update(['key' => 'annual_gas_production']);
        DB::table('dataset_import_columns')->where('key', 'ann_oil_production')->update(['key' => 'annual_oil_production']);
    }
};
