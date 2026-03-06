<?php

namespace App\Policies;

use App\Models\Scenario;
use App\Models\User;

class ScenarioPolicy
{
    /**
     * Determine whether the user can view any models.
     */
    public function viewAny(User $user): bool
    {
        //
    }

    /**
     * Determine whether the user can view the model.
     */
    public function view(User $user, Scenario $scenario): bool
    {
        //
    }

    /**
     * Determine whether the user can create models.
     */
    public function create(User $user): bool
    {
        //
    }

    /**
     * Determine whether the user can update the model.
     */
    public function update(User $user, Scenario $scenario): bool
    {
        if ($user->hasRole('super-admin')) {
            return true;
        }

        if ($user->id === $scenario->user->id) {
            return true;
        }

        if ($user->organization_id === $scenario->organization->id && $user->hasRole('org-admin')) {
            return true;
        }

        return false;
    }

    /**
     * Determine whether the user can delete the model.
     */
    public function delete(User $user, Scenario $scenario): bool
    {
        //
    }

    /**
     * Determine whether the user can restore the model.
     */
    public function restore(User $user, Scenario $scenario): bool
    {
        //
    }

    /**
     * Determine whether the user can permanently delete the model.
     */
    public function forceDelete(User $user, Scenario $scenario): bool
    {
        //
    }
}
