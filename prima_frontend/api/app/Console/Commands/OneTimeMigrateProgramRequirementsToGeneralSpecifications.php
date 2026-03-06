<?php

namespace App\Console\Commands;

use App\Models\Scenario;
use Illuminate\Console\Command;
use Illuminate\Support\Facades\DB;

class OneTimeMigrateProgramRequirementsToGeneralSpecifications extends Command
{
    /**
     * The name and signature of the console command.
     *
     * @var string
     */
    protected $signature = 'one-time:migrate-program-requirements-to-general-specifications';

    /**
     * The console command description.
     *
     * @var string
     */
    protected $description = 'Switch the program_requirements key to general_specifications in the Scenarios table';

    /**
     * Execute the console command.
     */
    public function handle(): void
    {
        DB::beginTransaction();
        $scenarios = Scenario::all();

        $this->info('Migrating fields from program_requirements to general_specifications..');
        $bar = $this->output->createProgressBar(count($scenarios));

        try {
            $scenarios->each(function ($scenario) use ($bar) {
                $jsonData = $scenario->data;
                if (isset($jsonData['program_requirements'])) {
                    $jsonData['general_specifications'] = $jsonData['program_requirements'];
                    unset($jsonData['program_requirements']);
                    $scenario->data = $jsonData;
                    $scenario->save();
                }
                $bar->advance();
            });
            DB::rollBack();
        } catch (\Exception $e) {
            $this->error('An error occurred while migrating program requirements to general specifications');
            $this->error($e->getMessage());
            DB::rollBack();

            return;
        }
    }
}
