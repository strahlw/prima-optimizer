<?php

namespace App\Types;

class EfficiencyFactors
{
    /**
     * @var Factor The number of wells factor.
     */
    public Factor $num_wells;

    /**
     * @var Factor The number of unique owners factor.
     */
    public Factor $num_unique_owners;

    /**
     * @var Factor The average distance to the nearest road factor.
     */
    public Factor $avg_distance_to_nearest_road;

    /**
     * @var Factor The average elevation change from the nearest road factor.
     */
    public Factor $avg_elevation_change_from_nearest_road;

    /**
     * @var Factor The age range factor.
     */
    public Factor $age_range;

    /**
     * @var Factor The average age factor.
     */
    public Factor $avg_age;

    /**
     * @var Factor The depth range factor.
     */
    public Factor $depth_range;

    /**
     * @var Factor The average depth factor.
     */
    public Factor $avg_depth;

    /**
     * @var Factor The distance range factor.
     */
    public Factor $distance_range;

    public Factor $population_density;

    public function __construct(
        array $num_wells,
        array $num_unique_owners,
        array $avg_distance_to_nearest_road,
        array $avg_elevation_change_from_nearest_road,
        array $age_range,
        array $avg_age,
        array $depth_range,
        array $avg_depth,
        array $distance_range,
        array $population_density
    ) {
        $this->num_wells = new Factor(...$num_wells);
        $this->num_unique_owners = new Factor(...$num_unique_owners);
        $this->avg_distance_to_nearest_road = new Factor(...$avg_distance_to_nearest_road);
        $this->avg_elevation_change_from_nearest_road = new Factor(...$avg_elevation_change_from_nearest_road);
        $this->age_range = new Factor(...$age_range);
        $this->avg_age = new Factor(...$avg_age);
        $this->depth_range = new Factor(...$depth_range);
        $this->avg_depth = new Factor(...$avg_depth);
        $this->distance_range = new Factor(...$distance_range);
        $this->population_density = new Factor(...$population_density);
    }
}
