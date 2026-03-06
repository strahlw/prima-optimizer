<?php

namespace App\Http\Controllers;

use App\Http\Requests\CreateUserRequest;
use App\Http\Requests\DestroyUserRequest;
use App\Http\Requests\UpdateUserRequest;
use App\Models\Organization;
use App\Models\User;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Hash;
use Illuminate\Support\Facades\Log;
use Illuminate\Support\Facades\Password;
use Illuminate\Support\Str;
use Spatie\Permission\Models\Role;

class UserController extends Controller
{
    /**
     * Display a listing of the resource.
     */
    public function index() {}

    public function getSuperAdmins(Request $request)
    {
        if (! $request->user()->hasRole('super-admin')) {
            return response()->json(['message' => 'Unauthorized to view super admins'], 403);
        }

        return response()->json(['users' => User::role('super-admin')->get()->map(fn (User $user) => $user->append(['role_id', 'roleName']))]);
    }

    public function getOrganizationUsers(Organization $organization)
    {
        return response()->json(['users' => $organization->users->map(fn (User $user) => $user->append(['role_id', 'roleName']))]);
    }

    /**
     * Store a newly created resource in storage.
     */
    public function store(CreateUserRequest $request)
    {
        DB::beginTransaction();

        try {
            // Customize the broker to allow for 24 hour reset expiration.
            $broker = Password::broker('users_welcome');

            $validated = $request->validated();

            $newUser = User::create([
                'first_name' => $validated['first_name'],
                'last_name' => $validated['last_name'],
                'email' => $validated['email'],
                'organization_id' => $validated['organization_id'] ?? null,
                'account_verified' => false,
                'password' => Hash::make(Str::random(300)),
            ]);

            $newUser->assignRole($validated['role_id']);

            $status = $broker->sendResetLink(
                $request->only('email'),
            );

            DB::commit();

            return $status === Password::RESET_LINK_SENT
                        ? response()->json(['message' => 'User created successfully', 'user' => $newUser->append('role_id')])
                        : back()->withErrors(['email' => __($status)]);
        } catch (\Exception $e) {
            Log::error($e);
            DB::rollback();

            return response()->json(['message' => 'Failed to create user'], 500);
        }
    }

    /**
     * Update the specified resource in storage.
     */
    public function update(UpdateUserRequest $request, User $user)
    {
        DB::beginTransaction();

        try {
            $validated = $request->validated();
            $user->update([
                'first_name' => $validated['first_name'],
                'last_name' => $validated['last_name'],
            ]);

            if (! $user->hasRole(Role::find($validated['role_id']))) {
                $user->syncRoles([]);
                $user->assignRole($validated['role_id']);
            }

            DB::commit();

            return response()->json(['message' => 'User updated successfully', 'user' => $user->append(['role_id', 'role_name'])]);
        } catch (\Exception $e) {
            Log::error($e);
            DB::rollback();

            return response()->json(['message' => 'Failed to update user'], 500);
        }
    }

    /**
     * Remove the specified resource from storage.
     */
    public function destroy(DestroyUserRequest $request, User $user)
    {
        $role = Role::find($user->role_id);

        if (! $role) {
            return response()->json(['message' => 'Role not found'], 404);
        }

        if ($user->hasRole('org-admin')) {
            $otherOrgUsers = User::where('organization_id', $user->organization_id)
                ->where('id', '!=', $user->id)
                ->get()->filter(fn (User $user) => $user->hasRole('org-admin'));

            if ($otherOrgUsers->isEmpty()) {
                return response()->json(['message' => 'Cannot delete the last admin in an organization'], 403);
            }
        }

        try {
            $user->delete();

            return response()->json(['message' => 'User deleted successfully', 'id' => $user->id]);
        } catch (\Exception $e) {
            Log::error($e);

            return response()->json(['message' => 'Failed to delete user'], 500);
        }
    }
}
