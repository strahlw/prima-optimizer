<?php

namespace Database\Seeders;

use App\Enum\ScenarioStatus;
use App\Models\Dataset;
use App\Models\Organization;
use App\Models\Scenario;
use App\Models\User;
use Database\Factories\ScenarioFactory;
use Illuminate\Database\Seeder;

class ScenarioSeeder extends Seeder
{
    /**
     * Run the database seeds.
     */
    public function run(): void
    {
        $user = User::get()->filter(fn ($user) => $user->hasRole('org-admin'))->first();

        if (Scenario::count() > 0) {
            return;
        }

        $dataset = Dataset::create([
            'name' => 'Well Data - NY.csv',
            'uploaded_by_id' => $user->id,
            'organization_id' => $user->organization_id,
            'file_path' => "$user->organization_id/Well Data - NY.csv",
        ]);

        Scenario::factory()->create([
            'user_id' => $user->id,
            'organization_id' => $user->organization_id,
            'status' => ScenarioStatus::PUBLISHED,
            'dataset_id' => Dataset::first()->id,
            'status_by_id' => $user->id,
        ]);

        Scenario::factory()->create([
            'user_id' => $user->id,
            'organization_id' => $user->organization_id,
            'status' => ScenarioStatus::PUBLISHED,
            'dataset_id' => Dataset::first()->id,
            'status_by_id' => $user->id,
        ]);

        Scenario::factory()->create([
            'user_id' => $user->id,
            'organization_id' => $user->organization_id,
            'status' => ScenarioStatus::PUBLISHED,
            'dataset_id' => Dataset::first()->id,
            'status_by_id' => $user->id,
        ]);

        Scenario::factory()->count(5)->create([
            'user_id' => $user->id,
            'organization_id' => $user->organization_id,
            'dataset_id' => Dataset::first()->id,
            'status_by_id' => $user->id,
        ]);

        if (config('app.env') === 'qa') {
            $firstOrgKey = Organization::first()->key;
            $qaOrgAdmin = User::where('email', "karen+{$firstOrgKey}admin@email.com")->first();

            Scenario::factory()->count(5)->create([
                'user_id' => $qaOrgAdmin->id,
                'organization_id' => $qaOrgAdmin->organization_id,
                'status' => ScenarioStatus::IN_REVIEW,
                'dataset_id' => Dataset::first()->id,
                'status_by_id' => $qaOrgAdmin->id,
            ]);
            ScenarioFactory::resetIndex();

            Scenario::factory()->count(5)->create([
                'user_id' => $qaOrgAdmin->id,
                'organization_id' => $qaOrgAdmin->organization_id,
                'status' => ScenarioStatus::IN_REVIEW,
                'dataset_id' => Dataset::first()->id,
                'status_by_id' => $qaOrgAdmin->id,
            ]);
            ScenarioFactory::resetIndex();

            Scenario::factory()->count(3)->create([
                'user_id' => $qaOrgAdmin->id,
                'organization_id' => $qaOrgAdmin->organization_id,
                'status' => ScenarioStatus::PROCESSING,
                'dataset_id' => Dataset::first()->id,
                'status_by_id' => $qaOrgAdmin->id,
            ]);
            ScenarioFactory::resetIndex();

            Scenario::factory()->count(3)->create([
                'user_id' => $qaOrgAdmin->id,
                'organization_id' => $qaOrgAdmin->organization_id,
                'status' => ScenarioStatus::PUBLISHED,
                'dataset_id' => Dataset::first()->id,
                'status_by_id' => $qaOrgAdmin->id,
            ]);
            ScenarioFactory::resetIndex();
        }

        Scenario::get()->each(function (Scenario $scenario) {
            $data = $scenario->data;
            $data['name'] = 'Scenario '.$scenario->id;
            $scenario->update(['data' => $data]);
        });
    }
}
