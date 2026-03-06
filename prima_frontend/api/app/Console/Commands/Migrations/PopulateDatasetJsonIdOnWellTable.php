<?php

namespace App\Console\Commands\Migrations;

use App\Models\DatasetJson;
use App\Models\Scenario;
use App\Models\Well;
use Illuminate\Console\Command;

class PopulateDatasetJsonIdOnWellTable extends Command
{
    /**
     * The name and signature of the console command.
     *
     * @var string
     */
    protected $signature = 'migrations:populate-dataset-json-id-on-well-table';

    /**
     * The console command description.
     *
     * @var string
     */
    protected $description = 'For each well record with a valid Scenario, populate the dataset_json_id field with the ObjectId string from the corresponding dataset jsons record';

    /**
     * Execute the console command.
     */
    public function handle(): void
    {
        try {
            $wells = Scenario::all()->flatMap(fn ($scenario) => $scenario->getWells());

            if ($wells->count() === 0) {
                $this->warn('No wells found that require dataset_json_id population');

                return;
            }

            $this->info("Found {$wells->count()} wells that require dataset_json_id population");
            $this->line('Processing wells...');
            $bar = $this->output->createProgressBar($wells->count());
            $bar->start();

            $adjustedWells = collect();

            Scenario::all()->each(function (Scenario $scenario) use (&$adjustedWells, &$bar) {
                $datasetId = $scenario->dataset_id;
                $scenario->getWells()->each(function (Well $well) use (&$adjustedWells, $datasetId, &$bar) {
                    $datasetJson = DatasetJson::where('dataset_id', $datasetId)->where('json.well_id', $well->json['well_id'])->first();
                    if ($datasetJson) {
                        $well->update(['dataset_json_id' => $datasetJson->id]);
                        $adjustedWells->push($well);
                    } else {
                        throw new \Exception("DatasetJson not found for well_id: {$well->json['well_id']}");
                    }

                    $bar->advance();
                });
            });

            $bar->finish();
            $this->info("\nProcessed {$adjustedWells->count()} wells");
            $this->table(['Well ID', 'Dataset JSON ID'], $adjustedWells->map(fn (Well $well) => [$well->json['well_id'], $well->dataset_json_id])->toArray());
        } catch (\Exception $e) {
            $this->error($e->getMessage());
        }
    }
}
