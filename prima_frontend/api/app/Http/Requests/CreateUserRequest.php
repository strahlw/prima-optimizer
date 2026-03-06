<?php

namespace App\Http\Requests;

use App\Enum\UserRoles;
use App\Models\User;
use Illuminate\Auth\Access\AuthorizationException;
use Illuminate\Foundation\Http\FormRequest;
use Spatie\Permission\Models\Role;

class CreateUserRequest extends FormRequest
{
    /**
     * Determine if the user is authorized to make this request.
     */
    public function authorize(): bool
    {
        return $this->user()->can('create', [User::class, $this]);
    }

    public function failedAuthorization()
    {
        throw new AuthorizationException('You are not authorized to create a user.', 403);
    }

    /**
     * Get the validation rules that apply to the request.
     *
     * @return array<string, \Illuminate\Contracts\Validation\ValidationRule|array<mixed>|string>
     */
    public function rules(): array
    {
        $superUserRoleId = Role::where('label', UserRoles::SUPER_ADMIN)->first()->id;

        if ($this->input('role_id') === $superUserRoleId) {
            $orgRules = 'nullable|exists:organizations,id';
        } else {
            $orgRules = 'required|exists:organizations,id';
        }

        return [
            'first_name' => 'required|string',
            'last_name' => 'required|string',
            'email' => 'required|email|unique:users,email',
            'role_id' => 'required|exists:roles,id',
            'organization_id' => $orgRules,
        ];
    }
}
