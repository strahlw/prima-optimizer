<?php

namespace App\Exports;

use App\Models\Dataset;
use App\Models\DatasetJson;
use App\Repositories\DatasetJsonRepository;
use App\WellExportTrait;
use Maatwebsite\Excel\Concerns\FromCollection;
use Maatwebsite\Excel\Concerns\WithHeadings;
use Maatwebsite\Excel\Concerns\WithStyles;

class RawDataExport implements FromCollection, WithHeadings, WithStyles
{
    use WellExportTrait;

    protected DatasetJsonRepository $repository;

    public function __construct(
        array $headings,
        array $columns,
        ?string $sortField,
        ?string $sortOrder,
        ?string $taskId,
        ?int $datasetId,
        array $wellTypeValues
    ) {
        $this->headings = $headings;
        $this->columns = $columns;
        $this->sortField = $sortField;
        $this->sortOrder = $sortOrder;
        $this->taskId = $taskId;
        $this->datasetId = $datasetId;
        $this->wellTypeValues = $wellTypeValues;
        $this->repository = app()->make(DatasetJsonRepository::class);
    }

    /**
     * @return \Illuminate\Support\Collection
     */
    public function collection()
    {
        $rawData = $this->repository->sortDatasetJsonWells(
            Dataset::find($this->datasetId),
            $this->sortField,
            $this->sortOrder,
            $this->wellTypeValues,
            null,
            null,
            $this->taskId ?? null
        )->values();

        return $rawData->map(function (DatasetJson $data) {
            return array_merge($data->json, $data->toArray());
        })->map(function ($row) {
            return collect($this->columns)->mapWithKeys(function ($column) use ($row) {
                $key = $column['key'];
                $value = $row[$key] ?? null;

                // Check if value is numeric and format it
                if ($key === 'latitude' || $key === 'longitude') {
                    return [$column['header'] => number_format($value, 5, '.', '')];
                } elseif (is_numeric($value)) {
                    return [$column['header'] => number_format($value, 2, '.', '')];
                }

                return [$column['header'] => $value];
            });
        })->values();
    }
}
