<?php

namespace App\Policies;

use App\Enum\UserRoles;
use App\Http\Requests\CreateUserRequest;
use App\Models\User;
use Spatie\Permission\Models\Role;

class UserPolicy
{
    protected function isSuperAdmin(User $user): bool
    {
        return $user->hasRole('super-admin');
    }

    protected function isOrgAdmin(User $user): bool
    {
        return $user->hasRole('org-admin');
    }

    protected function isManagingSelf(User $currentUser, User $targetUser): bool
    {
        return $currentUser->id === $targetUser->id;
    }

    public function create(User $currentUser, CreateUserRequest $request): bool
    {
        $role = Role::find($request->input('role_id'));

        if ($role && $role->label === UserRoles::SUPER_ADMIN) {
            // Only specific Super Admins can create super admins
            return $this->createSuper($currentUser);
        } elseif ($this->isSuperAdmin($currentUser)) {
            // Super admin can create other user types
            return true;
        }

        return $this->isOrgAdmin($currentUser) && $currentUser->organization_id === $request->input('organization_id');
    }

    public function createSuper(User $currentUser): bool
    {
        return $this->isSuperAdmin($currentUser) && $currentUser->hasPermissionTo('add-super-admins', 'api');
    }

    public function update(User $currentUser, User $userToUpdate, ?int $newRoleId = null): bool
    {
        if ($newRoleId !== $userToUpdate->role_id) {
            if ($currentUser->cannot('updateRole', [$userToUpdate, $newRoleId])) {
                return false;
            }
        }

        if ($currentUser->can('manageSuper', $userToUpdate)) {
            return true;
        }

        // Allow users to update themselves
        if ($currentUser->id === $userToUpdate->id) {
            return true;
        }

        return $currentUser->can('manage', $userToUpdate);
    }

    public function updateRole(User $currentUser, User $existingUser, $roleId): bool
    {
        $superRole = Role::where('label', UserRoles::SUPER_ADMIN)->first();

        // Allow super admins with manageSuper permission to update any roles
        // This also catching managing self.
        if ($currentUser->can('manageSuper', $existingUser)) {
            return true;
        }

        // Normal supers cannot elevate someone to super admin
        if ($this->isSuperAdmin($currentUser) && ! $this->isSuperAdmin($existingUser)) {
            if ($roleId !== $superRole->id) {
                return true;
            }

            return false;
        }

        return false;
    }

    public function manage(User $currentUser, User $userToManage): bool
    {
        return $this->isManagingSelf($currentUser, $userToManage) ||
               ($this->isSuperAdmin($currentUser) && ! $userToManage->hasRole('super-admin')) ||
               ($this->isOrgAdmin($currentUser) && $currentUser->organization_id === $userToManage->organization_id);
    }

    public function manageSuper(User $currentUser, User $userToManage): bool
    {
        // Allow self-management
        if ($this->isManagingSelf($currentUser, $userToManage)) {
            return true;
        }

        // Allow editing/deleting other super admins only if the user has both permissions
        return $this->isSuperAdmin($currentUser) &&
               $userToManage->hasRole('super-admin') &&
               $currentUser->hasPermissionTo('edit-super-admins', 'api') &&
               $currentUser->hasPermissionTo('delete-super-admins', 'api');
    }

    public function delete(User $currentUser, User $userToDelete): bool
    {
        return $this->manage($currentUser, $userToDelete) ||
               ($userToDelete->hasRole('super-admin') && $currentUser->can('manageSuper', $userToDelete));
    }
}
