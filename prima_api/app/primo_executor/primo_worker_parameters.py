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
"""
Implements constant parameters needed to run PRIMO backend
"""
# Standard libs
import logging

# Installed libs
from primo.data_parser import WellDataColumnNames

# pylint: disable=unused-import
from primo.data_parser.default_data import (
    SUPP_EFF_METRICS,
    SUPP_IMPACT_METRICS,
    _SupportedContent,
)
from primo.data_parser.input_config import ScenarioType
from pyomo.common.config import Bool, NonNegativeFloat

# User-defined libs
from app_setup import setup_logger
from utils import PLACEHOLDERS

LOGGER = logging.getLogger(__name__)

# multiplier for MCF to yield BoE
# it's 5.8 in some sources, but the USGS uses 6.0
MCF_TO_BOE = 1.0 / 6.0

# parameters for optimization
THRESHOLD_DISTANCE = 10  # miles
MOBILIZATION_COST = {1: 120000, 2: 210000, 3: 280000, 4: 350000}
ADDITIONAL_MOBILIZATION_COST = 84000  # amount per well after 4 wells
START_OF_ADDITIONAL_MOBILIZATION_COST = len(MOBILIZATION_COST) + 1
LOUVAIN_SWITCH_SIZE = 1000
MULTIPLIER_FOR_LOUVAIN_CLUSTER_SIZE_BUDGET = 4
MULTIPLIER_FOR_LOUVAIN_CLUSTER_SIZE_MAX_WELLS = 10
MINIMUM_MAX_SIZE = 200

COLUMN_NAMES = {
    "well_type": "Well Type [Oil, Gas, Combined]",
    "five_year_oil_production": "5-Year Oil Production [bbl]",
    "five_year_gas_production": "5-Year Gas Production [Mcf]",
    "h2s_leak": "H2s Leak [Yes/No]",
    "elevation_delta": "Elevation Delta (Well-to-Road Access Point) [m]",
    "dist_to_road": "Distance to Road [miles]",
    "leak": "Leak [Yes/No]",
    "violation": "Violation [Yes/No]",
    "incident": "Incident [Yes/No]",
    "compliance": "Compliance [Yes/No]",
    "life_oil_production": "Lifelong Oil Production [bbl]",
    "life_gas_production": "Lifelong Gas Production [Mcf]",
    "ann_oil_production": "Annual Oil Production [bbl/Year]",
    "ann_gas_production": "Annual Gas Production [Mcf/Year]",
    "operator_name": "Operator Name",
    "population_density": "Population Density [#/km2]",
    "hospitals": "Number of Hospitals Near the Well (or if there are any 1=Yes 0=No)",
    "schools": "Number of Schools Near the Well (or if there are any 1=Yes 0=No)",
    "buildings_near": "Buildings (Near) [Yes/No]",
    "buildings_far": "Buildings (Far) [Yes/No]",
    "fed_wetlands_near": "Federal Wetlands (Near) [Yes/No]",
    "fed_wetlands_far": "Federal Wetlands (Far) [Yes/No]",
    "state_wetlands_near": "State Wetlands (Near) [Yes/No]",
    "state_wetlands_far": "State Wetlands (Far) [Yes/No]",
    "water_source_nearby": "Water Source Nearby [Yes/No]",
    "known_soil_or_water_impact": "Known Soil or Water Impact [Yes/No]",
    "brine_leak": "Brine Leak [Yes/No]",
    "hydrocarbon_losses": "Hydrocarbon Losses [Ton/year]",
    # adding new impact factors
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
    **PLACEHOLDERS,
}
# Columns that don't exist in the code base - keeping in case we need it
# it is also updated in a separate function
ADDITIONAL_COLUMNS = {}


# update some to the key that the front end expects for the ranking page
SCORE_COLUMN_MAP_ADDITIONS = {
    "Owner Well-Count": "owner_well_count",
    "Priority Score [0-100]": "priority",
    "Age [Years]": "well_age",
}

SCORE_COLUMN_MAP = {value: key for key, value in COLUMN_NAMES.items()}
SCORE_COLUMN_MAP.update(SCORE_COLUMN_MAP_ADDITIONS)
SCORE_COLUMN_MAP.update({value: key for key, value in ADDITIONAL_COLUMNS.items()})


# PRIMO column names object
def get_well_data_columns(scenario_type: ScenarioType) -> WellDataColumnNames:
    """
    Builds and returns a WellDataColumnNames object

    Parameters
    ----------
    scenario_type : ScenarioType
        The type of scenario

    Returns
    -------
    WellDataColumnNames
        WellDataColumnNames object for well data
    """
    additional_columns = {**ADDITIONAL_COLUMNS}

    # here we have to add the priority score column in the case that it is not
    # well ranking and not project recommendations for the check_for_avail_data endpoint
    if (not scenario_type.well_ranking and scenario_type.project_recommendation) or (
        not scenario_type.well_ranking and not scenario_type.project_recommendation
    ):
        LOGGER.info("Adding Priority Score attribute to Well Data Column Names")
        additional_columns.update({"priority_score": "Priority Score User Input"})

    return WellDataColumnNames(
        "Well ID",
        "Latitude",
        "Longitude",
        "Age [Years]",
        "Depth [ft]",
        **COLUMN_NAMES,
        additional_columns=additional_columns,
    )


# Supported impact metrics - leaving this here for future impact metrics
SUPP_IMPACT_METRICS_ADDITIONS = {}

SUPP_IMPACT_METRICS.update(SUPP_IMPACT_METRICS_ADDITIONS)

# Efficiency metrics that will be supported in the future (or variants of them)
# "average_age": _SupportedContent(
#     name="average_age",
#     full_name="Average Age [Years]",
#     required_data="age",
# ),
# "average_depth": _SupportedContent(
#     name="average_depth",
#     full_name="Depth Range [ft]",
#     required_data="depth",
# ),

# Map factors that are named differently in the front end than back end
# Key refers to what the factor is called in front end
# Value refers to what the primo-optimizer library needs it in the back end
FACTOR_MAP = {
    # efficiency factors
    "owner_well_count": "well_count",
    "avg_distance_to_nearest_road": "dist_to_road",
    "avg_elevation_change_from_nearest_road": "elevation_delta",
    "avg_age": "average_age",
    "avg_depth": "average_depth",
    "distance_range": "dist_range",
    # impact factors
    "losses": "well_history",
}
