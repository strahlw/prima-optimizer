<?php

namespace App\Exports\ScenarioProjects;

use App\Models\Project;
use App\Models\Well;
use Illuminate\Support\Collection;
use Maatwebsite\Excel\Concerns\FromCollection;
use Maatwebsite\Excel\Concerns\WithEvents;
use Maatwebsite\Excel\Concerns\WithStyles;
use Maatwebsite\Excel\Concerns\WithTitle;
use Maatwebsite\Excel\Events\AfterSheet;
use PhpOffice\PhpSpreadsheet\Style\Border;

class ProjectWellsExport implements FromCollection, WithEvents, WithStyles, WithTitle
{
    protected Collection $projects;

    protected string $type;

    public array $headings = [
        'Project',
        'API Well Number',
        'Operator Name',
        'Well Priority Score',
        'Efficiency Score',
        'Gas [Mcf/Year]',
        'Oil [bbl/Year]',
        'Age [Years]',
        'Depth [ft]',
        'Latitude',
        'Longitude',
        'Incident [Yes/No]',
        'Violation [Yes/No]',
        'Compliance [Yes/No]',
        'Leak [Yes/No]',
        'Number of Schools near the Well',
        'Number of Hospitals near the Well',
    ];

    public function __construct(Collection $projects, string $type)
    {
        $this->projects = $projects;
        $this->type = $type;
    }

    /**
     * @return \Illuminate\Support\Collection
     */
    public function collection()
    {
        return $this->projects->map(function (Project $project) {
            $header = [$this->headings];
            $rows = $project->wells()->get()->map(function (Well $well) use ($project) {
                // Deprecated from autoloading json values for Well model in Phase 2
                // $data = $well->json;

                return [
                    $project->id,
                    $well->well_id,
                    $well->operator_name,
                    $well->priority_score ?? $well->well_priority_score ?? '',
                    $well->efficiency_score ?? '',
                    $well->annual_gas_production,
                    $well->annual_oil_production,
                    $well->age,
                    $well->depth,
                    $well->latitude,
                    $well->longitude,
                    $this->formatBooleanField($well->incident),
                    $this->formatBooleanField($well->violation),
                    $this->formatBooleanField($well->compliance),
                    $this->formatBooleanField($well->leak),
                    $well->num_of_schools_near_well ?? '',
                    $well->num_of_hospitals_near_well ?? '',
                ];
            });
            $blankRow = [[]];

            return array_merge($header, $rows->toArray(), $blankRow);
        });
    }

    private function formatBooleanField(?bool $value): string
    {
        $fieldValue = $value ?? null;

        if (! is_null($fieldValue)) {
            return $fieldValue ? 'Yes' : 'No';
        }

        return '';
    }

    public function title(): string
    {
        return $this->type.' Well Projects';
    }

    public function styles(\PhpOffice\PhpSpreadsheet\Worksheet\Worksheet $sheet)
    {
        return [
            // Make the headers bold
            1 => ['font' => ['bold' => true]],
        ];
    }

    public function registerEvents(): array
    {
        return [
            AfterSheet::class => function (AfterSheet $event) {
                $sheet = $event->sheet->getDelegate();
                $currentRow = 1;

                foreach (range('A', 'R') as $column) { // Adjust range based on the number of columns
                    $sheet->getColumnDimension($column)->setAutoSize(true);
                }

                // NOTE: R hardcoded for length of headers
                foreach ($this->projects as $project) {
                    // Style each project's header
                    $sheet->getStyle("A{$currentRow}:R{$currentRow}")->applyFromArray([
                        'font' => ['bold' => true],
                        'borders' => [
                            'outline' => [
                                'borderStyle' => Border::BORDER_THIN,
                                'color' => ['argb' => '000000'],
                            ],
                        ],
                        'fill' => ['fillType' => 'solid', 'startColor' => ['rgb' => 'D5D3D5']],
                    ]);

                    // Skip rows for the project's wells
                    $currentRow += $project->wells()->count() + 2; // Account for header and blank row
                }
            },
        ];
    }
}
