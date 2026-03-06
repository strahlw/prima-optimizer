<?php

namespace App\Http\ValidationRules;

class EfficiencyFactorRules
{
    private static array $topLevelFactors = [
        'num_wells',
        'num_unique_owners',
        'avg_distance_to_nearest_road',
        'avg_elevation_change_from_nearest_road',
        'age_range',
        'avg_age',
        'depth_range',
        'avg_depth',
        'distance_range',
        'population_density',
    ];

    public static function rules(array $overrides = []): array
    {
        $rules = array_merge(
            self::buildEfficiencyFactorRules(self::$topLevelFactors, 'efficiency_factors'),
        );

        return array_merge($rules, $overrides);
    }

    private static function buildEfficiencyFactorRules(array $factors, string $basePath): array
    {
        $rules = [];

        foreach ($factors as $factor) {
            $path = "{$basePath}.{$factor}";
            $rules["{$path}.value"] = "required_if_accepted:{$path}.selected|int";
            $rules["{$path}.selected"] = 'required|boolean';
        }

        return $rules;
    }
}
