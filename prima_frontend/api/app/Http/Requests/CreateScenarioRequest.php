<?php

namespace App\Http\Requests;

use App\Enum\ScenarioType;
use App\Http\ValidationRules\EfficiencyFactorRules;
use App\Http\ValidationRules\GeneralSpecificationsRules;
use App\Http\ValidationRules\ImpactFactorRules;
use Illuminate\Auth\Access\AuthorizationException;
use Illuminate\Foundation\Http\FormRequest;
use Illuminate\Validation\Rule;

class CreateScenarioRequest extends FormRequest
{
    /**
     * Determine if the user is authorized to make this request.
     */
    public function authorize(): bool
    {
        if ($this->user()->hasRole('super-admin')) {
            return true;
        }

        if ($this->user()->organization_id === (int) $this->input('general_specifications.organization_id')) {
            return true;
        }

        return false;
    }

    public function failedAuthorization()
    {
        throw new AuthorizationException('You are not authorized to create this scenario.', 403);
    }

    /**
     * Get the validation rules that apply to the request.
     *
     * @return array<string, \Illuminate\Contracts\Validation\ValidationRule|array<mixed>|string>
     */
    public function rules(): array
    {
        $generalSpecificationOverrides = [];
        $impactFactorOverrides = [];
        $efficiencyFactorOverrides = [];

        $rules = [
            'use_cases.cases' => 'required|array',
            'use_cases.cases.*' => [
                'required',
                Rule::in(ScenarioType::values()),
            ],
            'copy_parent_id' => 'sometimes|nullable|integer|exists:scenarios,id',
        ];

        $useCases = $this->input('use_cases.cases', []);
        $useCaseCount = count($useCases);

        if ($useCaseCount === 1 && in_array(ScenarioType::WELL_RANKING, $useCases)) {
            $rules += GeneralSpecificationsRules::rules($this->all(), self::$rankOnlyGenerateSpecificationOverrides);
            $rules += ImpactFactorRules::rules($impactFactorOverrides);

            return $rules;
        }

        if ($useCaseCount === 1 && in_array(ScenarioType::PROJECT_RECOMMENDATIONS, $useCases)) {
            $rules += GeneralSpecificationsRules::rules($this->all());
            $rules += EfficiencyFactorRules::rules();

            return $rules;
        }

        $rules += GeneralSpecificationsRules::rules($this->all(), $generalSpecificationOverrides);
        $rules += ImpactFactorRules::rules($impactFactorOverrides);
        $rules += EfficiencyFactorRules::rules($efficiencyFactorOverrides);

        return $rules;
    }

    public function messages(): array
    {
        return [
            'general_specifications.name.unique' => 'The scenario name must be unique within your organization.',
        ];
    }

    private static array $rankOnlyGenerateSpecificationOverrides = [
        'general_specifications.budget' => 'nullable',
        'general_specifications.shallow_gas_well_cost' => 'nullable',
        'general_specifications.shallow_oil_well_cost' => 'nullable',
        'general_specifications.deep_gas_well_cost' => 'nullable',
        'general_specifications.deep_oil_well_cost' => 'nullable',
    ];
}
