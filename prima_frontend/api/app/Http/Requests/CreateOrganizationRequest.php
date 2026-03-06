<?php

namespace App\Http\Requests;

use App\Models\Organization;
use Illuminate\Auth\Access\AuthorizationException;
use Illuminate\Foundation\Http\FormRequest;
use Illuminate\Support\Facades\Gate;

class CreateOrganizationRequest extends FormRequest
{
    /**
     * Determine if the user is authorized to make this request.
     */
    public function authorize(): bool
    {
        return Gate::allows('create', Organization::class);
    }

    public function failedAuthorization()
    {
        throw new AuthorizationException('You are not authorized to create an organization.', 403);
    }

    /**
     * Get the validation rules that apply to the request.
     *
     * @return array<string, \Illuminate\Contracts\Validation\ValidationRule|array<mixed>|string>
     */
    public function rules(): array
    {
        return [
            'key' => 'required|string|unique:organizations,key',
            'name' => 'required|string',
            'logo' => 'nullable|file|mimes:jpeg,png,jpg,gif,svg|max:2048',
            'available_funding' => 'nullable|numeric|min:0',
            'well_count' => 'nullable|integer|min:0',
            'pa_target' => 'nullable|integer|min:0',
            'longitude' => 'required|numeric',
            'latitude' => 'required|numeric',
        ];
    }
}
