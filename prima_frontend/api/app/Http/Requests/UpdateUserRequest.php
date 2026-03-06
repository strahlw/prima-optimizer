<?php

namespace App\Http\Requests;

use Illuminate\Auth\Access\AuthorizationException;
use Illuminate\Foundation\Http\FormRequest;

class UpdateUserRequest extends FormRequest
{
    /**
     * Determine if the user is authorized to make this request.
     */
    public function authorize(): bool
    {
        if ($this->user()->can('update', [$this->route('user'), $this->input('role_id')])) {
            return true;
        }

        return false;
    }

    public function failedAuthorization()
    {
        throw new AuthorizationException('You are not authorized to edit this User.', 403);
    }

    /**
     * Get the validation rules that apply to the request.
     *
     * @return array<string, \Illuminate\Contracts\Validation\ValidationRule|array<mixed>|string>
     */
    public function rules(): array
    {
        return [
            'first_name' => 'required|string',
            'last_name' => 'required|string',
            'role_id' => 'required|exists:roles,id',
        ];
    }
}
