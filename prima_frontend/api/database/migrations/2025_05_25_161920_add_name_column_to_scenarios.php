<?php

use App\Models\Scenario;
use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    // Check for duplicate names in the scenarios table
    private $sqlCheck = "
            SELECT
            JSON_UNQUOTE(JSON_EXTRACT(data, '$.name')) AS name,
            organization_id,
            COUNT(*) AS duplicate_count
        FROM scenarios
        GROUP BY name, organization_id
        HAVING COUNT(*) > 1;
    ";

    /**
     * Run the migrations.
     */
    public function up(): void
    {
        $duplicates = DB::table('scenarios')
            ->selectRaw("JSON_UNQUOTE(JSON_EXTRACT(data, '$.name')) AS name, organization_id, COUNT(*) AS duplicate_count")
            ->groupBy('name', 'organization_id')
            ->havingRaw('COUNT(*) > 1')
            ->get();

        if ($duplicates->isNotEmpty()) {
            $message = "❌ Duplicate scenario names found by organization. Fix these before applying the unique constraint:\n";
            foreach ($duplicates as $row) {
                $message .= "- Org ID {$row->organization_id}, Name '{$row->name}', Count: {$row->duplicate_count}\n";
            }

            // Output to console and throw an exception to stop the migration
            echo $message;
            throw new \Exception('❌ Migration halted due to duplicate (name, organization_id) values.');
        }

        Schema::table('scenarios', function (Blueprint $table) {
            // Only nullable until backfilled
            $table->string('name')->nullable()->after('id');
        });

        /** It is  best practice to run the backfill as part of the migration.
         * It is added here due to all migrations being run as part of a deployment.
         * The subsequent migration will add the unique constraint and backfill must occur before that.
         **/
        Scenario::withTrashed()->whereNull('name')->chunkById(100, function ($scenarios) {
            foreach ($scenarios as $scenario) {
                $scenario->name = $scenario->data['name'] ?? null;
                $scenario->save();
            }
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::table('scenarios', function (Blueprint $table) {
            $table->dropColumn('name');
        });
    }
};
