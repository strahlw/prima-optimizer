<?php

namespace App\Exports\ScenarioProjects;

use App\Models\Scenario;
use Illuminate\Support\Str;
use Maatwebsite\Excel\Concerns\FromCollection;
use Maatwebsite\Excel\Concerns\WithEvents;
use Maatwebsite\Excel\Concerns\WithTitle;
use Maatwebsite\Excel\Events\AfterSheet;
use PhpOffice\PhpSpreadsheet\Style\Border;

class ScenarioParamsExport implements FromCollection, WithEvents, WithTitle
{
    protected Scenario $scenario;

    protected int $maxHeadings = 0;

    public function __construct(Scenario $scenario)
    {
        $this->scenario = $scenario;
    }

    /**
     * @return \Illuminate\Support\Collection
     */
    public function collection()
    {
        $data = $this->scenario->data;
        $generalSpecificationHeaders = collect([
            'ID',
            'Name',
            'Organization',
            'Dataset',
            'Well Types',
        ]);

        $omitFromDynamicFields = ['name', 'organization_id', 'dataset_id', 'well_type', 'additional_datasets'];

        $generalSpecifications = collect([
            $this->scenario->id,
            $data['name'] ?? '',
            $this->scenario->organization->key,
            $this->scenario->dataset->name,
            implode(', ', $data['general_specifications']['well_type']),
        ]);

        collect($data['general_specifications'])->filter(function ($value, $key) use ($omitFromDynamicFields) {
            return ! in_array($key, $omitFromDynamicFields);
        })->each(function ($value, $key) use (&$generalSpecifications, &$generalSpecificationHeaders) {
            $generalSpecificationHeaders->push($this->convertKeyToTitle($key));
            if (Str::contains($key, 'specified') && ! $value) {
                $value = is_null($value) ? 'null' : '0';
            }
            $generalSpecifications->push($value);
        });

        $impactFactorsHeaders = collect([]);
        $impactFactors = collect([]);

        if (array_key_exists('impact_factors', $data)) {
            collect($data['impact_factors'])->each(function ($value, $key) use (&$impactFactors, &$impactFactorsHeaders) {
                $factorTitle = $this->convertKeyToTitle($key);
                $impactFactorsHeaders->push($factorTitle);
                $impactFactors->push($value['value']);

                if (isset($value['child_factors'])) {
                    collect($value['child_factors'])->each(function ($childValue, $childKey) use (&$impactFactors, &$impactFactorsHeaders, $factorTitle) {
                        $impactFactorsHeaders->push($factorTitle.' - '.$this->convertKeyToTitle($childKey));
                        $impactFactors->push($childValue['value']);
                    });
                }
            });
        }

        $efficiencyFactorsHeaders = collect([]);
        $efficiencyFactors = collect([]);

        if (array_key_exists('efficiency_factors', $data)) {
            collect($data['efficiency_factors'])->each(function ($value, $key) use (&$efficiencyFactors, &$efficiencyFactorsHeaders) {
                $efficiencyFactorsHeaders->push($this->convertKeyToTitle($key));
                $efficiencyFactors->push($value['value']);
            });
        }

        $this->maxHeadings = max([$generalSpecificationHeaders->count(), $impactFactorsHeaders->count(), $efficiencyFactorsHeaders->count()]);

        return collect([
            ['General Specifications'],
            $generalSpecificationHeaders,
            $generalSpecifications,
            [[]],
            ['Impact Factors'],
            $impactFactorsHeaders,
            $impactFactors,
            [[]],
            ['Efficiency Factors'],
            $efficiencyFactorsHeaders,
            $efficiencyFactors,
        ]);
    }

    public function registerEvents(): array
    {
        return [
            AfterSheet::class => function (AfterSheet $event) {
                $sheet = $event->sheet->getDelegate();
                $currentRow = 2;

                $lastColumnIndex = $this->maxHeadings;
                $lastColumn = \PhpOffice\PhpSpreadsheet\Cell\Coordinate::stringFromColumnIndex($lastColumnIndex);

                // Instead of range('A', $lastColumn)
                for ($i = 1; $i <= $lastColumnIndex; $i++) {
                    $column = \PhpOffice\PhpSpreadsheet\Cell\Coordinate::stringFromColumnIndex($i);
                    $sheet->getColumnDimension($column)->setAutoSize(true);
                }

                // Rest of your code remains the same
                foreach ([0, 1, 2] as $paramsIndex) {
                    $headerRow = $currentRow - 1;
                    $sheet->getStyle("A{$headerRow}:{$lastColumn}{$headerRow}")->applyFromArray([
                        'font' => ['bold' => true],
                    ]);
                    $sheet->getStyle("A{$currentRow}:{$lastColumn}{$currentRow}")->applyFromArray([
                        'font' => ['bold' => true],
                        'borders' => [
                            'outline' => [
                                'borderStyle' => Border::BORDER_THIN,
                                'color' => ['argb' => '000000'],
                            ],
                        ],
                        'fill' => ['fillType' => 'solid', 'startColor' => ['rgb' => 'D5D3D5']],
                    ]);

                    $currentRow += 4;
                }
            },
        ];
    }

    private function convertKeyToTitle($key): string
    {
        return ucwords(str_replace('_', ' ', $key));
    }

    public function title(): string
    {
        return 'Scenario Parameters';
    }
}
