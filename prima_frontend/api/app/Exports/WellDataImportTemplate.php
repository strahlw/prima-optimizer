<?php

namespace App\Exports;

use App\Enum\DatasetImportColumnPriority;
use App\Models\DatasetImportColumn;
use Maatwebsite\Excel\Concerns\FromCollection;
use Maatwebsite\Excel\Concerns\WithHeadings;
use Maatwebsite\Excel\Concerns\WithStyles;
use PhpOffice\PhpSpreadsheet\Style\Color;
use PhpOffice\PhpSpreadsheet\Style\Fill;

class WellDataImportTemplate implements FromCollection, WithHeadings, WithStyles
{
    public function collection()
    {
        return collect();
    }

    public function headings(): array
    {
        $labels = DatasetImportColumn::all()->sortBy(function ($item) {
            return $item['order'] ?? PHP_INT_MAX;
        })->pluck('label')->toArray();

        return [
            $labels,
        ];
    }

    public function styles($sheet)
    {
        $sheet->getStyle('1:1')->applyFromArray([
            'font' => [
                'bold' => true,
            ],
        ]);

        $columns = DatasetImportColumn::all()
            ->sortBy(function ($item) {
                return $item['order'] ?? PHP_INT_MAX;
            });

        foreach ($columns as $index => $column) {
            // Apply conditional background color based on 'priority' field
            $priority = $column->priority;
            $columnLetter = \PhpOffice\PhpSpreadsheet\Cell\Coordinate::stringFromColumnIndex($index + 1);

            $backgroundColor = $this->getPriorityColor($priority);
            $sheet->getStyle("{$columnLetter}1")->getFill()->setFillType(Fill::FILL_SOLID);
            $sheet->getStyle("{$columnLetter}1")->getFill()->getStartColor()->setARGB($backgroundColor);
        }
    }

    private function getPriorityColor($priority)
    {
        // Map priority to color
        switch ($priority) {
            case DatasetImportColumnPriority::REQUIRED:
                return Color::COLOR_RED;
            case DatasetImportColumnPriority::RECOMMENDED:
                return Color::COLOR_YELLOW;
            case DatasetImportColumnPriority::OPTIONAL:
                return Color::COLOR_GREEN;
            default:
                return Color::COLOR_WHITE;
        }
    }
}
