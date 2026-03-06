<?php

namespace Database\Factories;

use App\Models\User;
use Illuminate\Database\Eloquent\Factories\Factory;

/**
 * @extends \Illuminate\Database\Eloquent\Factories\Factory<\App\Models\Dataset>
 */
class DatasetFactory extends Factory
{
    /**
     * Define the model's default state.
     *
     * @return array<string, mixed>
     */
    public function definition(): array
    {
        $fileName = $this->faker->lexify('Input-????').'.'.'xlsx';
        $user = User::whereNotNull('organization_id')->get()->filter(fn ($user) => $user->hasRole('org-admin'))->first();

        return [
            'name' => $fileName,
            'uploaded_by_id' => $user->id,
            'organization_id' => $user->organization_id,
            'file_path' => $user->organization_id.'/'.$fileName,
        ];
    }
}
