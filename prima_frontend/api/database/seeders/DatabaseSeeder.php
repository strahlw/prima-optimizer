<?php

namespace Database\Seeders;

use App\Models\Scenario;
// use Illuminate\Database\Console\Seeds\WithoutModelEvents;
use Illuminate\Database\Seeder;

class DatabaseSeeder extends Seeder
{
    /**
     * Seed the application's database.
     */
    public function run(): void
    {
        $this->call(UserRolesSeeder::class);
        $this->call(UserPermissionsSeeder::class);
        $this->call(OrganizationSeeder::class);
        $this->call(DatasetImportColumnPhase3Seeder::class);

        if (config('app.env') === 'local' || config('app.env') === 'qa') {
            $this->call(UserSeeder::class);

            // Temporarily limiting QA access
            if (config('app.env') === 'local') {
                $this->call(QASeeder::class);
            }

            if (Scenario::count() === 0 && config('app.env') === 'local') {
                $this->call(ScenarioSeeder::class);
            }

            $this->call(OauthSeeder::class);
        }

        $this->call(NETLAdminSeeder::class);
    }
}
