<?php

namespace App\Types;

class ChildFactor
{
    public ?int $value = null;

    public bool $selected = false;

    public function __construct(?int $value = null, bool $selected = false)
    {
        $this->value = $value;
        $this->selected = $selected;
    }
}

class Losses extends Factor
{
    /**
     * @var ChildFactor[]
     */
    public array $child_factors;

    public function __construct(
        ?int $value = null, bool $selected = false, array $child_factors = []
    ) {
        $this->value = $value;
        $this->selected = $selected;
        $this->child_factors = [
            'leak' => new ChildFactor(...$child_factors['leak']),
            'violation' => new ChildFactor(...$child_factors['violation']),
            'compliance' => new ChildFactor(...$child_factors['compliance']),
            'incident' => new ChildFactor(...$child_factors['incident']),
            'hydrocarbon_losses' => new ChildFactor(...$child_factors['hydrocarbon_losses']),
        ];
    }
}

class AnnProductionVolume extends Factor
{
    /**
     * @var ChildFactor[]
     */
    public array $child_factors;

    public function __construct(
        ?int $value = null, bool $selected = false, array $child_factors = []
    ) {
        $this->value = $value;
        $this->selected = $selected;
        $this->child_factors = [
            'ann_gas_production' => new ChildFactor(...$child_factors['ann_gas_production']),
            'ann_oil_production' => new ChildFactor(...$child_factors['ann_oil_production']),
        ];
    }
}

class FiveYearProductionVolume extends Factor
{
    /**
     * @var ChildFactor[]
     */
    public array $child_factors;

    public function __construct(
        ?int $value = null, bool $selected = false, array $child_factors = []
    ) {
        $this->value = $value;
        $this->selected = $selected;
        $this->child_factors = [
            'five_year_gas_production' => new ChildFactor(...$child_factors['five_year_gas_production']),
            'five_year_oil_production' => new ChildFactor(...$child_factors['five_year_oil_production']),
        ];
    }
}

class LifelongProductionVolume extends Factor
{
    /**
     * @var ChildFactor[]
     */
    public array $child_factors;

    public function __construct(
        ?int $value = null, bool $selected = false, array $child_factors = []
    ) {
        $this->value = $value;
        $this->selected = $selected;
        $this->child_factors = [
            'lifelong_gas_production' => new ChildFactor(...$child_factors['lifelong_gas_production']),
            'lifelong_oil_production' => new ChildFactor(...$child_factors['lifelong_oil_production']),
        ];
    }
}

class SiteConsiderations extends Factor
{
    /**
     * @var ChildFactor[]
     */
    public array $child_factors;

    public function __construct(
        ?int $value = null, bool $selected = false, array $child_factors = []
    ) {
        $this->value = $value;
        $this->selected = $selected;
        $this->child_factors = [
            'historical_preservation_site' => new ChildFactor(...$child_factors['historical_preservation_site']),
            'home_use_gas_well' => new ChildFactor(...$child_factors['home_use_gas_well']),
            'post_plugging_land_use' => new ChildFactor(...$child_factors['post_plugging_land_use']),
            'surface_equipment_on_site' => new ChildFactor(...$child_factors['surface_equipment_on_site']),
        ];
    }
}

class SensistiveReceptors extends Factor
{
    /**
     * @var ChildFactor[]
     */
    public array $child_factors;

    public function __construct(
        ?int $value, bool $selected,
        array $child_factors
    ) {
        $this->value = $value;
        $this->selected = $selected;
        $this->child_factors = [
            'schools' => new ChildFactor(...$child_factors['schools']),
            'hospitals' => new ChildFactor(...$child_factors['hospitals']),
            'agriculture_area_nearby' => new ChildFactor(...$child_factors['agriculture_area_nearby']),
            'buildings_far' => new ChildFactor(...$child_factors['buildings_far']),
            'buildings_near' => new ChildFactor(...$child_factors['buildings_near']),
        ];
    }
}

class Environment extends Factor
{
    /**
     * @var ChildFactor[]
     */
    public array $child_factors;

    public function __construct(
        ?int $value, bool $selected,
        array $child_factors
    ) {
        $this->value = $value;
        $this->selected = $selected;
        $this->child_factors = [
            'water_source_nearby' => new ChildFactor(...$child_factors['water_source_nearby']),
            'known_soil_or_water_impact' => new ChildFactor(...$child_factors['known_soil_or_water_impact']),
            'fed_wetlands_near' => new ChildFactor(...$child_factors['fed_wetlands_near']),
            'fed_wetlands_far' => new ChildFactor(...$child_factors['fed_wetlands_far']),
            'state_wetlands_near' => new ChildFactor(...$child_factors['state_wetlands_near']),
            'state_wetlands_far' => new ChildFactor(...$child_factors['state_wetlands_far']),
        ];
    }
}

class EcologicalReceptors extends Factor
{
    /**
     * @var ChildFactor[]
     */
    public array $child_factors;

    public function __construct(
        ?int $value, bool $selected,
        array $child_factors
    ) {
        $this->value = $value;
        $this->selected = $selected;
        $this->child_factors = [
            'endangered_species_on_site' => new ChildFactor(...$child_factors['endangered_species_on_site']),
        ];
    }
}

class OtherLosses extends Factor
{
    /**
     * @var ChildFactor[]
     */
    public array $child_factors;

    public function __construct(
        ?int $value, bool $selected,
        array $child_factors
    ) {
        $this->value = $value;
        $this->selected = $selected;
        $this->child_factors = [
            'brine_leak' => new ChildFactor(...$child_factors['brine_leak']),
            'h2s_leak' => new ChildFactor(...$child_factors['h2s_leak']),
        ];
    }
}

class ImpactFactors
{
    public Losses $losses;

    public AnnProductionVolume $ann_production_volume;

    public FiveYearProductionVolume $five_year_production_volume;

    public LifelongProductionVolume $lifelong_production_volume;

    public SiteConsiderations $site_considerations;

    public EcologicalReceptors $ecological_receptors;

    public OtherLosses $other_losses;

    public Factor $well_age;

    public Factor $owner_well_count;

    public Factor $likely_to_be_orphaned;

    public Factor $in_tribal_land;

    public Factor $cost_of_plugging;

    public Factor $high_pressure_observed;

    public Factor $idle_status_duration;

    public Factor $number_of_mcws_nearby;

    public Factor $mechanical_integrity_test;

    public Factor $otherwise_incentivized_well;

    public Factor $well_integrity;

    public Factor $placeholder_one;

    public Factor $placeholder_two;

    public Factor $placeholder_three;

    public Factor $placeholder_four;

    public Factor $placeholder_five;

    public Factor $placeholder_six;

    public Factor $placeholder_seven;

    public Factor $placeholder_eight;

    public Factor $placeholder_nine;

    public Factor $placeholder_ten;

    public Factor $placeholder_eleven;

    public Factor $placeholder_twelve;

    public Factor $placeholder_thirteen;

    public Factor $placeholder_fourteen;

    public Factor $placeholder_fifteen;

    public Factor $placeholder_sixteen;

    public Factor $placeholder_seventeen;

    public Factor $placeholder_eighteen;

    public Factor $placeholder_nineteen;

    public Factor $placeholder_twenty;

    public SensistiveReceptors $sensitive_receptors;

    public Environment $environment;

    public function __construct(
        array $losses,
        array $ann_production_volume,
        array $five_year_production_volume,
        array $lifelong_production_volume,
        array $site_considerations,
        array $ecological_receptors,
        array $other_losses,
        array $well_age,
        array $owner_well_count,
        array $likely_to_be_orphaned,
        array $in_tribal_land,
        array $cost_of_plugging,
        array $high_pressure_observed,
        array $idle_status_duration,
        array $number_of_mcws_nearby,
        array $mechanical_integrity_test,
        array $otherwise_incentivized_well,
        array $well_integrity,
        array $placeholder_one,
        array $placeholder_two,
        array $placeholder_three,
        array $placeholder_four,
        array $placeholder_five,
        array $placeholder_six,
        array $placeholder_seven,
        array $placeholder_eight,
        array $placeholder_nine,
        array $placeholder_ten,
        array $placeholder_eleven,
        array $placeholder_twelve,
        array $placeholder_thirteen,
        array $placeholder_fourteen,
        array $placeholder_fifteen,
        array $placeholder_sixteen,
        array $placeholder_seventeen,
        array $placeholder_eighteen,
        array $placeholder_nineteen,
        array $placeholder_twenty,
        array $sensitive_receptors,
        array $environment
    ) {
        $this->losses = new Losses(...$losses);
        $this->ann_production_volume = new AnnProductionVolume(...$ann_production_volume);
        $this->five_year_production_volume = new FiveYearProductionVolume(...$five_year_production_volume);
        $this->lifelong_production_volume = new LifelongProductionVolume(...$lifelong_production_volume);
        $this->site_considerations = new SiteConsiderations(...$site_considerations);
        $this->ecological_receptors = new EcologicalReceptors(...$ecological_receptors);
        $this->other_losses = new OtherLosses(...$other_losses);
        $this->well_age = new Factor(...$well_age);
        $this->owner_well_count = new Factor(...$owner_well_count);
        $this->likely_to_be_orphaned = new Factor(...$likely_to_be_orphaned);
        $this->in_tribal_land = new Factor(...$in_tribal_land);
        $this->cost_of_plugging = new Factor(...$cost_of_plugging);
        $this->high_pressure_observed = new Factor(...$high_pressure_observed);
        $this->idle_status_duration = new Factor(...$idle_status_duration);
        $this->number_of_mcws_nearby = new Factor(...$number_of_mcws_nearby);
        $this->mechanical_integrity_test = new Factor(...$mechanical_integrity_test);
        $this->otherwise_incentivized_well = new Factor(...$otherwise_incentivized_well);
        $this->well_integrity = new Factor(...$well_integrity);
        $this->placeholder_one = new Factor(...$placeholder_one);
        $this->placeholder_two = new Factor(...$placeholder_two);
        $this->placeholder_three = new Factor(...$placeholder_three);
        $this->placeholder_four = new Factor(...$placeholder_four);
        $this->placeholder_five = new Factor(...$placeholder_five);
        $this->placeholder_six = new Factor(...$placeholder_six);
        $this->placeholder_seven = new Factor(...$placeholder_seven);
        $this->placeholder_eight = new Factor(...$placeholder_eight);
        $this->placeholder_nine = new Factor(...$placeholder_nine);
        $this->placeholder_ten = new Factor(...$placeholder_ten);
        $this->placeholder_eleven = new Factor(...$placeholder_eleven);
        $this->placeholder_twelve = new Factor(...$placeholder_twelve);
        $this->placeholder_thirteen = new Factor(...$placeholder_thirteen);
        $this->placeholder_fourteen = new Factor(...$placeholder_fourteen);
        $this->placeholder_fifteen = new Factor(...$placeholder_fifteen);
        $this->placeholder_sixteen = new Factor(...$placeholder_sixteen);
        $this->placeholder_seventeen = new Factor(...$placeholder_seventeen);
        $this->placeholder_eighteen = new Factor(...$placeholder_eighteen);
        $this->placeholder_nineteen = new Factor(...$placeholder_nineteen);
        $this->placeholder_twenty = new Factor(...$placeholder_twenty);
        $this->sensitive_receptors = new SensistiveReceptors(...$sensitive_receptors);
        $this->environment = new Environment(...$environment);
    }
}
