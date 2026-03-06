<?php

namespace Database\Factories;

use App\Enum\ScenarioStatus;
use App\Models\Dataset;
use App\Models\Scenario;
use Illuminate\Database\Eloquent\Factories\Factory;

/**
 * @extends \Illuminate\Database\Eloquent\Factories\Factory<\App\Models\Scenario>
 */
class ScenarioFactory extends Factory
{
    private static $index = 0;

    public static function resetIndex()
    {
        self::$index = 0;
    }

    /**
     * Define the model's default state.
     *
     * @return array<string, mixed>
     */
    public function definition(): array
    {
        return [
            'name' => 'Scenario '.Scenario::count() + 1,
            'user_id' => 1,
            'organization_id' => 1,
            'status' => fake()->randomElement([
                ScenarioStatus::PROCESSING,
                ScenarioStatus::IN_REVIEW,
                ScenarioStatus::PUBLISHED,
            ]),
            'data' => self::generateData(),
            'deleted_at' => null,
            'created_at' => now(),
            'updated_at' => now(),
        ];
    }

    protected static function generateData(): array
    {
        return [
            'name' => 'Scenario '.Scenario::count() + 1,
            'general_specifications' => [
                'name' => 'Scenario '.Scenario::count() + 1,
                'budget' => fake()->randomFloat(2, 1000, 10000),
                'well_type' => [fake()->randomElement(['Oil', 'Gas'])],
                'dataset_id' => Dataset::first()->id,
                'organization_id' => 1,
                'additional_datasets' => [],
                'max_wells_per_owner' => 1,
                'liftime_production_less_than' => 1,
            ],
            'impact_factors' => [
                'losses' => [
                    'value' => 15,
                    'selected' => true,
                    'child_factors' => [
                        'leak' => [
                            'value' => 10,
                            'selected' => true,
                        ],
                        'violation' => [
                            'value' => 90,
                            'selected' => true,
                        ],
                    ],
                ],
                'well_age' => [
                    'value' => 25,
                    'selected' => true,
                ],
                'owner_well_count' => [
                    'value' => 10,
                    'selected' => true,
                ],
                'sensitive_receptors' => [
                    'value' => 10,
                    'selected' => true,
                    'child_factors' => [
                        'schools' => [
                            'value' => 10,
                            'selected' => true,
                        ],
                        'hospitals' => [
                            'value' => 10,
                            'selected' => true,
                        ],
                        'wetlands' => [
                            'value' => 80,
                            'selected' => true,
                        ],
                    ],
                ],
                'lifetime_production_volumes' => [
                    'value' => 30,
                    'selected' => true,
                ],
            ],
            'efficiency_factors' => [
                'avg_age' => [
                    'value' => 10,
                    'selected' => true,
                ],
                'avg_range' => [
                    'value' => 10,
                    'selected' => true,
                ],
                'avg_depth' => [
                    'value' => 10,
                    'selected' => true,
                ],
                'num_wells' => [
                    'value' => 10,
                    'selected' => true,
                ],
                'depth_range' => [
                    'value' => 10,
                    'selected' => true,
                ],
                'num_unique_owners' => [
                    'value' => 10,
                    'selected' => true,
                ],
                'avg_distance_to_nearest_road' => [
                    'value' => 10,
                    'selected' => true,
                ],
                'avg_elevation_change_from_nearest_road' => [
                    'value' => 20,
                    'selected' => true,
                ],

            ],
        ];
    }

    protected static function getNextData(): array
    {
        static $dataOptions = [
            [
                'name' => 'Scenario 1',
                'createdBy' => 'David Chen',
                'wellFileName' => '6-20welldata.csv',
                'efficiency' => 87.12,
                'avgImpact' => 84.12,
                'numProjects' => 28,
                'numWells' => 321,
                'status' => 'reviewable',
            ],
            [
                'name' => 'Scenario 2',
                'createdBy' => 'Alice Johnson',
                'wellFileName' => '7-15welldata.csv',
                'efficiency' => 90.45,
                'avgImpact' => 88.67,
                'numProjects' => 35,
                'numWells' => 289,
                'status' => 'processing',
            ],
            [
                'name' => 'Scenario 3',
                'createdBy' => 'Bob Smith',
                'wellFileName' => '8-10welldata.csv',
                'efficiency' => 85.78,
                'avgImpact' => 82.34,
                'numProjects' => 22,
                'numWells' => 310,
                'status' => 'published',
            ],
            [
                'name' => 'Scenario 4',
                'createdBy' => 'Carol White',
                'wellFileName' => '9-05welldata.csv',
                'efficiency' => 92.34,
                'avgImpact' => 89.12,
                'numProjects' => 40,
                'numWells' => 350,
                'status' => 'reviewable',
            ],
            [
                'name' => 'Scenario 5',
                'createdBy' => 'David Chen',
                'wellFileName' => '10-01welldata.csv',
                'efficiency' => 88.56,
                'avgImpact' => 85.67,
                'numProjects' => 30,
                'numWells' => 295,
                'status' => 'reviewable',
            ],
        ];

        return $dataOptions[self::$index++ % count($dataOptions)];
    }
}
