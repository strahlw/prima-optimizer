<?php

namespace App\Actions;

use App\Exceptions\PrimoApiException;
use App\Models\Scenario;
use App\Services\PrimoApiService;
use Illuminate\Support\Facades\Log;

class GetKPISummaryInformation
{
    public function execute(Scenario $scenario)
    {
        try {
            $primoApiService = new PrimoApiService;
            $primoApiService->verifyConnection();
            $scenarioData = [
                'scenario_id' => $scenario->id,
                ...$scenario->data,
                'project_ids' => $scenario->projects->pluck('id')->toArray(),
            ];

            $kpiData = $primoApiService->getKPISummaryInformation($scenarioData);
            $kpiData->impactFactors = $scenario->impactFactors;
            $kpiData->efficiencyFactors = $scenario->efficiencyFactors;

            return $kpiData;
        } catch (PrimoApiException $e) {
            throw $e;
        } catch (\Exception $e) {
            Log::error("An error occurred while fetching KPI summary for scenario ID {$scenario->id}:");
            Log::error($e->getTraceAsString());
            throw $e;
        }
    }
}
