#################################################################################
# PRIMO - The P&A Project Optimizer was produced under the Methane Emissions
# Reduction Program (MERP) and National Energy Technology Laboratory's (NETL)
# National Emissions Reduction Initiative (NEMRI).
#
# NOTICE. This Software was developed under funding from the U.S. Government
# and the U.S. Government consequently retains certain rights. As such, the
# U.S. Government has been granted for itself and others acting on its behalf
# a paid-up, nonexclusive, irrevocable, worldwide license in the Software to
# reproduce, distribute copies to the public, prepare derivative works, and
# perform publicly and display publicly, and to permit others to do so.
#################################################################################

# Mapping of columns written to MongoDB by front end
# vs their original column names
PLACEHOLDERS = {
    "placeholder_one": "Placeholder 1",
    "placeholder_two": "Placeholder 2",
    "placeholder_three": "Placeholder 3",
    "placeholder_four": "Placeholder 4",
    "placeholder_five": "Placeholder 5",
    "placeholder_six": "Placeholder 6",
    "placeholder_seven": "Placeholder 7",
    "placeholder_eight": "Placeholder 8",
    "placeholder_nine": "Placeholder 9",
    "placeholder_ten": "Placeholder 10",
    "placeholder_eleven": "Placeholder 11",
    "placeholder_twelve": "Placeholder 12",
    "placeholder_thirteen": "Placeholder 13",
    "placeholder_fourteen": "Placeholder 14",
    "placeholder_fifteen": "Placeholder 15",
    "placeholder_sixteen": "Placeholder 16",
    "placeholder_seventeen": "Placeholder 17",
    "placeholder_eighteen": "Placeholder 18",
    "placeholder_nineteen": "Placeholder 19",
    "placeholder_twenty": "Placeholder 20",
}
# these are the keys used in the database for the front end
# NOT the keys used for the request body of the JSON
# these need to align with how we store the data in the database
# pylint: disable=line-too-long, duplicate-code
COLUMN_MAP = {
    "well_id": "Well ID",
    "latitude": "Latitude",
    "longitude": "Longitude",
    "age": "Age [Years]",
    "depth": "Depth [ft]",
    "state_wetlands_close_range": "State Wetlands (Near) [Yes/No]",
    "state_wetlands_wide_range": "State Wetlands (Far) [Yes/No]",
    "census_tract_id": "Census Tract ID",
    "well_type": "Well Type [Oil, Gas, Combined]",
    "state_code": "State Code",
    "county_code": "County Code",
    "land_area": "Land Area",
    "h2s_leak": "H2s Leak [Yes/No]",
    "federal_wetlands_close_range": "Federal Wetlands (Near) [Yes/No]",
    "federal_wetlands_wide_range": "Federal Wetlands (Far) [Yes/No]",
    "num_of_schools_near_well": "Number of Schools Near the Well (or if there are any 1=Yes 0=No)",
    "num_of_hospitals_near_well": "Number of Hospitals Near the Well (or if there are any 1=Yes 0=No)",
    "five_year_oil_production": "5-Year Oil Production [bbl]",
    "five_year_gas_production": "5-Year Gas Production [Mcf]",
    "name": "Well Name",
    "lifelong_oil_production": "Lifelong Oil Production [bbl]",
    "lifelong_gas_production": "Lifelong Gas Production [Mcf]",
    "incident": "Incident [Yes/No]",
    "violation": "Violation [Yes/No]",
    "compliance": "Compliance [Yes/No]",
    "leak": "Leak [Yes/No]",
    "ann_oil_production": "Annual Oil Production [bbl/Year]",
    "ann_gas_production": "Annual Gas Production [Mcf/Year]",
    "elevation_delta": "Elevation Delta (Well-to-Road Access Point) [m]",
    "distance_to_road": "Distance to Road [miles]",
    "operator_name": "Operator Name",
    "water_source_nearby": "Water Source Nearby [Yes/No]",
    "buildings_close_range": "Buildings (Near) [Yes/No]",
    "buildings_wide_range": "Buildings (Far) [Yes/No]",
    "known_soil_or_water_impact": "Known Soil or Water Impact [Yes/No]",
    "population_density": "Population Density [#/km2]",
    "hydrocarbon_losses": "Hydrocarbon Losses [Ton/year]",
    "brine_leak": "Brine Leak [Yes/No]",
    "endangered_species_on_site": "Endangered Species on Site [Yes/No]",
    "cost_of_plugging": "Cost of Plugging [USD]",
    "high_pressure_observed": "High Pressure Observed [Yes/No]",
    "idle_status_duration": "Idle Status Duration [Years]",
    "in_tribal_land": "In Tribal Land [Yes/No]",
    "likely_to_be_orphaned": "Likely to be Orphaned [Yes/No]",
    "mechanical_integrity_test": "Mechanical Integrity Test [#]",
    "number_of_mcws_nearby": "Number of MCWs Nearby [#]",
    "otherwise_incentivized_well": "Otherwise Incentivized Well [Yes/No]",
    "well_integrity": "Well Integrity Issues [Yes/No]",
    "agriculture_area_nearby": "Agriculture Area Nearby [Yes/No]",
    "historical_preservation_site": "Historical Preservation Site [Yes/No]",
    "home_use_gas_well": "Home Use Gas Well [Yes/No]",
    "post_plugging_land_use": "Post-Plugging Land Use [Yes/No]",
    # "proximity_to_geologic_faults": "Proximity to Geologic Faults [miles]",
    "surface_equipment_on_site": "Surface Equipment on Site [Yes/No]",
    "priority_score_user_input": "Priority Score User Input",
    **PLACEHOLDERS,
}
