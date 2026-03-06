<?php

namespace App\Console\Commands\Migrations;

use App\Models\Project;
use App\Models\Scenario;
use Illuminate\Console\Command;
use Illuminate\Support\Facades\DB;

class MigrateMongoDBProjects extends Command
{
    /**
     * The name and signature of the console command.
     *
     * @var string
     */
    protected $signature = 'migrations:migrate-mongodb-projects {--dryrun}';

    protected bool $dryrun;

    /**
     * The console command description.
     *
     * @var string
     */
    protected $description = 'A onetime command to migrate projects (with valid scenarios) from MongoDB to MySQL';

    /**
     * Execute the console command.
     */
    public function handle(): void
    {
        $this->dryrun = $this->option('dryrun');

        DB::beginTransaction();

        try {
            $mongoProjects = DB::connection('mongodb')->table('projects')->get();
            $this->info("Found {$mongoProjects->count()} projects in MongoDB");

            $this->info('Migrating projects to MySQL...');
            $bar = $this->output->createProgressBar($mongoProjects->count());
            $bar->start();

            $processedProjects = collect();
            $projectsWithParents = collect();
            $mongoProjects->each(function ($project) use (&$bar, &$processedProjects, &$projectsWithParents) {
                if (Scenario::where('id', $project->scenario_id)->exists()) {
                    $newProject = Project::create([
                        'scenario_id' => $project->scenario_id,
                        'impact_score' => $project->impact_score,
                        'efficiency_score' => $project->efficiency_score,
                        'object_id' => $project->id,
                    ]);

                    if (property_exists($project, 'parent_project_id')) {
                        $projectsWithParents->push([
                            'project_id' => $newProject->id,
                            'parent_project_id' => $project->parent_project_id,
                        ]);
                    } else {
                        $processedProjects->push($newProject);
                    }
                }
                $bar->advance();
            });

            $bar->finish();

            if ($projectsWithParents->isNotEmpty()) {
                $this->line('');
                $this->info("\nFound {$projectsWithParents->count()} projects with parents, adding parent ids...");
                $projectsWithParents->each(function ($project) use (&$processedProjects) {
                    $parentProject = Project::where('object_id', $project->parent_project_id)->first();
                    if ($parentProject) {
                        $childProject = Project::find($project->project_id);
                        $childProject->update(['parent_project_id' => $parentProject->id]);
                        $processedProjects->push($childProject);
                    }
                });
            }

            $this->info("\nMigrated {$processedProjects->count()} projects to MySQL");
            $this->table(['ID', 'Scenario ID', 'Impact Score', 'Efficiency Score', 'Object ID', 'Parent Project ID'], $processedProjects->map(function ($project) {
                return [
                    $project->id,
                    $project->scenario_id,
                    $project->impact_score,
                    $project->efficiency_score,
                    $project->object_id,
                    $project->parent_project_id,
                ];
            }));

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
