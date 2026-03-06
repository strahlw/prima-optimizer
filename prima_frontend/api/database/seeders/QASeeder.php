<?php

namespace Database\Seeders;

use App\Models\Organization;
use App\Models\User;
use Illuminate\Database\Seeder;
use Illuminate\Support\Str;
use Spatie\Permission\Models\Role;

class QASeeder extends Seeder
{
    protected array $names = ['karen'];

    /**
     * Run the database seeds.
     */
    public function run(): void
    {
        $superAdmins = collect();
        $orgAdmins = collect();
        $users = collect();

        Organization::get()->each(function (Organization $organization) use (&$superAdmins, &$orgAdmins, &$users) {
            foreach ($this->names as $name) {
                $superAdmin = User::withTrashed()->firstOrCreate(['email' => "$name+super@email.com"], [
                    'first_name' => Str::ucfirst($name),
                    'last_name' => 'SuperAdmin',
                    'email' => "$name+super@email.com",
                    'password' => bcrypt('password'),
                    'account_verified' => true,
                ]);

                $orgAdmin = User::withTrashed()->firstOrCreate(['email' => "$name+{$organization->key}admin@email.com"], [
                    'first_name' => Str::ucfirst($name),
                    'last_name' => "{$organization->key}Admin",
                    'email' => "$name+{$organization->key}admin@email.com",
                    'password' => bcrypt('password'),
                    'organization_id' => $organization->id,
                    'account_verified' => true,
                ]);

                $user = User::withTrashed()->firstOrCreate(['email' => "$name+{$organization->key}user@email.com"], [
                    'first_name' => Str::ucfirst($name),
                    'last_name' => "{$organization->key}User",
                    'email' => "$name+{$organization->key}user@email.com",
                    'password' => bcrypt('password'),
                    'organization_id' => $organization->id,
                    'account_verified' => true,
                ]);

                $superAdmins->push($superAdmin);
                $orgAdmins->push($orgAdmin);
                $users->push($user);
            }
        });

        $superAdmins->each(function ($superAdmin) {
            $superAdmin->assignRole(Role::where('name', 'super-admin')->first());
        });

        $orgAdmins->each(function ($orgAdmin) {
            $orgAdmin->assignRole(Role::where('name', 'org-admin')->first());
        });

        $users->each(function ($user) {
            $user->assignRole(Role::where('name', 'user')->first());
        });
    }
}
