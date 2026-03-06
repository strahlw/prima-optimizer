<?php

namespace App\Exports\ScenarioProjects;

use App\Models\Project;
use Illuminate\Support\Collection;
use Illuminate\Support\Facades\Log;
use Maatwebsite\Excel\Concerns\FromCollection;
use Maatwebsite\Excel\Concerns\WithEvents;
use Maatwebsite\Excel\Concerns\WithHeadings;
use Maatwebsite\Excel\Concerns\WithStyles;
use Maatwebsite\Excel\Concerns\WithTitle;
use Maatwebsite\Excel\Events\AfterSheet;
use PhpOffice\PhpSpreadsheet\Style\Border;

class ProjectScoresExport implements FromCollection, WithEvents, WithHeadings, WithStyles, WithTitle
{
    protected Collection $projects;

    protected string $type;

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
        $projectCollection = $this->projects->map(function (Project $project) {
            return [
                'project' => $project->id,
                'number_of_wells' => $project->wellCount,
                'impact_score' => $project->impact_score,
                'efficiency_score' => $project->efficiency_score,
            ];
        });

        if ($projectCollection->isEmpty()) {
            Log::error("No data found for prohject scores export of type {$this->type}.");
        }

        return $projectCollection;
    }

    public function headings(): array
    {
        return [
            'Project',
            'Number of Wells',
            'Impact Score [0-100]',
            'Efficiency Score [0-100]',
        ];
    }

    public function title(): string
    {
        return $this->type.' Project Scores';
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

                // NOTE: D hardcoded to match headers
                foreach (range('A', 'D') as $column) { // Adjust range based on the number of columns
                    $sheet->getColumnDimension($column)->setAutoSize(true);
                }

                // NOTE: D hardcoded for length of headers
                $sheet->getStyle('A1:D1')->applyFromArray([
                    'font' => ['bold' => true],
                    'borders' => [
                        'outline' => [
                            'borderStyle' => Border::BORDER_THIN,
                            'color' => ['argb' => '000000'],
                        ],
                    ],
                    'fill' => ['fillType' => 'solid', 'startColor' => ['rgb' => 'D5D3D5']],
                ]);
            },
        ];
    }
}
