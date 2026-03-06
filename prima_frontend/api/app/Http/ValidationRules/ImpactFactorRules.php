<?php

namespace App\Http\ValidationRules;

class ImpactFactorRules
{
    private static array $topLevelFactors = [
        'losses',
        'well_age',
        'owner_well_count',
        'likely_to_be_orphaned',
        'in_tribal_land',
        'cost_of_plugging',
        'high_pressure_observed',
        'idle_status_duration',
        'number_of_mcws_nearby',
        'mechanical_integrity_test',
        'otherwise_incentivized_well',
        'well_integrity',
        'placeholder_one',
        'placeholder_two',
        'placeholder_three',
        'placeholder_four',
        'placeholder_five',
        'placeholder_six',
        'placeholder_seven',
        'placeholder_eight',
        'placeholder_nine',
        'placeholder_ten',
        'placeholder_eleven',
        'placeholder_twelve',
        'placeholder_thirteen',
        'placeholder_fourteen',
        'placeholder_fifteen',
        'placeholder_sixteen',
        'placeholder_seventeen',
        'placeholder_eighteen',
        'placeholder_nineteen',
        'placeholder_twenty',
        'sensitive_receptors',
        'environment',
        'ann_production_volume',
        'five_year_production_volume',
        'lifelong_production_volume',
        'site_considerations',
        'ecological_receptors',
        'other_losses',
    ];

    private static array $lossesChildFactors = [
        'leak',
        'violation',
        'compliance',
        'incident',
        'hydrocarbon_losses',
    ];

    private static array $sensitiveReceptorsChildFactors = [
        'schools',
        'hospitals',
        'agriculture_area_nearby',
        'buildings_far',
        'buildings_near',
    ];

    private static array $environmentChildFactors = [
        'water_source_nearby',
        'known_soil_or_water_impact',
        'fed_wetlands_near',
        'fed_wetlands_far',
        'state_wetlands_near',
        'state_wetlands_far',
    ];

    private static array $annProductionVolumeChildFactors = [
        'ann_gas_production',
        'ann_oil_production',
    ];

    private static array $fiveYearProductionVolumeChildFactors = [
        'five_year_gas_production',
        'five_year_oil_production',
    ];

    private static array $lifelongProductionVolumeChildFactors = [
        'lifelong_gas_production',
        'lifelong_oil_production',
    ];

    private static array $siteConsiderationsChildFactors = [
        'historical_preservation_site',
        'home_use_gas_well',
        'post_plugging_land_use',
        'surface_equipment_on_site',
    ];

    private static array $ecologicalReceptorsChildFactors = [
        'endangered_species_on_site',
    ];

    private static array $otherLossesChildFactors = [
        'brine_leak',
        'h2s_leak',
    ];

    public static function rules(array $overrides = []): array
    {
        $rules = array_merge(
            self::buildImpactFactorRules(self::$topLevelFactors, 'impact_factors'),
            self::buildImpactFactorRules(self::$lossesChildFactors, 'impact_factors.losses.child_factors'),
            self::buildImpactFactorRules(self::$sensitiveReceptorsChildFactors, 'impact_factors.sensitive_receptors.child_factors'),
            self::buildImpactFactorRules(self::$environmentChildFactors, 'impact_factors.environment.child_factors'),
            self::buildImpactFactorRules(self::$annProductionVolumeChildFactors, 'impact_factors.ann_production_volume.child_factors'),
            self::buildImpactFactorRules(self::$fiveYearProductionVolumeChildFactors, 'impact_factors.five_year_production_volume.child_factors'),
            self::buildImpactFactorRules(self::$lifelongProductionVolumeChildFactors, 'impact_factors.lifelong_production_volume.child_factors'),
            self::buildImpactFactorRules(self::$siteConsiderationsChildFactors, 'impact_factors.site_considerations.child_factors'),
            self::buildImpactFactorRules(self::$ecologicalReceptorsChildFactors, 'impact_factors.ecological_receptors.child_factors'),
            self::buildImpactFactorRules(self::$otherLossesChildFactors, 'impact_factors.other_losses.child_factors'),
        );

        return array_merge($rules, $overrides);
    }

    private static function buildImpactFactorRules(array $factors, string $basePath): array
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
