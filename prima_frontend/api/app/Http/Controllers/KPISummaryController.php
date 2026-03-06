<?php

namespace App\Http\Controllers;

use App\Actions\GetKPISummaryInformation;
use App\Models\Scenario;
use Exception;

class KPISummaryController extends Controller
{
    public function __invoke(Scenario $scenario)
    {
        try {
            $kpiData = app()->make(GetKPISummaryInformation::class)->execute($scenario);

            return response()->json($kpiData, 200);
        } catch (Exception $e) {
            return response()->json([
                'message' => 'Failed to fetch KPI summary.',
                'error' => $e->getMessage(),
            ], 500);
        }
    }
}
