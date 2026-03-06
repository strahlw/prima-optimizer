<?php

namespace App\Models;

// use Illuminate\Contracts\Auth\MustVerifyEmail;

use App\Notifications\CreatePassword;
use Illuminate\Auth\Notifications\ResetPassword;
use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\HasMany;
use Illuminate\Database\Eloquent\SoftDeletes;
use Illuminate\Foundation\Auth\User as Authenticatable;
use Illuminate\Notifications\Notifiable;
use Laravel\Passport\HasApiTokens;
use Spatie\Permission\Models\Role;
use Spatie\Permission\Traits\HasPermissions;
use Spatie\Permission\Traits\HasRoles;

class User extends Authenticatable
{
    use HasApiTokens, HasFactory, HasPermissions, HasRoles, Notifiable, SoftDeletes;

    /**
     * The attributes that are mass assignable.
     *
     * @var array<int, string>
     */
    protected $fillable = [
        'first_name',
        'last_name',
        'email',
        'password',
        'organization_id',
        'account_verified',
        'show_disclaimer',
    ];

    /**
     * The attributes that should be hidden for serialization.
     *
     * @var array<int, string>
     */
    protected $hidden = [
        'password',
        'remember_token',
    ];

    /**
     * Get the attributes that should be cast.
     *
     * @return array<string, string>
     */
    protected function casts(): array
    {
        return [
            'email_verified_at' => 'datetime',
            'password' => 'hashed',
            'account_verified' => 'boolean',
        ];
    }

    public function organization(): BelongsTo
    {
        return $this->belongsTo(Organization::class);
    }

    public function getRoleNameAttribute(): string
    {
        // NOTE: Is there a reason to have multiple roles?
        return $this->roles->first()->name;
    }

    public function getPermissionNamesAttribute(): array
    {
        $rolePermissions = $this->roles->flatMap(fn (Role $role) => $role->permissions->map(fn ($permission) => $permission->name))->toArray();
        $userPermissions = $this->permissions->map(fn ($permission) => $permission->name)->toArray();

        return array_merge($rolePermissions, $userPermissions);
    }

    public function sendPasswordResetNotification($token)
    {
        if ($this->account_verified) {
            $this->notify(new ResetPassword($token));
        } else {
            $this->notify(new CreatePassword($token));
        }
    }

    public function getRoleIdAttribute(): int
    {
        return $this->roles->first()->id;
    }

    public function getNameAttribute(): string
    {
        return $this->first_name.' '.$this->last_name;
    }

    public function scenarios(): HasMany
    {
        return $this->hasMany(Scenario::class);
    }

    public function datasets(): HasMany
    {
        return $this->hasMany(Dataset::class, 'uploaded_by_id');
    }

    public function statusTasks(): HasMany
    {
        return $this->hasMany(Task::class, 'status_by_id');
    }

    public function statusScenarios(): HasMany
    {
        return $this->hasMany(Scenario::class, 'status_by_id');
    }
}
