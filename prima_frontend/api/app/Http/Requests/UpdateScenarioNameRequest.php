<?php

namespace App\Http\Requests;

use Illuminate\Auth\Access\AuthorizationException;
use Illuminate\Foundation\Http\FormRequest;
use Illuminate\Validation\Rule;

class UpdateScenarioNameRequest extends FormRequest
{
    /**
     * Determine if the user is authorized to make this request.
     */
    public function authorize(): bool
    {
        $scenario = $this->route('scenario');

        if ($this->user()->hasRole('super-admin')) {
            return true;
        }

        if ($this->user()->hasRole('org-admin') &&
            $this->user()->organization_id === (int) $scenario->organization_id) {
            return true;
        }

        if ($this->user()->id === (int) $scenario->user_id) {
            return true;
        }

        return false;
    }

    public function failedAuthorization()
    {
        throw new AuthorizationException("You are not authorized to update this scenario's name.", 403);
    }

    /**
     * Get the validation rules that apply to the request.
     *
     * @return array<string, \Illuminate\Contracts\Validation\ValidationRule|array<mixed>|string>
     */
    public function rules(): array
    {
        return [
            'name' => [
                'required',
                'string',
                Rule::unique('scenarios', 'name')
                    ->where(fn ($query) => $query->where('organization_id', $this->route('scenario')->organization_id)),
            ],
        ];
    }

    public function messages(): array
    {
        return [
            'name.unique' => 'The scenario name must be unique within your organization.',
        ];
    }
}
