<?php

namespace Database\Seeders;

use App\Enum\DatasetImportColumnPriority;
use App\Models\DatasetImportColumn;
use Illuminate\Database\Seeder;

class DatasetImportColumnPhase2Seeder extends Seeder
{
    protected function sanitizeLabel(string $label): string
    {
        // Convert to lowercase
        $label = strtolower($label);

        // Replace spaces and hyphens with underscores
        $label = str_replace([' ', '-'], '_', $label);

        // Remove asterisks
        $label = str_replace('*', '', $label);

        // Remove any text inside square brackets, including the brackets
        $label = preg_replace('/\[[^\]]*\]/', '', $label);

        // Trim any trailing underscores
        $label = rtrim($label, '_');

        return $label;
    }

    /**
     * Run the database seeds.
     */
    public function run(): void
    {
        $columns = collect([
            [
                'label' => 'Well ID',
                'rules' => ['numeric'],
                'order' => 1,
                'validation_messages' => ['Well ID - must be a number'],
                'required' => true,
                'priority' => DatasetImportColumnPriority::REQUIRED,
            ],
            [
                'label' => 'Latitude',
                'order' => 2,
                'rules' => ['numeric'],
                'validation_messages' => ['Latitude or X - must be a number'],
                'required' => false,
                'priority' => DatasetImportColumnPriority::REQUIRED,
            ],
            [
                'label' => 'Longitude',
                'order' => 3,
                'rules' => ['numeric'],
                'validation_messages' => ['Longitude or Y - must be a number'],
                'required' => false,
                'priority' => DatasetImportColumnPriority::REQUIRED,
            ],
            [
                'label' => 'Operator Name',
                'order' => 4,
                'rules' => ['string'],
                'validation_messages' => ['Operator Name - must be a string or empty'],
                'required' => false,
                'priority' => DatasetImportColumnPriority::RECOMMENDED,
            ],
            [
                'label' => 'Well Name',
                'key' => 'well_name',
                'order' => 5,
                'rules' => ['string'],
                'validation_messages' => ['Well Name - must be a string or empty'],
                'required' => false,
                'priority' => DatasetImportColumnPriority::RECOMMENDED,
            ],
            [
                'label' => 'Well Type [Oil, Gas, Combined]',
                'rules' => ['string', 'in:Oil,Gas,Combined'],
                'order' => 6,
                'validation_messages' => ['Well Type - must be a string and Oil, Gas, or Combined'],
                'required' => false,
                'priority' => DatasetImportColumnPriority::RECOMMENDED,
            ],
            [
                'label' => 'Methane Emissions [Ton/year]',
                'rules' => ['numeric'],
                'order' => 7,
                'validation_messages' => ['Methane Emissions - must be a number or empty'],
                'required' => false,
                'priority' => DatasetImportColumnPriority::RECOMMENDED,
            ],
            [
                'label' => 'Age [Years]',
                'rules' => ['numeric'],
                'order' => 8,
                'validation_messages' => ['Age - must be a number or empty'],
                'required' => false,
                'priority' => DatasetImportColumnPriority::RECOMMENDED,
            ],
            [
                'label' => 'Depth [ft]',
                'rules' => ['numeric'],
                'order' => 9,
                'validation_messages' => ['Depth - must be a number or empty'],
                'required' => false,
                'priority' => DatasetImportColumnPriority::RECOMMENDED,
            ],
            // Make these for Annual Oil Production andAnnual Gas Production
            [
                'label' => 'Annual Oil Production [bbl/Year]',
                'rules' => ['numeric'],
                'order' => 10,
                'validation_messages' => ['Annual Oil Production - must be a number or empty'],
                'required' => false,
                'priority' => DatasetImportColumnPriority::OPTIONAL,
            ],
            [
                'label' => 'Annual Gas Production [Mcf/Year]',
                'rules' => ['numeric'],
                'order' => 11,
                'validation_messages' => ['Annual Gas Production - must be a number or empty'],
                'required' => false,
                'priority' => DatasetImportColumnPriority::OPTIONAL,
            ],
            [
                'label' => '5-Year Oil Production [bbl]',
                'rules' => ['numeric'],
                'order' => 12,
                'validation_messages' => ['5-Year Oil Production - must be a number or empty'],
                'required' => false,
                'priority' => DatasetImportColumnPriority::OPTIONAL,
            ],
            [
                'label' => '5-Year Gas Production [Mcf]',
                'rules' => ['numeric'],
                'order' => 13,
                'validation_messages' => ['5-Year Gas Production - must be a number or empty'],
                'required' => false,
                'priority' => DatasetImportColumnPriority::OPTIONAL,
            ],
            [
                'label' => 'Lifelong Oil Production [bbl]',
                'rules' => ['numeric'],
                'order' => 14,
                'validation_messages' => ['Lifelong Oil Production - must be a number or empty'],
                'required' => false,
                'priority' => DatasetImportColumnPriority::OPTIONAL,
            ],
            [
                'label' => 'Lifelong Gas Production [Mcf]',
                'rules' => ['numeric'],
                'order' => 15,
                'validation_messages' => ['Lifelong Gas Production - must be a number or empty'],
                'required' => false,
                'priority' => DatasetImportColumnPriority::OPTIONAL,
            ],
            [
                'label' => 'Leak [Yes/No]',
                'rules' => ['boolean'],
                'order' => 16,
                'validation_messages' => ['Leak - must be Yes or No'],
                'required' => false,
                'priority' => DatasetImportColumnPriority::OPTIONAL,
            ],
            [
                'label' => 'Violation [Yes/No]',
                'rules' => ['boolean'],
                'order' => 17,
                'validation_messages' => ['Violation - must be Yes or No'],
                'required' => false,
                'priority' => DatasetImportColumnPriority::OPTIONAL,
            ],
            [
                'label' => 'Incident [Yes/No]',
                'rules' => ['boolean'],
                'order' => 18,
                'validation_messages' => ['Incident - must be Yes or No'],
                'required' => false,
                'priority' => DatasetImportColumnPriority::OPTIONAL,
            ],
            [
                'label' => 'Compliance [Yes/No]',
                'rules' => ['boolean'],
                'order' => 19,
                'validation_messages' => ['Compliance - must be Yes or No'],
                'required' => false,
                'priority' => DatasetImportColumnPriority::OPTIONAL,
            ],
            [
                'label' => 'H2s Leak [Yes/No]',
                'rules' => ['boolean'],
                'order' => 20,
                'validation_messages' => ['H2s Leak - must be Yes or No'],
                'required' => false,
                'priority' => DatasetImportColumnPriority::OPTIONAL,
            ],
            [
                'label' => 'State Wetlands (Near) [Yes/No]',
                'key' => 'state_wetlands_close_range',
                'rules' => ['boolean'],
                'order' => 21,
                'validation_messages' => ['State Wetlands (Near) - must be Yes or No'],
                'required' => false,
                'priority' => DatasetImportColumnPriority::OPTIONAL,
            ],
            [
                'label' => 'State Wetlands (Far) [Yes/No]',
                'key' => 'state_wetlands_wide_range',
                'rules' => ['boolean'],
                'order' => 22,
                'validation_messages' => ['State Wetlands (Far) - must be Yes or No'],
                'required' => false,
                'priority' => DatasetImportColumnPriority::OPTIONAL,
            ],
            [
                'label' => 'Federal Wetlands (Near) [Yes/No]',
                'key' => 'federal_wetlands_close_range',
                'rules' => ['boolean'],
                'order' => 23,
                'validation_messages' => ['Federal Wetlands (Near) - must be Yes or No'],
                'required' => false,
                'priority' => DatasetImportColumnPriority::OPTIONAL,
            ],
            [
                'label' => 'Federal Wetlands (Far) [Yes/No]',
                'key' => 'federal_wetlands_wide_range',
                'rules' => ['boolean'],
                'order' => 24,
                'validation_messages' => ['Federal Wetlands (Far) - must be Yes or No'],
                'required' => false,
                'priority' => DatasetImportColumnPriority::OPTIONAL,
            ],
            [
                'label' => 'Buildings (Near) [Yes/No]',
                'key' => 'buildings_close_range',
                'rules' => ['boolean'],
                'order' => 25,
                'validation_messages' => ['Buildings (Near) - must be Yes or No'],
                'required' => false,
                'priority' => DatasetImportColumnPriority::OPTIONAL,
            ],
            [
                'label' => 'Buildings (Far) [Yes/No]',
                'key' => 'buildings_wide_range',
                'rules' => ['boolean'],
                'order' => 26,
                'validation_messages' => ['Buildings (Far) - must be Yes or No'],
                'required' => false,
                'priority' => DatasetImportColumnPriority::OPTIONAL,
            ],
            [
                'label' => 'Number of Schools Near the Well (or if there are any 1=Yes 0=No)',
                'key' => 'num_of_schools_near_well',
                'rules' => ['numeric'],
                'order' => 27,
                'validation_messages' => ['Number of Schools Near the Well - must be a number or empty'],
                'required' => false,
                'priority' => DatasetImportColumnPriority::OPTIONAL,
            ],
            [
                'label' => 'Number of Hospitals Near the Well (or if there are any 1=Yes 0=No)',
                'key' => 'num_of_hospitals_near_well',
                'rules' => ['numeric'],
                'order' => 28,
                'validation_messages' => ['Number of Hospitals Near the Well - must be a number or empty'],
                'required' => false,
                'priority' => DatasetImportColumnPriority::OPTIONAL,
            ],
            [
                'label' => 'Disadvantaged Community Status [State-level] [Yes/No]',
                'rules' => ['boolean'],
                'order' => 29,
                'validation_messages' => ['Disadvantaged Community Status - must be Yes or No'],
                'required' => false,
                'priority' => DatasetImportColumnPriority::OPTIONAL,
            ],
            [
                'label' => 'Elevation Delta (Well-to-Road Access Point) [m]',
                'key' => 'elevation_delta',
                'rules' => ['numeric'],
                'order' => 30,
                'validation_messages' => ['Elevation Delta - must be a number or empty'],
                'required' => false,
                'priority' => DatasetImportColumnPriority::OPTIONAL,
            ],
            [
                'label' => 'Distance to Road [miles]',
                'rules' => ['numeric'],
                'order' => 31,
                'validation_messages' => ['Distance to Road - must be a number or empty'],
                'required' => false,
                'priority' => DatasetImportColumnPriority::OPTIONAL,
            ],
            [
                'label' => 'Water Source Nearby [Yes/No]',
                'rules' => ['boolean'],
                'order' => 32,
                'validation_messages' => ['Water Source Nearby - must be Yes or No'],
                'required' => false,
                'priority' => DatasetImportColumnPriority::OPTIONAL,
            ],
            [
                'label' => 'Known Soil or Water Impact [Yes/No]',
                'rules' => ['boolean'],
                'order' => 33,
                'validation_messages' => ['Known Soil or Water Impact - must be Yes or No'],
                'required' => false,
                'priority' => DatasetImportColumnPriority::OPTIONAL,
            ],
            [
                'label' => 'Population Density [#/km2]',
                'rules' => ['numeric'],
                'order' => 34,
                'validation_messages' => ['Population Density - must be a number or empty'],
                'required' => false,
                'priority' => DatasetImportColumnPriority::OPTIONAL,
            ],
            [
                'label' => 'State Code',
                'rules' => ['numeric'],
                'order' => 35,
                'validation_messages' => ['State Code - must be a number or empty'],
                'required' => false,
                'priority' => DatasetImportColumnPriority::OPTIONAL,
            ],
            [
                'label' => 'County Code',
                'rules' => ['numeric'],
                'order' => 36,
                'validation_messages' => ['County Code - must be a number or empty'],
                'required' => false,
                'priority' => DatasetImportColumnPriority::OPTIONAL,
            ],
            [
                'label' => 'Census Tract ID',
                'rules' => ['numeric'],
                'order' => 37,
                'validation_messages' => ['Census Tract ID - must be a number or empty'],
                'required' => false,
                'priority' => DatasetImportColumnPriority::OPTIONAL,
            ],
            [
                'label' => 'Placeholder 1',
                'rules' => [],
                'validation_messages' => [],
                'required' => false,
            ],
            [
                'label' => 'Placeholder 2',
                'rules' => [],
                'validation_messages' => [],
                'required' => false,
            ],
            [
                'label' => 'Placeholder 3',
                'rules' => [],
                'validation_messages' => [],
                'required' => false,
            ],
            [
                'label' => 'Placeholder 4',
                'rules' => [],
                'validation_messages' => [],
                'required' => false,
            ],
            [
                'label' => 'Placeholder 5',
                'rules' => [],
                'validation_messages' => [],
                'required' => false,
            ],
            [
                'label' => 'Placeholder 6',
                'rules' => [],
                'validation_messages' => [],
                'required' => false,
            ],
            [
                'label' => 'Placeholder 7',
                'rules' => [],
                'validation_messages' => [],
                'required' => false,
            ],
            [
                'label' => 'Placeholder 8',
                'rules' => [],
                'validation_messages' => [],
                'required' => false,
            ],
            [
                'label' => 'Placeholder 9',
                'rules' => [],
                'validation_messages' => [],
                'required' => false,
            ],
            [
                'label' => 'Placeholder 10',
                'rules' => [],
                'validation_messages' => [],
                'required' => false,
            ],
            [
                'label' => 'Placeholder 11',
                'rules' => [],
                'validation_messages' => [],
                'required' => false,
            ],
            [
                'label' => 'Placeholder 12',
                'rules' => [],
                'validation_messages' => [],
                'required' => false,
            ],
            [
                'label' => 'Placeholder 13',
                'rules' => [],
                'validation_messages' => [],
                'required' => false,
            ],
            [
                'label' => 'Placeholder 14',
                'rules' => [],
                'validation_messages' => [],
                'required' => false,
            ],
            [
                'label' => 'Placeholder 15',
                'rules' => [],
                'validation_messages' => [],
                'required' => false,
            ],
            [
                'label' => 'Placeholder 16',
                'rules' => [],
                'validation_messages' => [],
                'required' => false,
            ],
            [
                'label' => 'Placeholder 17',
                'rules' => [],
                'validation_messages' => [],
                'required' => false,
            ],
            [
                'label' => 'Placeholder 18',
                'rules' => [],
                'validation_messages' => [],
                'required' => false,
            ],
            [
                'label' => 'Placeholder 19',
                'rules' => [],
                'validation_messages' => [],
                'required' => false,
            ],
            [
                'label' => 'Placeholder 20',
                'rules' => [],
                'validation_messages' => [],
                'required' => false,
            ],
        ]);

        $columns->each(function ($column) {
            DatasetImportColumn::updateOrCreate(
                ['label' => $column['label']],
                [...$column, 'key' => $column['key'] ?? $this->sanitizeLabel($column['label'])]
            );
        });
    }
}
