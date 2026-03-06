<?php

namespace App\Exports;

use App\Models\Ranking;
use App\Repositories\RankingRepository;
use App\WellExportTrait;
use Illuminate\Support\Collection;
use Illuminate\Support\Str;
use Maatwebsite\Excel\Concerns\FromCollection;
use Maatwebsite\Excel\Concerns\WithHeadings;
use Maatwebsite\Excel\Concerns\WithStyles;
use Maatwebsite\Excel\Concerns\WithTitle;

class RankedWellsExport implements FromCollection, WithHeadings, WithStyles, WithTitle
{
    use WellExportTrait;

    protected Collection $data;

    public RankingRepository $rankingRepository;

    public function __construct(
        array $headings,
        array $columns,
        ?string $sortField,
        ?string $sortOrder,
        ?string $taskId,
        array $wellTypeValues
    ) {
        $this->headings = $headings;
        $this->columns = $columns;
        $this->sortField = $sortField;
        $this->sortOrder = $sortOrder;
        $this->taskId = $taskId;
        $this->wellTypeValues = $wellTypeValues;
        $this->rankingRepository = new RankingRepository;
        $this->setupData();
    }

    private function setupData(): void
    {
        $baseModelFields = array_keys(Ranking::where('task_id', $this->taskId)->first()->toArray());
        $isBaseModelSortField = in_array(Str::snake($this->sortField), $baseModelFields);

        if (! is_null($this->sortField)) {
            $this->sortField = Str::snake($this->sortField);
        }

        if ($isBaseModelSortField) {
            $rankingData = $this->rankingRepository->baseModelSortFieldSearch(
                $this->sortField,
                $this->sortOrder,
                $this->taskId,
                $this->wellTypeValues
            );
        } else {
            $rankingData = $this->rankingRepository->datasetJsonFieldSearch(
                $this->sortField,
                $this->sortOrder,
                $this->taskId,
                $this->wellTypeValues
            );

            $rankingData = collect($rankingData);
        }

        $adjustedHeadings = collect([]);
        $rankValue = $rankingData->map(function ($row) use (&$adjustedHeadings) {
            return collect($this->columns)->mapWithKeys(function ($column) use ($row, &$adjustedHeadings) {
                $value = $row[$column['key']] ?? null;

                if (! is_null($value)) {
                    $adjustedHeadings->push($column['header']);
                } else {
                    return [];
                }

                // Check if value is numeric and format it
                if (is_numeric($value)) {
                    return [$column['header'] => number_format($value, 2, '.', '')];
                }

                return [$column['header'] => $value];
            });
        })->values();

        $this->headings = $adjustedHeadings->unique()->toArray();
        $this->data = $rankValue;
    }

    public function title(): string
    {
        return 'Ranked Wells';
    }

    /**
     * @return \Illuminate\Support\Collection
     */
    public function collection()
    {
        return $this->data;
    }
}
