<?php

namespace App\Actions;

use App\Models\Scenario;
use App\Repositories\ScenarioRepository;
use App\Types\EfficiencyFactors;
use App\Types\GeneralSpecifications;
use App\Types\ImpactFactors;
use App\Types\RankOnlyScenarioData;
use App\Types\RecommendationOnlyScenarioData;
use App\Types\ScenarioData;

class RankExistingScenario
{
    public function __construct(protected ScenarioRepository $scenarioRepository) {}

    public function execute(Scenario $scenario): string
    {
        // TODO: Reevaulate why a scenario would prefer parent data over its own
        $data = $scenario->parent ? $scenario->parent->data : $scenario->data;

        if ($scenario->isRankOnly) {
            $scenarioData = new RankOnlyScenarioData(
                new GeneralSpecifications(...$data['general_specifications']),
                new ImpactFactors(...$data['impact_factors']),
                $scenario->useCases
            );
        } elseif ($scenario->isRecommendationOnly) {
            $scenarioData = new RecommendationOnlyScenarioData(
                new GeneralSpecifications(...$data['general_specifications']),
                new EfficiencyFactors(...$data['efficiency_factors']),
                $scenario->useCases
            );
        } else {
            $scenarioData = new ScenarioData(
                new GeneralSpecifications(...$data['general_specifications']),
                new ImpactFactors(...$data['impact_factors']),
                new EfficiencyFactors(...$data['efficiency_factors']),
                $scenario->useCases
            );
        }

        return $this->scenarioRepository->createRanking($scenarioData);
    }
}
