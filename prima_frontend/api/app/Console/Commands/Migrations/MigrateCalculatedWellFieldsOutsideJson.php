<?php

namespace App\Console\Commands\Migrations;

use App\Models\Well;
use Illuminate\Console\Command;

class MigrateCalculatedWellFieldsOutsideJson extends Command
{
    /**
     * The name and signature of the console command.
     *
     * @var string
     */
    protected $signature = 'migrations:migrate-calculated-well-fields-outside-json';

    /**
     * The console command description.
     *
     * @var string
     */
    protected $description = 'Move the calculated fields formerly stored in the json objects of the wells entries to the root level of the wells table.';

    /**
     * Execute the console command.
     */
    public function handle(): void
    {
        try {
            $wells = Well::all();

            $this->info("Found {$wells->count()} well records to process...");
            $bar = $this->output->createProgressBar($wells->count());
            $bar->start();

            $wells->each(function (Well $well) use (&$bar) {
                $priorityScore = array_key_exists('well_priority_score', $well->json) ?
                                    $well->json['well_priority_score'] : (array_key_exists('priority_score', $well->json) ? $well->json['priority_score'] : null);

                $well->update([
                    'well_id' => $well->json['well_id'],
                    'priority_score' => $priorityScore,
                    'well_rank' => $well->json['well_rank'] ?? null,
                ]);

                $bar->advance();
            });

            $bar->finish();

            $this->info('Well records updated successfully!');
        } catch (\Exception $e) {
            $this->error($e->getMessage());
        }
    }
}
