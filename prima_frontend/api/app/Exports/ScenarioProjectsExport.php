<?php

namespace App\Exports;

use App\Actions\RankExistingScenario;
use App\Constants\RankColumnDefinitions;
use App\Enum\WellType;
use App\Exports\ScenarioProjects\ProjectScoresExport;
use App\Exports\ScenarioProjects\ProjectsDownloadExport;
use App\Exports\ScenarioProjects\ProjectWellsExport;
use App\Exports\ScenarioProjects\ScenarioParamsExport;
use App\Models\Project;
use App\Models\Scenario;
use App\Repositories\ExportRepository;
use Maatwebsite\Excel\Concerns\Exportable;
use Maatwebsite\Excel\Concerns\WithMultipleSheets;

class ScenarioProjectsExport implements WithMultipleSheets
{
    use Exportable;

    public string $imgPath;

    public array $projectColorMap;

    public int $mapWidth;

    public int $mapHeight;

    public Scenario $scenario;

    public function __construct(
        string $imgPath,
        array $projectColorMap,
        int $mapWidth,
        int $mapHeight,
        Scenario $scenario
    ) {
        $this->imgPath = $imgPath;
        $this->projectColorMap = $projectColorMap;
        $this->mapWidth = $mapWidth;
        $this->mapHeight = $mapHeight;
        $this->scenario = $scenario;
    }

    public function sheets(): array
    {
        $sheets = [];

        $sheets[] = new ProjectsDownloadExport(
            $this->imgPath,
            $this->projectColorMap,
            $this->mapWidth,
            $this->mapHeight,
            $this->scenario
        );

        [$oilProjects, $gasProjects] = $this->scenario->projects->partition(function (Project $project) {
            return $project->majorityWellType === WellType::OIL;
        });

        if ($oilProjects->isNotEmpty()) {
            $sheets[] = new ProjectScoresExport($oilProjects, WellType::OIL);
            $sheets[] = new ProjectWellsExport($oilProjects, WellType::OIL);
        }

        if ($gasProjects->isNotEmpty()) {
            $sheets[] = new ProjectScoresExport($gasProjects, WellType::GAS);
            $sheets[] = new ProjectWellsExport($gasProjects, WellType::GAS);
        }

        $sheets[] = new ScenarioParamsExport($this->scenario);

        $taskId = app()->make(RankExistingScenario::class)->execute($this->scenario);
        if ($taskId) {
            $repo = new ExportRepository(
                columns: collect(RankColumnDefinitions::RANK_COLS)->map(function ($item, $key) {
                    return [
                        'header' => $item,
                        'key' => $key,
                    ];
                })->toArray(),
                sortField: 'wellRank',
                numericSortOrder: 1,
                wellType: [],
                primaryId: $taskId,
                secondaryId: null,
                scenario: $this->scenario
            );
            $sheets[] = $repo->generateRankedWellsExport();
        }

        return $sheets;
    }
}
