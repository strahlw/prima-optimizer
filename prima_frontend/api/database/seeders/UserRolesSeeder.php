<?php

namespace Database\Seeders;

use App\Enum\UserRoles;
use Illuminate\Database\Seeder;
use Spatie\Permission\Models\Role;

class UserRolesSeeder extends Seeder
{
    /**
     * Run the database seeds.
     */
    public function run(): void
    {
        Role::firstOrCreate(['name' => 'super-admin', 'label' => UserRoles::SUPER_ADMIN, 'guard_name' => 'api']);
        Role::firstOrCreate(['name' => 'org-admin', 'label' => UserRoles::ORGANIZATION_ADMIN, 'guard_name' => 'api']);
        Role::firstOrCreate(['name' => 'user', 'label' => UserRoles::USER, 'guard_name' => 'api']);
    }
}
