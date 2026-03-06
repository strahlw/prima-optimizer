<?php

namespace App\Http\Requests;

use Illuminate\Contracts\Validation\Validator;
use Illuminate\Foundation\Http\FormRequest;
use Illuminate\Http\Exceptions\HttpResponseException;
use Illuminate\Support\Facades\Log;
use Illuminate\Validation\Rule;

class StoreDatasetRequest extends FormRequest
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
            'file' => 'required|file|mimes:csv,xlsx',
            'organization_id' => 'required|exists:organizations,id',
            'name' => [
                'required',
                'string',
                Rule::unique('datasets', 'name')->where('organization_id', $this->input('organization_id')),
            ],
            'additional' => 'required|boolean',
        ];
    }

    protected function failedValidation(Validator $validator)
    {
        // Log validation errors
        Log::error('Validation failed for request:', [
            'errors' => $validator->errors()->all(),
            'request_data' => $this->all(),
        ]);

        // You can throw an exception or customize the response
        throw new HttpResponseException(
            response()->json(['errors' => $validator->errors()], 422)
        );
    }

    public function messages(): array
    {
        return [
            'name.unique' => 'A dataset with this name already exists within this organization.',
        ];
    }

    protected function prepareForValidation()
    {
        $this->merge([
            'additional' => $this->input('additional') == 'true',
        ]);
    }
}
