<?php

namespace App\Exports;

use App\Exports\ScenarioProjects\ScenarioParamsExport;
use App\Models\Scenario;
use App\Repositories\ExportRepository;
use Maatwebsite\Excel\Concerns\Exportable;
use Maatwebsite\Excel\Concerns\WithMultipleSheets;

class ScenarioRankedWellsExport implements WithMultipleSheets
{
    use Exportable;

    public function __construct(
        public Scenario $scenario,
        public ExportRepository $exportRepository
    ) {}

    public function sheets(): array
    {
        $sheets = [];

        $sheets[] = $this->exportRepository->generateRankedWellsExport();

        $sheets[] = new ScenarioParamsExport($this->scenario);

        return $sheets;
    }
}
