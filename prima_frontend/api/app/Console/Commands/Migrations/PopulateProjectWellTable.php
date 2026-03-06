<?php

namespace App\Console\Commands\Migrations;

use App\Models\Project;
use Illuminate\Console\Command;
use Illuminate\Support\Facades\DB;

class PopulateProjectWellTable extends Command
{
    /**
     * The name and signature of the console command.
     *
     * @var string
     */
    protected $signature = 'migrations:populate-project-well-table {--dryrun}';

    protected bool $dryrun;

    /**
     * The console command description.
     *
     * @var string
     */
    protected $description = 'For each project, use the object id of that Project to gather Wells from the mongo DB, and populate the pivot table in MySQL';

    /**
     * Execute the console command.
     */
    public function handle(): void
    {
        $this->dryrun = $this->option('dryrun');

        DB::beginTransaction();

        try {
            // To aid filtering, get all dataset ids that are in use
            $this->info('Populating project_well pivot table...');
            Project::all()->each(function ($project) use (&$populatedWellIDs) {
                $projectWells = DB::connection('mongodb')->table('wells')->where('json.project_id', $project->object_id)->get();

                $projectWells->each(function ($well) use ($project) {
                    DB::table('project_well')->insert([
                        'project_id' => $project->id,
                        'well_id' => (string) $well->id,
                    ]);
                });
            });

            $this->info('Project_well pivot table populated successfully.');

            if ($this->dryrun) {
                DB::rollBack();
            } else {
                DB::commit();
            }
        } catch (\Exception $e) {
            $this->error($e->getMessage());
            DB::rollBack();
        }
    }
}
