<?php

namespace App\Exports\ScenarioProjects;

use App\Models\Project;
use App\Models\Scenario;
use App\Models\Well;
use Illuminate\Support\Facades\Log;
use Maatwebsite\Excel\Concerns\FromCollection;
use Maatwebsite\Excel\Concerns\RegistersEventListeners;
use Maatwebsite\Excel\Concerns\ShouldAutoSize;
use Maatwebsite\Excel\Concerns\WithCustomStartCell;
use Maatwebsite\Excel\Concerns\WithDrawings;
use Maatwebsite\Excel\Concerns\WithEvents;
use Maatwebsite\Excel\Concerns\WithHeadings;
use Maatwebsite\Excel\Concerns\WithStyles;
use Maatwebsite\Excel\Concerns\WithTitle;
use Maatwebsite\Excel\Events\AfterSheet;
use PhpOffice\PhpSpreadsheet\Worksheet\Drawing;
use PhpOffice\PhpSpreadsheet\Worksheet\Worksheet;

class ProjectsDownloadExport implements FromCollection, ShouldAutoSize, WithCustomStartCell, WithDrawings, WithEvents, WithHeadings, WithStyles, WithTitle
{
    use RegistersEventListeners;

    protected string $imgPath;

    protected array $projectColorMap;

    protected int $mapWidth;

    protected int $mapHeight;

    protected Scenario $scenario;

    public function __construct(string $imgPath, array $projectColorMap, int $mapWidth, int $mapHeight, Scenario $scenario)
    {
        $this->imgPath = $imgPath;
        $this->projectColorMap = $projectColorMap;
        $this->mapWidth = $mapWidth;
        $this->mapHeight = $mapHeight;
        $this->scenario = $scenario;
    }

    public function styles(Worksheet $sheet)
    {
        return [
            // Style the first row as bold text.
            1 => ['font' => ['bold' => true], 'fill' => ['fillType' => 'solid', 'startColor' => ['rgb' => 'D5D3D5']]],
        ];
    }

    public function headings(): array
    {
        return [
            'Color',
            'Scenario ID',
            'Project ID',
            'Well Rank',
            'Operator Name',
            'Well ID',
            'Well Priority Score',
            'Well Efficiency Score',
            'Age',
            'Annual Oil Production',
            'Annual Gas Production',
            'Well Name',
            'Latitude',
            'Longitude',
            'Depth',
            'Incident',
            'Violation',
            'Compliance',
            'Leak',
            'H2s Leak',
            'Number of Schools near the Well',
            'Number of Hospitals near the Well',
        ];
    }

    public function drawings()
    {
        // Add the Map and Legend images
        $mapAspectRatio = $this->mapWidth / $this->mapHeight;
        $drawing = new Drawing;
        $drawing->setName('Map');
        $drawing->setDescription('This is a map image');
        $drawing->setPath(storage_path('app/'.$this->imgPath));
        $drawing->setWidth(1300);
        $drawing->setHeight(1300 / $mapAspectRatio);
        $drawing->setCoordinates('A2');

        $legendDrawing = new Drawing;
        $legendDrawing->setName('Legend');
        $legendDrawing->setDescription('This is a legend image');
        $legendDrawing->setPath(public_path('images/legend.png'));
        $legendDrawing->setCoordinates('Q3');

        return [$drawing, $legendDrawing];
    }

    /**
     * @return \Illuminate\Support\Collection
     */
    public function collection()
    {
        $projectIds = collect($this->projectColorMap)->map(fn ($data) => $data->id);
        $wells = Project::where('scenario_id', $this->scenario->id)->whereIn('id', $projectIds)->get()->sortBy('scenario_id')->map(function (Project $project) {
            $currentColor = null;
            if ($this->projectColorMap) {
                $currentColor = collect($this->projectColorMap)->firstWhere('id', $project->id)->color ?? '';
            }

            return $project->getWells()->map(function (Well $well) use ($project, $currentColor) {
                $rows = [
                    $project->scenario_id,
                    "$project->id",
                    $well->well_rank ?? '',
                    $well->operator_name ?? '',
                    $well->well_id ?? '',
                    $well->priority_score ?? $well->json['well_priority_score'] ?? $well->well_priority_score,
                    $well->efficiency_score ?? $well->json['well_efficiency_score'] ?? $well->well_efficiency_score ?? '',
                    $well->age ?? '',
                    $well->annual_oil_production ?? '',
                    $well->annual_gas_production ?? '',
                    $well->well_name ?? '',
                    $well->latitude ?? '',
                    $well->longitude ?? '',
                    $well->depth ?? '',
                    $this->formatBooleanField($well->incident),
                    $this->formatBooleanField($well->violation),
                    $this->formatBooleanField($well->compliance),
                    $this->formatBooleanField($well->leak),
                    $this->formatBooleanField($well->h2s_leak),
                    $well->num_of_schools_near_well ?? '',
                    $well->num_of_hospitals_near_well ?? '',
                ];

                if ($currentColor) {
                    $rows = array_merge(['color' => $currentColor], $rows);
                }

                return $rows;
            });
        })->flatten(1);

        if ($wells->isEmpty()) {
            Log::error('No wells found for the given scenario and project IDs.');
        }

        return $wells;
    }

    public function startCell(): string
    {
        return 'S1';
    }

    public function registerEvents(): array
    {
        return [
            AfterSheet::class => function (AfterSheet $event) {
                // Start filling the color column with background color from row 2 onward
                $sheet = $event->sheet->getDelegate();
                $wells = $this->collection(); // Get the well collection
                $rowNumber = 2; // Start from row 2, assuming row 1 is for headings
                $lastColumn = 'AK';

                foreach ($wells as $well) {
                    $color = $well['color'] ?? null;
                    if ($color) {
                        $sheet->getStyle('S'.$rowNumber)->getFill()->setFillType('solid')->getStartColor()->setARGB(ltrim($color, '#'));

                        $sheet->setCellValue('S'.$rowNumber, '');
                    }
                    // Apply alternating row colors (every other row)
                    if ($rowNumber % 2 == 0) {
                        // Even row: light gray background
                        $sheet->getStyle('T'.$rowNumber.':AK'.$rowNumber) // Adjust the column range as needed
                            ->getFill()->setFillType('solid')->getStartColor()->setRGB('F5F5F5');
                    } else {
                        // Odd row: no background color or keep it white
                        $sheet->getStyle('T'.$rowNumber.':AK'.$rowNumber) // Adjust the column range as needed
                            ->getFill()->setFillType('solid')->getStartColor()->setRGB('FFFFFF');
                    }

                    $sheet->getStyle('T'.$rowNumber.':'.$lastColumn.$rowNumber)->getBorders()->getAllBorders()->setBorderStyle(\PhpOffice\PhpSpreadsheet\Style\Border::BORDER_THIN);

                    $rowNumber++;
                }

                $sheet->getStyle('S1:'.$lastColumn.'1')->getBorders()->getAllBorders()->setBorderStyle(\PhpOffice\PhpSpreadsheet\Style\Border::BORDER_THIN);

            },
        ];
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
        return 'Map View';
    }
}
