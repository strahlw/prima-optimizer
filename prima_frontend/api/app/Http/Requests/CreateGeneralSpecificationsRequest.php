<?php

namespace App\Http\Requests;

use App\Enum\WellType;
use Illuminate\Auth\Access\AuthorizationException;
use Illuminate\Foundation\Http\FormRequest;
use Illuminate\Validation\Rule;

class CreateGeneralSpecificationsRequest extends FormRequest
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
        return [
            'general_specifications.additional_datasets' => 'nullable|array',
            'general_specifications.additional_datasets.*' => [
                'required',
                Rule::exists('datasets', 'id')->where(function ($query) {
                    $query->where('additional', true);
                }),
            ],
            'general_specifications.basic_data_checks' => 'required|boolean',
            'general_specifications.dataset_id' => 'required|int|exists:datasets,id',
            'general_specifications.handle_missing_depth' => ['required', 'string', Rule::in(['specify-value', 'remove-wells'])],
            'general_specifications.handle_missing_production' => ['required', 'string', Rule::in(['specify-value', 'remove-wells'])],
            'general_specifications.handle_missing_type' => ['required', 'string', Rule::in(['specify-value', 'remove-wells'])],
            'general_specifications.handle_missing_well_age' => ['required', 'string', Rule::in(['specify-value', 'remove-wells'])],
            'general_specifications.max_lifetime_gas_production' => ['nullable', 'numeric', 'min:0', 'max:1000000', function ($attribute, $value, $fail) {
                if (! is_null($this->input('general_specifications.min_lifetime_gas_production')) && $value <= $this->input('general_specifications.min_lifetime_gas_production')) {
                    $fail('The max lifetime gas production must be greater than the min lifetime gas production.');
                }
            }],
            'general_specifications.max_lifetime_oil_production' => ['nullable', 'numeric', 'min:0', 'max:1000000000', function ($attribute, $value, $fail) {
                if (! is_null($this->input('general_specifications.min_lifetime_oil_production')) && $value <= $this->input('general_specifications.min_lifetime_oil_production')) {
                    $fail('The max lifetime oil production must be greater than the min lifetime oil production.');
                }
            }],
            'general_specifications.min_lifetime_gas_production' => 'nullable|numeric|min:0|max:1000000',
            'general_specifications.min_lifetime_oil_production' => 'nullable|numeric|min:0|max:1000000000',
            'general_specifications.name' => [
                'required',
                'string',
                Rule::unique('scenarios', 'name')->where(function ($query) {
                    return $query->where('organization_id', request('general_specifications.organization_id'));
                }),
            ],
            'general_specifications.organization_id' => 'required|int|exists:organizations,id',
            'general_specifications.specified_age' => 'nullable|required_if:general_specifications.handle_missing_well_age,specify-value|numeric|min:0|max:300',
            'general_specifications.specified_annual_gas_production' => 'nullable|required_if:general_specifications.handle_missing_production,specify-value|decimal:0,2',
            'general_specifications.specified_annual_oil_production' => 'nullable|required_if:general_specifications.handle_missing_production,specify-value|decimal:0,2',
            'general_specifications.specified_depth' => 'nullable|required_if:general_specifications.handle_missing_depth,specify-value|numeric|min:0|max:20000',
            'general_specifications.specified_lifetime_gas_production' => 'nullable|required_if:general_specifications.handle_missing_production,specify-value|decimal:0,2',
            'general_specifications.specified_lifetime_oil_production' => 'nullable|required_if:general_specifications.handle_missing_production,specify-value|decimal:0,2',
            'general_specifications.specified_type' => 'nullable|required_if:general_specifications.handle_missing_type,specify-value|in:oil,gas',
            'general_specifications.well_type' => 'required|array',
            'general_specifications.use_lazy_constraints' => 'nullable|boolean',
            'general_specifications.well_type' => ['required', 'array'],
            'general_specifications.well_type.*' => ['required', Rule::in([WellType::OIL, WellType::GAS])],
        ];
    }

    public function messages(): array
    {
        return [
            'general_specifications.name.unique' => 'The scenario name must be unique within your organization.',
        ];
    }
}
