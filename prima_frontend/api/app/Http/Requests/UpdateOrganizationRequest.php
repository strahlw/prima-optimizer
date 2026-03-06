<?php

namespace App\Http\Requests;

use App\Models\Organization;
use Illuminate\Auth\Access\AuthorizationException;
use Illuminate\Foundation\Http\FormRequest;
use Illuminate\Support\Facades\Gate;
use Illuminate\Validation\Rule;

class UpdateOrganizationRequest extends FormRequest
{
    /**
     * Determine if the user is authorized to make this request.
     */
    public function authorize(): bool
    {
        return Gate::allows('update', $this->route('organization'));
    }

    public function failedAuthorization()
    {
        throw new AuthorizationException('You are not authorized to update this organization.', 403);
    }

    /**
     * Get the validation rules that apply to the request.
     *
     * @return array<string, \Illuminate\Contracts\Validation\ValidationRule|array<mixed>|string>
     */
    public function rules(): array
    {
        $organizationId = $this->route('organization');
        $organization = Organization::findOrFail($this->route('organization')->id);

        return [
            'key' => ['required', 'string', Rule::unique('organizations')->ignore($organizationId)],
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
