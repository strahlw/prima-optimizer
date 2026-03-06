<?php

namespace App\Types;

class ScenarioData
{
    public string $name;

    public ?int $scenario_id;

    public function __construct(
        public GeneralSpecifications $general_specifications,
        public ImpactFactors $impact_factors,
        public EfficiencyFactors $efficiency_factors,
        public UseCases $use_cases
    ) {
        $this->name = $general_specifications->name;
        $this->general_specifications = $general_specifications;
        $this->impact_factors = $impact_factors;
        $this->efficiency_factors = $efficiency_factors;
        $this->use_cases = $use_cases;
    }
}
