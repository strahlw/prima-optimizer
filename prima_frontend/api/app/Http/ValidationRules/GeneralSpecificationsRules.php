<?php

namespace App\Http\ValidationRules;

use App\Enum\WellType;
use Illuminate\Validation\Rule;

class GeneralSpecificationsRules
{
    public static function rules(array $input, array $overrides = []): array
    {
        $rules = [
            'general_specifications.absolute_gap' => 'nullable|decimal:0,2|min:0|max:1000000',
            'general_specifications.additional_datasets' => 'nullable|array',
            'general_specifications.additional_datasets.*' => [
                'required',
                Rule::exists('datasets', 'id')->where(function ($query) {
                    $query->where('additional', true);
                }),
            ],
            'general_specifications.basic_data_checks' => 'required|boolean',
            'general_specifications.budget' => 'required|numeric|min:120000',
            'general_specifications.cost_efficiency' => 'required|decimal:0,2|between:0,1',
            'general_specifications.dataset_id' => 'required|int|exists:datasets,id',
            'general_specifications.deep_gas_well_cost' => 'required|numeric',
            'general_specifications.deep_oil_well_cost' => 'required|numeric',
            'general_specifications.handle_missing_depth' => ['required', 'string', Rule::in(['specify-value', 'remove-wells'])],
            'general_specifications.handle_missing_production' => ['required', 'string', Rule::in(['specify-value', 'remove-wells'])],
            'general_specifications.handle_missing_type' => ['required', 'string', Rule::in(['specify-value', 'remove-wells'])],
            'general_specifications.handle_missing_well_age' => ['required', 'string', Rule::in(['specify-value', 'remove-wells'])],
            'general_specifications.max_distance_between_project_wells' => 'nullable|decimal:0,2|min:0|max:500',
            'general_specifications.max_lifetime_gas_production' => ['nullable', 'numeric', 'min:0', 'max:1000000', function ($attribute, $value, $fail) use ($input) {
                if (! is_null($input['general_specifications']['min_lifetime_gas_production']) && $value <= $input['general_specifications']['min_lifetime_gas_production']) {
                    $fail('The max lifetime gas production must be greater than the min lifetime gas production.');
                }
            }],
            'general_specifications.max_lifetime_oil_production' => ['nullable', 'numeric', 'min:0', 'max:1000000000', function ($attribute, $value, $fail) use ($input) {
                if (! is_null($input['general_specifications']['min_lifetime_oil_production']) && $value <= $input['general_specifications']['min_lifetime_oil_production']) {
                    $fail('The max lifetime oil production must be greater than the min lifetime oil production.');
                }
            }],
            'general_specifications.max_wells_in_project' => 'nullable|numeric|gt:general_specifications.min_wells_in_project',
            'general_specifications.min_lifetime_gas_production' => 'nullable|numeric|min:0|max:1000000',
            'general_specifications.min_lifetime_oil_production' => 'nullable|numeric|min:0|max:1000000000',
            'general_specifications.min_wells_in_project' => 'nullable|numeric|min:1|max:100',
            'general_specifications.model' => 'nullable|in:impact-and-efficiency,impact',
            'general_specifications.name' => [
                'required',
                'string',
                Rule::unique('scenarios', 'name')->where(function ($query) use ($input) {
                    return $query->where('organization_id', $input['general_specifications']['organization_id']);
                }),
            ],
            'general_specifications.organization_id' => 'required|int|exists:organizations,id',
            'general_specifications.max_wells_per_owner' => 'nullable|int|min:0|max:10000',
            'general_specifications.relative_gap' => 'nullable|decimal:0,6|min:0|max:1',
            'general_specifications.shallow_gas_well_cost' => 'required|numeric',
            'general_specifications.shallow_oil_well_cost' => 'required|numeric',
            'general_specifications.solver_time' => 'nullable|numeric',
            'general_specifications.specified_age' => 'nullable|required_if:general_specifications.handle_missing_well_age,specify-value|numeric|min:0|max:300',
            'general_specifications.specified_annual_gas_production' => 'nullable|required_if:general_specifications.handle_missing_production,specify-value|decimal:0,2',
            'general_specifications.specified_annual_oil_production' => 'nullable|required_if:general_specifications.handle_missing_production,specify-value|decimal:0,2',
            'general_specifications.specified_depth' => 'nullable|required_if:general_specifications.handle_missing_depth,specify-value|numeric|min:0|max:20000',
            'general_specifications.specified_lifetime_gas_production' => 'nullable|required_if:general_specifications.handle_missing_production,specify-value|decimal:0,2',
            'general_specifications.specified_lifetime_oil_production' => 'nullable|required_if:general_specifications.handle_missing_production,specify-value|decimal:0,2',
            'general_specifications.specified_type' => 'nullable|required_if:general_specifications.handle_missing_type,specify-value|in:oil,gas',
            'general_specifications.well_type' => 'required|array',
            'general_specifications.use_lazy_constraints' => 'nullable|boolean',
            'general_specifications.well_depth_limit' => 'nullable|numeric|min:0|max:50000',
            'general_specifications.well_type' => ['required', 'array'],
            'general_specifications.well_type.*' => ['required', Rule::in([WellType::OIL, WellType::GAS])],
        ];

        return array_merge($rules, $overrides);
    }
}
