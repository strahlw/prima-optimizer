<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::table('scenarios', function (Blueprint $table) {
            $table->string('name')->change();
            $table->unique(['name', 'organization_id'], 'scenarios_name_org_unique');
        });
    }

    public function down(): void
    {
        Schema::table('scenarios', function (Blueprint $table) {
            $table->dropUnique('scenarios_name_org_unique');
            $table->string('name')->nullable()->change();
        });
    }
};
