<?php

namespace Database\Seeders;

use App\Models\DatasetImportColumn;
use Illuminate\Database\Seeder;

class DatasetImportColumnSeederArchive extends Seeder
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
                'validation_messages' => ['Well ID - must be a number'],
                'required' => true,
            ],
            [
                'label' => 'Census Tract ID',
                'rules' => ['numeric'],
                'validation_messages' => ['Census Tract ID - must be a number or empty'],
                'required' => false,
            ],
            [
                'label' => 'Well Type',
                'rules' => ['string', 'in:Oil,Gas,Both'],
                'validation_messages' => ['Well Type - must be a string and Oil, Gas, or Both'],
                'required' => true,
            ],
            [
                'label' => 'State Code',
                'rules' => ['numeric'],
                'validation_messages' => ['State Code - must be a number or empty'],
                'required' => false,
            ],
            [
                'label' => 'County Code',
                'rules' => ['numeric'],
                'validation_messages' => ['County Code - must be a number or empty'],
                'required' => false,
            ],
            [
                'label' => 'Land Area',
                'rules' => ['numeric'],
                'validation_messages' => ['Land Area - must be a number or empty'],
                'required' => false,
            ],
            [
                'label' => 'H2s Leak [Yes/No]',
                'rules' => ['boolean'],
                'validation_messages' => ['H2s Leak - must be Yes or No'],
                'required' => false,
            ],
            [
                'label' => 'State Wetlands Close Range',
                'rules' => ['numeric'],
                'validation_messages' => ['State Wetlands Close Range - must be a number or empty'],
                'required' => false,
            ],
            [
                'label' => 'State Wetlands Medium Range',
                'rules' => ['numeric'],
                'validation_messages' => ['State Wetlands Medium Range - must be a number or empty'],
                'required' => false,
            ],
            [
                'label' => 'State Wetlands Wide Range',
                'rules' => ['numeric'],
                'validation_messages' => ['State Wetlands Wide Range - must be a number or empty'],
                'required' => false,
            ],
            [
                'label' => 'Federal Wetlands Close Range',
                'rules' => ['numeric'],
                'validation_messages' => ['Federal Wetlands Close Range - must be a number or empty'],
                'required' => false,
            ],
            [
                'label' => 'Federal Wetlands Medium Range',
                'rules' => ['numeric'],
                'validation_messages' => ['Federal Wetlands Medium Range - must be a number or empty'],
                'required' => false,
            ],
            [
                'label' => 'Federal Wetlands Wide Range',
                'rules' => ['numeric'],
                'validation_messages' => ['Federal Wetlands Wide Range - must be a number or empty'],
                'required' => false,
            ],
            [
                'label' => 'Buildings Close Range',
                'rules' => ['numeric'],
                'validation_messages' => ['Buildings Close Range - must be a number or empty'],
                'required' => false,
            ],
            [
                'label' => 'Buildings Medium Range',
                'rules' => ['numeric'],
                'validation_messages' => ['Buildings Medium Range - must be a number or empty'],
                'required' => false,
            ],
            [
                'label' => 'Buildings Wide Range',
                'rules' => ['numeric'],
                'validation_messages' => ['Buildings Wide Range - must be a number or empty'],
                'required' => false,
            ],
            [
                'label' => 'Schools Close Range',
                'rules' => ['numeric'],
                'validation_messages' => ['Schools Close Range - must be a number or empty'],
                'required' => false,
            ],
            [
                'label' => 'Schools Medium Range',
                'rules' => ['numeric'],
                'validation_messages' => ['Schools Medium Range - must be a number or empty'],
                'required' => false,
            ],
            [
                'label' => 'Schools Wide Range',
                'rules' => ['numeric'],
                'validation_messages' => ['Schools Wide Range - must be a number or empty'],
                'required' => false,
            ],
            [
                'label' => 'Hospitals Close Range',
                'rules' => ['numeric'],
                'validation_messages' => ['Hospitals Close Range - must be a number or empty'],
                'required' => false,
            ],
            [
                'label' => 'Hospitals Medium Range',
                'rules' => ['numeric'],
                'validation_messages' => ['Hospitals Medium Range - must be a number or empty'],
                'required' => false,
            ],
            [
                'label' => 'Hospitals Wide Range',
                'rules' => ['numeric'],
                'validation_messages' => ['Hospitals Wide Range - must be a number or empty'],
                'required' => false,
            ],
            [
                'label' => '5-Year Oil Production [bbl]',
                'rules' => ['numeric'],
                'validation_messages' => ['5-Year Oil Production - must be a number or empty'],
                'required' => false,
            ],
            [
                'label' => '5-Year Gas Production [Mcf]',
                'rules' => ['numeric'],
                'validation_messages' => ['5-Year Gas Production - must be a number or empty'],
                'required' => false,
            ],
            [
                'label' => 'Name',
                'rules' => ['string'],
                'validation_messages' => ['Name - must be a string or empty'],
                'required' => false,
            ],
            [
                'label' => 'Disadvantaged Community Status [State-level]',
                'rules' => ['numeric'],
                'validation_messages' => ['Disadvantaged Community Status - must be a number or empty'],
                'required' => false,
            ],
            [
                'label' => 'Lifelong Oil Production [bbl]',
                'rules' => ['numeric'],
                'validation_messages' => ['Lifelong Oil Production - must be a number or empty'],
                'required' => false,
            ],
            [
                'label' => 'Lifelong Gas Production [Mcf]',
                'rules' => ['numeric'],
                'validation_messages' => ['Lifelong Gas Production - must be a number or empty'],
                'required' => false,
            ],
            [
                'label' => 'Methane Leak [Yes/No]',
                'rules' => ['boolean'],
                'validation_messages' => ['Methane Leak - must be Yes or No'],
                'required' => false,
            ],
            [
                'label' => 'Contamination [Yes/No]',
                'rules' => ['boolean'],
                'validation_messages' => ['Contamination - must be Yes or No'],
                'required' => false,
            ],
            [
                'label' => 'Leak [Yes/No]',
                'rules' => ['boolean'],
                'validation_messages' => ['Leak - must be Yes or No'],
                'required' => false,
            ],
            [
                'label' => 'Violation [Yes/No]',
                'rules' => ['boolean'],
                'validation_messages' => ['Violation - must be Yes or No'],
                'required' => false,
            ],
            [
                'label' => 'Incident [Yes/No]',
                'rules' => ['boolean'],
                'validation_messages' => ['Incident - must be Yes or No'],
                'required' => false,
            ],
            [
                'label' => 'Compliance [Yes/No]',
                'rules' => ['boolean'],
                'validation_messages' => ['Compliance - must be Yes or No'],
                'required' => false,
            ],
            [
                'label' => 'Oil [bbl/Year]',
                'rules' => ['numeric'],
                'validation_messages' => ['Oil - must be a number or empty'],
                'required' => false,
            ],
            [
                'label' => 'Gas [Mcf/Year]',
                'rules' => ['numeric'],
                'validation_messages' => ['Gas - must be a number or empty'],
                'required' => false,
            ],
            [
                'label' => 'Age [Years]',
                'rules' => ['numeric'],
                'validation_messages' => ['Age - must be a number or empty'],
                'required' => false,
            ],
            [
                'label' => 'Depth [ft]',
                'rules' => ['numeric'],
                'validation_messages' => ['Depth - must be a number or empty'],
                'required' => false,
            ],
            [
                'label' => 'Elevation Delta [m]',
                'rules' => ['numeric'],
                'validation_messages' => ['Elevation Delta - must be a number or empty'],
                'required' => false,
            ],
            [
                'label' => 'Distance to Road [miles]',
                'rules' => ['numeric'],
                'validation_messages' => ['Distance to Road - must be a number or empty'],
                'required' => false,
            ],
            [
                'label' => 'Operator Name',
                'rules' => ['string'],
                'validation_messages' => ['Operator Name - must be a string or empty'],
                'required' => false,
            ],
            [
                'label' => 'Latitude',
                'rules' => ['numeric'],
                'validation_messages' => ['Latitude or X - must be a number'],
                'required' => false,
            ],
            [
                'label' => 'x',
                'rules' => ['numeric'],
                'validation_messages' => ['Latitude or X - must be a number'],
                'required' => false,
            ],
            [
                'label' => 'Longitude',
                'rules' => ['numeric'],
                'validation_messages' => ['Longitude or Y - must be a number'],
                'required' => false,
            ],
            [
                'label' => 'y',
                'rules' => ['numeric'],
                'validation_messages' => ['Longitude or Y - must be a number'],
                'required' => false,
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
                [...$column, 'key' => $this->sanitizeLabel($column['label'])]
            );
        });
    }
}
