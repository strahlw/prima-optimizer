<?php

namespace App\Console\Commands;

use App\Models\Project;
use App\Models\ProjectWell;
use App\Models\Scenario;
use App\Models\Well;
use Carbon\Carbon;
use Illuminate\Console\Command;

class DeleteOldScenarios extends Command
{
    /**
     * The name and signature of the console command.
     *
     * @var string
     */
    protected $signature = 'scenarios:delete-old-scenarios';

    /**
     * The console command description.
     *
     * @var string
     */
    protected $description = 'Delete scenarios where the deleted_at column value is equal to or over 2 weeks prior';

    /**
     * Execute the console command.
     */
    public function handle(): void
    {
        $twoWeeksAgo = Carbon::now()->subWeeks(2);

        try {
            $oldScenarios = Scenario::onlyTrashed()
                ->where('deleted_at', '<=', $twoWeeksAgo)
                ->get();
            foreach ($oldScenarios as $scenario) {
                $scenario->projects()->each(function (Project $project) {
                    $project->getWells()->each(function (Well $well) {
                        $well->delete();
                    });
                    ProjectWell::where('project_id', $project->id)->forceDelete();
                    $project->delete();
                });

                $scenario->forceDelete();
            }
            $this->info('Deleted scenarios and related projects older than 2 weeks have been removed from the database');
        } catch (\Exception $e) {
            $this->error($e->getMessage());
        }
    }
}
