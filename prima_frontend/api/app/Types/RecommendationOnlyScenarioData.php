<?php

namespace App\Types;

class RecommendationOnlyScenarioData
{
    public string $name;

    public ?int $scenario_id;

    public function __construct(
        public GeneralSpecifications $general_specifications,
        public EfficiencyFactors $efficiency_factors,
        public UseCases $use_cases
    ) {
        $this->name = $general_specifications->name;
    }
}
