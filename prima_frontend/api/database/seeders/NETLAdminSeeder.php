<?php

namespace Database\Seeders;

use App\Models\Organization;
use App\Models\User;
use Illuminate\Database\Seeder;
use Illuminate\Support\Str;
use Spatie\Permission\Models\Permission;
use Spatie\Permission\Models\Role;

class NETLAdminSeeder extends Seeder
{
    /**
     * Run the database seeds. Create users for the NETL team.
     */
    public function run(): void
    {
        $netlDomainAdmins = collect([]);

        // Higher order NETL Super Admins
        $markus = User::withTrashed()->firstOrCreate(['email' => 'Markus.Drouven@netl.doe.gov'], [
            'first_name' => 'Markus',
            'last_name' => 'Drouven',
            'email' => 'Markus.Drouven@netl.doe.gov',
            'password' => bcrypt(Str::random(32)),
            'account_verified' => false,
        ]);

        $colton = User::withTrashed()->firstOrCreate(['email' => 'cmcgee_primo@keylogic.com'], [
            'first_name' => 'Colton',
            'last_name' => 'McGee',
            'email' => 'cmcgee_primo@keylogic.com',
            'password' => bcrypt(Str::random(32)),
            'account_verified' => false,
        ]);

        $harry = User::withTrashed()->firstOrCreate(['email' => 'Hmckinney_primo@keylogic.com'], [
            'first_name' => 'Harry',
            'last_name' => 'McKinney',
            'email' => 'Hmckinney_primo@keylogic.com',
            'password' => bcrypt(Str::random(32)),
            'account_verified' => false,
        ]);

        $jeremy = User::withTrashed()->firstOrCreate(['email' => 'jeremy.langevin+NETL@troyweb.com'], [
            'first_name' => 'Jeremy',
            'last_name' => 'NETLAdmin',
            'email' => 'jeremy.langevin+NETL@troyweb.com',
            'password' => bcrypt(Str::random(32)),
            'account_verified' => false,
        ]);

        $netlDomainAdmins->push($markus);
        $netlDomainAdmins->push($colton);
        $netlDomainAdmins->push($harry);
        $netlDomainAdmins->push($jeremy);

        if (config('app.env') === 'qa') {
            $karen = User::withTrashed()->firstOrCreate(['email' => 'karen+NETLAdmin@troyweb.com'], [
                'first_name' => 'Karen',
                'last_name' => 'NETL Admin',
                'email' => 'karen.grodnick+NETLAdmin@troyweb.com',
                'password' => 'password',
                'account_verified' => false,
            ]);

            $netlDomainAdmins->push($karen);
        }

        $org = Organization::where('key', 'NETL')->first();

        // NETL Organization Admins
        $will = User::withTrashed()->firstOrCreate(['email' => 'William.Strahl@netl.doe.gov'], [
            'first_name' => 'William',
            'last_name' => 'Strahl',
            'email' => 'William.Strahl@netl.doe.gov',
            'password' => bcrypt(Str::random(32)),
            'account_verified' => false,
            'organization_id' => $org->id,
        ]);

        $tyler = User::withTrashed()->firstOrCreate(['email' => 'Tyler.Jaffe@netl.doe.gov'], [
            'first_name' => 'Tyler',
            'last_name' => 'Jaffe',
            'email' => 'Tyler.Jaffe@netl.doe.gov',
            'password' => bcrypt(Str::random(32)),
            'account_verified' => false,
            'organization_id' => $org->id,
        ]);

        $dev = User::withTrashed()->firstOrCreate(['email' => 'Dev.Kakkad@netl.doe.gov'], [
            'first_name' => 'Dev',
            'last_name' => 'Kakkad',
            'email' => 'Dev.Kakkad@netl.doe.gov',
            'password' => bcrypt(Str::random(32)),
            'account_verified' => false,
            'organization_id' => $org->id,
        ]);

        $ruonan = User::withTrashed()->firstOrCreate(['email' => 'ruonan.li@netl.doe.gov'], [
            'first_name' => 'Ruonan',
            'last_name' => 'Li',
            'email' => 'ruonan.li@netl.doe.gov',
            'password' => bcrypt(Str::random(32)),
            'account_verified' => false,
            'organization_id' => $org->id,
        ]);

        $sangbum = User::withTrashed()->firstOrCreate(['email' => 'Sangbum.Lee@netl.doe.gov'], [
            'first_name' => 'Sangbum',
            'last_name' => 'Lee',
            'email' => 'Sangbum.Lee@netl.doe.gov',
            'password' => bcrypt(Str::random(32)),
            'account_verified' => false,
            'organization_id' => $org->id,
        ]);

        $miguel = User::withTrashed()->firstOrCreate(['email' => 'Miguel.Zamarripa-Perez@netl.doe.gov'], [
            'first_name' => 'Miguel',
            'last_name' => 'Zamarripa',
            'email' => 'Miguel.Zamarripa-Perez@netl.doe.gov',
            'password' => bcrypt(Str::random(32)),
            'account_verified' => false,
            'organization_id' => $org->id,
        ]);

        $yash = User::withTrashed()->firstOrCreate(['email' => 'yash.puranik@aimpointdigital.com'], [
            'first_name' => 'Yash',
            'last_name' => 'Puranik',
            'email' => 'yash.puranik@aimpointdigital.com',
            'password' => bcrypt(Str::random(32)),
            'account_verified' => false,
        ]);

        // As of 09/05/2024 Harry and Colton have not been added to the IP allow list
        $colton = User::withTrashed()->firstOrCreate(['email' => 'colton.mcgee@keylogic.com'], [
            'first_name' => 'Colton',
            'last_name' => 'McGee',
            'email' => 'colton.mcgee@keylogic.com',
            'password' => bcrypt(Str::random(32)),
            'account_verified' => false,
        ]);

        $harry = User::withTrashed()->firstOrCreate(['email' => 'harry.mckinney@keylogic.com'], [
            'first_name' => 'Harry',
            'last_name' => 'McKinney',
            'email' => 'harry.mckinney@keylogic.com',
            'password' => bcrypt(Str::random(32)),
            'account_verified' => false,
            'organization_id' => $org->id,
        ]);

        $superAdminRole = Role::where('name', 'super-admin')->first();
        $addSuperAdminPermission = Permission::where('name', 'add-super-admins')->first();
        $editSuperAdminPermission = Permission::where('name', 'edit-super-admins')->first();
        $deleteSuperAdminPermission = Permission::where('name', 'delete-super-admins')->first();
        $addOrgPermission = Permission::where('name', 'add-organizations')->first();
        $deleteOrgPermission = Permission::where('name', 'delete-organizations')->first();
        $netlAdminPermissions = Permission::where('name', 'netl-admin')->first();

        $orgAdminRole = Role::where('name', 'org-admin')->first();

        $permissionsToAdd = [
            $addSuperAdminPermission,
            $editSuperAdminPermission,
            $deleteSuperAdminPermission,
            $addOrgPermission,
            $deleteOrgPermission,
            $netlAdminPermissions,
        ];

        $netlDomainAdmins->each(function ($user) use ($superAdminRole, $permissionsToAdd) {
            $user->assignRole($superAdminRole);
            $user->givePermissionTo($permissionsToAdd);
        });

        collect([$ruonan, $sangbum, $miguel, $yash, $colton, $harry, $tyler, $dev, $will])->each(function ($user) use ($orgAdminRole) {
            $user->assignRole($orgAdminRole);
        });
    }
}
