<?php

namespace App;

use PhpOffice\PhpSpreadsheet\Worksheet\Worksheet;

trait WellExportTrait
{
    public array $headings = [];

    public array $columns;

    public ?string $sortField;

    public ?string $sortOrder;

    public ?string $taskId;

    public ?int $datasetId;

    public array $wellTypeValues;

    public function headings(): array
    {
        return $this->headings;
    }

    public function styles(Worksheet $sheet)
    {
        return [
            // Style the first row as bold text.
            1 => ['font' => ['bold' => true], 'fill' => ['fillType' => 'solid', 'startColor' => ['rgb' => 'D5D3D5']]],
        ];
    }
}
