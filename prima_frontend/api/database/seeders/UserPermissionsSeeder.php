<?php

namespace Database\Seeders;

use Illuminate\Database\Seeder;
use Spatie\Permission\Models\Permission;
use Spatie\Permission\Models\Role;

class UserPermissionsSeeder extends Seeder
{
    /**
     * Run the database seeds.
     */
    public function run(): void
    {
        $superAdminRole = Role::where('name', 'super-admin')->first();
        $orgAdminRole = Role::where('name', 'org-admin')->first();
        $userRole = Role::where('name', 'user')->first();

        $addUserPermission = Permission::firstOrCreate(['name' => 'add-users', 'guard_name' => 'api']);
        $editUserPermission = Permission::firstOrCreate(['name' => 'edit-users', 'guard_name' => 'api']);
        $deleteUserPermission = Permission::firstOrCreate(['name' => 'delete-users', 'guard_name' => 'api']);
        $uploadDataPermission = Permission::firstOrCreate(['name' => 'upload-data', 'guard_name' => 'api']);
        $addOrgAdminPermission = Permission::firstOrCreate(['name' => 'add-org-admins', 'guard_name' => 'api']);
        $addSuperAdminPermission = Permission::firstOrCreate(['name' => 'add-super-admins', 'guard_name' => 'api']);
        $editSuperAdminPermission = Permission::firstOrCreate(['name' => 'edit-super-admins', 'guard_name' => 'api']);
        $deleteSuperAdminPermission = Permission::firstOrCreate(['name' => 'delete-super-admins', 'guard_name' => 'api']);
        $addOrgPermission = Permission::firstOrCreate(['name' => 'add-organizations', 'guard_name' => 'api']);
        $editOrgPermission = Permission::firstOrCreate(['name' => 'edit-organizations', 'guard_name' => 'api']);
        $deleteOrgPermission = Permission::firstOrCreate(['name' => 'delete-organizations', 'guard_name' => 'api']);
        $netlAdminPermission = Permission::firstOrCreate(['name' => 'netl-admin', 'guard_name' => 'api']);

        $superAdminRole->givePermissionTo(['add-users', 'edit-users', 'delete-users', 'upload-data', 'add-org-admins', 'edit-organizations']);
        $orgAdminRole->givePermissionTo(['add-users', 'edit-users', 'delete-users', 'upload-data']);
    }
}
