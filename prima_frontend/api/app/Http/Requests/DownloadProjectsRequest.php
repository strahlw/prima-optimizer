<?php

namespace App\Http\Requests;

use Illuminate\Foundation\Http\FormRequest;

class DownloadProjectsRequest extends FormRequest
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
            'image' => 'required|image|mimes:png|max:4000',
            'project_id_color_map' => 'required|json',
            'project_id_color_map.*.id' => 'required|integer',
            'project_id_color_map.*.color' => 'required|string',
            'width' => 'required|integer',
            'height' => 'required|integer',
            'scenario_id' => 'required|integer|exists:scenarios,id',
        ];
    }

    public function prepareForValidation(): void
    {
        $this->merge([
            'scenario_id' => (int) $this->scenario_id,
        ]);
    }
}
