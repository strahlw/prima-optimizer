<?php

namespace App\Console\Commands\Migrations;

use App\Models\Well;
use Illuminate\Console\Command;
use Illuminate\Support\Facades\DB;

class CleanupDeprecatedMongoDBFields extends Command
{
    /**
     * The name and signature of the console command.
     *
     * @var string
     */
    protected $signature = 'migrations:cleanup-deprecated-mongo-db-fields';

    /**
     * The console command description.
     *
     * @var string
     */
    protected $description = 'Remove all unused models and fields from the MongoDB database post-migration to MySQL.';

    /**
     * Execute the console command.
     */
    public function handle(): void
    {
        try {
            $this->info('Removing unused MongoDB models and fields...');

            $this->line('Dropping projects collection...');
            DB::connection('mongodb')->dropCollection('projects');

            $this->line('Deleting json object, scenario_id, and project_id from wells collection...');
            Well::query()->update([
                '$unset' => [
                    'json' => 1,
                    'scenario_id' => 1,
                    'project_id' => 1,
                ],
            ]);

            $this->info('MongoDB cleanup complete!');
        } catch (\Exception $e) {
            $this->error($e->getMessage());
        }
    }
}
