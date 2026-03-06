<?php

namespace App\Repositories;

use App\Exports\RankedWellsExport;
use App\Exports\RawDataExport;
use App\Exports\ScenarioRankedWellsExport;
use App\Models\Scenario;
use Illuminate\Support\Str;

class ExportRepository
{
    public array $headings = [];

    public ?string $taskId;

    public ?string $sortOrder;

    public ?int $datasetId;

    public array $wellTypeValues;

    public function __construct(
        public array $columns,
        public ?string $sortField,
        public ?int $numericSortOrder,
        public ?array $wellType,
        public string|int $primaryId,
        public ?string $secondaryId = null, // Holder for task id for raw data sort
        public ?Scenario $scenario = null
    ) {}

    public function generateRankedWellsExport(): object
    {
        $this->parseExcelData('RANKED');

        return new RankedWellsExport(
            $this->headings,
            $this->columns,
            $this->sortField,
            $this->sortOrder,
            $this->taskId,
            $this->wellTypeValues
        );
    }

    public function generateScenarioRankedWellsExport(): object
    {
        return new ScenarioRankedWellsExport($this->scenario, $this);
    }

    public function generateRawDataExport(): object
    {
        $this->parseExcelData('RAW');

        return new RawDataExport(
            $this->headings,
            $this->columns,
            $this->sortField,
            $this->sortOrder,
            $this->taskId,
            $this->datasetId,
            $this->wellTypeValues
        );
    }

    private function parseExcelData(string $type)
    {
        $this->headings = collect($this->columns)->map(function ($heading) {
            return $heading['header'];
        })->toArray();

        $this->columns = collect($this->columns)->map(function ($column) {
            return [
                'header' => $column['header'],
                'key' => Str::snake($column['key']),
            ];
        })->toArray();

        $sortOrder = ! is_null($this->numericSortOrder) ? $this->numericSortOrder : 'asc';
        $defaultSortField = $type === 'RANKED' ? 'wellRank' : 'wellId';
        $sortField = ! is_null($this->sortField) ? $this->sortField : $defaultSortField;
        $sortOrder = $sortOrder === -1 ? 'desc' : 'asc';

        if (! is_null($sortField)) {
            $sortField = Str::snake($sortField);
        }

        $this->sortField = $sortField;
        $this->sortOrder = $sortOrder;
        $this->wellTypeValues = $this->wellType ?? [];

        if ($type === 'RANKED') {
            $this->taskId = $this->primaryId;
        } else {
            $this->datasetId = $this->primaryId;
            if ($this->secondaryId) {
                $this->taskId = $this->secondaryId;
            }
        }
    }
}
