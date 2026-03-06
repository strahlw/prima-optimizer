<?php

namespace App\Http\Requests;

use Illuminate\Foundation\Http\FormRequest;

class SearchAvailableWellsRequest extends FormRequest
{
    /**
     * Determine if the user is authorized to make this request.
     */
    public function authorize(): bool
    {
        return true;
    }

    /**
     * Get the validation rules that apply to the request.
     *
     * @return array<string, \Illuminate\Contracts\Validation\ValidationRule|array<mixed>|string>
     */
    public function rules(): array
    {
        return [
            'query' => ['required', 'string'],
            'included_well_ids' => ['array'],
            'inactive_project_ids' => ['array'],
            'excluded_dataset_well_ids' => ['array'],
            'reassigned_well_ids' => ['array'],
            'well_types' => ['array'],
        ];
    }
}
