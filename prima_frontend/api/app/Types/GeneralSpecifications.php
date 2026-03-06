<?php

namespace App\Types;

class GeneralSpecifications
{
    public int $organization_id;

    public int $dataset_id;

    public ?array $additional_datasets;

    public array $well_type;

    public string $name;

    public ?float $budget;

    public ?int $max_wells_per_owner;

    public ?float $absolute_gap;

    public bool $basic_data_checks;

    public ?float $cost_efficiency;

    public ?float $deep_gas_well_cost;

    public ?float $deep_oil_well_cost;

    public string $handle_missing_depth;

    public string $handle_missing_production;

    public string $handle_missing_type;

    public string $handle_missing_well_age;

    public ?float $max_distance_between_project_wells;

    public ?float $max_lifetime_gas_production;

    public ?float $max_lifetime_oil_production;

    public ?int $max_wells_in_project;

    public ?float $min_lifetime_gas_production;

    public ?float $min_lifetime_oil_production;

    public ?int $min_wells_in_project;

    public ?string $model;

    public ?float $relative_gap;

    public ?float $shallow_gas_well_cost;

    public ?float $shallow_oil_well_cost;

    public ?float $solver_time;

    public ?float $specified_age;

    public ?float $specified_annual_gas_production;

    public ?float $specified_annual_oil_production;

    public ?float $specified_depth;

    public ?float $specified_lifetime_gas_production;

    public ?float $specified_lifetime_oil_production;

    public ?string $specified_type;

    public ?bool $use_lazy_constraints;

    public ?float $well_depth_limit;

    public function __construct(
        int $organization_id = 0,
        int $dataset_id = 0,
        ?array $additional_datasets = [],
        array $well_type = [],
        string $name = '',
        float $budget = 0,
        ?int $max_wells_per_owner = null,
        ?float $absolute_gap = null,
        bool $basic_data_checks = false,
        float $cost_efficiency = 0.9,
        ?float $deep_gas_well_cost = 0,
        ?float $deep_oil_well_cost = 0,
        string $handle_missing_depth = '',
        string $handle_missing_production = '',
        string $handle_missing_type = '',
        string $handle_missing_well_age = '',
        ?float $max_distance_between_project_wells = null,
        ?float $max_lifetime_gas_production = null,
        ?float $max_lifetime_oil_production = null,
        ?int $max_wells_in_project = null,
        ?float $min_lifetime_gas_production = null,
        ?float $min_lifetime_oil_production = null,
        ?int $min_wells_in_project = null,
        ?string $model = null,
        ?float $relative_gap = null,
        ?float $shallow_gas_well_cost = 0,
        ?float $shallow_oil_well_cost = 0,
        ?float $solver_time = null,
        ?float $specified_age = null,
        ?float $specified_annual_gas_production = null,
        ?float $specified_annual_oil_production = null,
        ?float $specified_depth = null,
        ?float $specified_lifetime_gas_production = null,
        ?float $specified_lifetime_oil_production = null,
        ?string $specified_type = null,
        ?bool $use_lazy_constraints = null,
        ?float $well_depth_limit = null
    ) {
        $this->organization_id = $organization_id;
        $this->dataset_id = $dataset_id;
        $this->additional_datasets = $additional_datasets;
        $this->well_type = $well_type;
        $this->name = $name;
        $this->budget = $budget;
        $this->max_wells_per_owner = $max_wells_per_owner;
        $this->absolute_gap = $absolute_gap;
        $this->basic_data_checks = $basic_data_checks;
        $this->cost_efficiency = $cost_efficiency;
        $this->deep_gas_well_cost = $deep_gas_well_cost;
        $this->deep_oil_well_cost = $deep_oil_well_cost;
        $this->handle_missing_depth = $handle_missing_depth;
        $this->handle_missing_production = $handle_missing_production;
        $this->handle_missing_type = $handle_missing_type;
        $this->handle_missing_well_age = $handle_missing_well_age;
        $this->max_distance_between_project_wells = $max_distance_between_project_wells;
        $this->max_lifetime_gas_production = $max_lifetime_gas_production == 0 ? null : $max_lifetime_gas_production;
        $this->max_lifetime_oil_production = $max_lifetime_oil_production == 0 ? null : $max_lifetime_oil_production;
        $this->max_wells_in_project = $max_wells_in_project;
        $this->min_lifetime_gas_production = $min_lifetime_gas_production == 0 ? null : $min_lifetime_gas_production;
        $this->min_lifetime_oil_production = $min_lifetime_oil_production == 0 ? null : $min_lifetime_oil_production;
        $this->min_wells_in_project = $min_wells_in_project;
        $this->model = $model;
        $this->relative_gap = $relative_gap;
        $this->shallow_gas_well_cost = $shallow_gas_well_cost;
        $this->shallow_oil_well_cost = $shallow_oil_well_cost;
        $this->solver_time = $solver_time;
        $this->specified_age = $specified_age;
        $this->specified_annual_gas_production = $specified_annual_gas_production;
        $this->specified_annual_oil_production = $specified_annual_oil_production;
        $this->specified_depth = $specified_depth;
        $this->specified_lifetime_gas_production = $specified_lifetime_gas_production;
        $this->specified_lifetime_oil_production = $specified_lifetime_oil_production;
        $this->specified_type = $specified_type;
        $this->use_lazy_constraints = $use_lazy_constraints;
        $this->well_depth_limit = $well_depth_limit;
    }
}
