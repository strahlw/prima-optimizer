<?php

namespace Database\Seeders;

use App\Models\Organization;
use Illuminate\Database\Seeder;

class OrganizationSeeder extends Seeder
{
    /**
     * Run the database seeds.
     */
    public function run(): void
    {
        Organization::firstOrCreate(['key' => 'NY'], ['key' => 'NY', 'name' => 'New York State Department of Environmental Conservation', 'available_funding' => 8123602, 'latitude' => 42.652843, 'longitude' => -73.757874]);
        Organization::firstOrCreate(['key' => 'CA'], ['key' => 'CA', 'name' => 'California State Lands Commission', 'available_funding' => 21913688, 'latitude' => 38.576668, 'longitude' => -121.493629]);
        Organization::firstOrCreate(['key' => 'CO'], ['key' => 'CO', 'name' => 'Colorado Energy and Carbon Management Commission', 'available_funding' => 12608270, 'latitude' => 39.739235, 'longitude' => -104.990250]);
        Organization::firstOrCreate(['key' => 'IL'], ['key' => 'IL', 'name' => 'Illinois Department of Natural Resources', 'available_funding' => 17367009, 'latitude' => 39.781721, 'longitude' => -89.650148]);
        Organization::firstOrCreate(['key' => 'KY'], ['key' => 'KY', 'name' => 'Kentucky Divison of Oil and Gas', 'available_funding' => 12912198, 'latitude' => 38.186722, 'longitude' => -84.875374]);
        Organization::firstOrCreate(['key' => 'LA'], ['key' => 'LA', 'name' => 'Louisiana Department of Natural Resources', 'available_funding' => 15661335, 'latitude' => 30.4583, 'longitude' => -91.1403]);
        Organization::firstOrCreate(['key' => 'MI'], ['key' => 'MI', 'name' => 'Michigan Department of Environment, Great Lakes, and Energy', 'available_funding' => 5022306, 'latitude' => 42.7325, 'longitude' => -84.5555]);
        Organization::firstOrCreate(['key' => 'NM'], ['key' => 'NM', 'name' => 'New Mexico Energy, Minerals, and Natural Resources Department', 'available_funding' => 14656151, 'latitude' => 35.686975, 'longitude' => -105.937799]);
        Organization::firstOrCreate(['key' => 'OH'], ['key' => 'OH', 'name' => 'Ohio Department of Natural Resources', 'available_funding' => 19941597, 'latitude' => 39.9612, 'longitude' => -82.9988]);
        Organization::firstOrCreate(['key' => 'PA'], ['key' => 'PA', 'name' => 'PA Department of Environmental Protection', 'available_funding' => 44457220, 'latitude' => 40.269789, 'longitude' => -76.875613]);
        Organization::firstOrCreate(['key' => 'TX'], ['key' => 'TX', 'name' => 'Texas Commission of Environmental Quality', 'available_funding' => 134151343, 'latitude' => 30.2672, 'longitude' => -97.7431]);
        Organization::firstOrCreate(['key' => 'UT'], ['key' => 'UT', 'name' => 'Utah Department of Environmental Quality', 'available_funding' => 2750115, 'latitude' => 40.7608, 'longitude' => -111.8910]);
        Organization::firstOrCreate(['key' => 'VA'], ['key' => 'VA', 'name' => 'Virginia Department of Energy', 'available_funding' => 2643702, 'latitude' => 37.5407, 'longitude' => -77.4360]);
        Organization::firstOrCreate(['key' => 'WV'], ['key' => 'WV', 'name' => 'West Virginia Department of Environmental Protection', 'available_funding' => 37791464, 'latitude' => 38.3498, 'longitude' => -81.6326]);
        Organization::firstOrCreate(['key' => 'NETL'], ['key' => 'NETL', 'name' => 'National Energy Technology Laboratory', 'available_funding' => 0, 'latitude' => 40.269789, 'longitude' => -76.875613]);
    }
}
