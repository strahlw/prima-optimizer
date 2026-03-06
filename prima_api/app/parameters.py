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
Parameters used throughout the code
"""
# Standard libs
import os
from datetime import datetime
from pathlib import Path

# Installed libs
from dotenv import load_dotenv

# TODO: Update based on front end requirements
ALLOWED_HOSTS = ["*"]
# Reuse favicon from PRIMO
FAVICON_URL = (
    "https://github.com/NEMRI-org/primo-optimizer/"
    "blob/main/docs/_static/favicon.ico?raw=true"
)
LOGO_URL = (
    "https://github.com/NEMRI-org/primo-optimizer/"
    "blob/main/docs/_static/logo-print-hd.jpg?raw=true"
)
RELEASE = "0.1.dev0"
VERSION = "0.1"
START_TIME = datetime.now()

ENV_FILE = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(ENV_FILE)
# Logger parameters
LOGGER_FORMAT = "%(asctime)s - %(name)s:%(lineno)d - %(levelname)s - %(message)s"
LOGGER_DATE = "%d-%b-%y %H:%M:%S"
BACKUP_COUNT = 10
MAX_BYTES = 2000000
API_LOGFILE = "logs/api.log"
CELERY_LOGFILE = "logs/celery.log"

# Solver selection
SOLVER = os.environ.get("SOLVER", "scip")

# Redis parameters
REDIS_BROKER_URL = os.environ.get("REDIS_BROKER_URL", "localhost:6379")
REDIS_BACKEND_URL = os.environ.get("REDIS_BACKEND_URL", "localhost:6379")
REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
REDIS_PORT = os.environ.get("REDIS_PORT", "6379")


# MongoDB Parameters
MONGO_HOST = os.environ.get("MONGO_INITDB_HOST", "mongodb")
MONGO_USER = os.environ.get("MONGO_INITDB_ROOT_USERNAME", "user")
MONGO_PASS = os.environ.get("MONGO_INITDB_ROOT_PASSWORD", "pass")
MONGO_URI = f"mongodb://{MONGO_USER}:{MONGO_PASS}@{MONGO_HOST}:27017/"

# The only database with read/write access for the API
MONGO_DATABASE = os.environ.get("MONGO_INITDB_DATABASE", "primo_api")

# The collection from where API reads well data
MONGO_DATASET_COLLECTION = os.environ.get(
    "MONGO_INITDB_DATASET_COLLECTION", "datasets_json"
)

# The collection where API writes project results with specific well details
MONGO_WELL_COLLECTION = os.environ.get("MONGO_INITDB_WELL_COLLECTION", "wells")

# The collection where API writes results of ranking wells
MONGO_RANK_COLLECTION = os.environ.get("MONGO_INITDB_RANK_COLLECTION", "ranked_wells")


# MySQL Parameters
MYSQL_HOST = os.environ.get("MYSQL_HOST", "mysql")
MYSQL_USER = os.environ.get("MYSQL_USER", "user")
MYSQL_PASS = os.environ.get("MYSQL_ROOT_PASSWORD", "pass")
MYSQL_PORT = os.environ.get("MYSQL_PORT", "3306")

# The database with read/write access for the API
MYSQL_DATABASE = os.environ.get("MYSQL_DATABASE", "primo_api")

# The collection where API writes project results
MYSQL_PROJECT_COLLECTION = os.environ.get("MYSQL_PROJECT_COLLECTION", "projects")

# The collection where API writes project results with specific well details
MYSQL_PROJECT_WELL_COLLECTION = os.environ.get(
    "MYSQL_PROJECT_WELL_COLLECTION", "project_well"
)

# the default label for wells that are not assigned to clusters in the
# manual recalculation endpoint
# when the re-optimize step is implemented, this will no longer be needed
# we will have to store the cluster information in a database
UNASSIGNED_CLUSTER = -1

# Variables used PRIMO API Documentation
IMPACT_FACTORS = {
    "well_age": {"selected": True, "value": 20},
    "losses": {
        "selected": True,
        "value": 20,
        "child_factors": {
            "leak": {"selected": True, "value": 50},
            "violation": {"selected": True, "value": 50},
        },
    },
    "sensitive_receptors": {
        "selected": True,
        "value": 14,
        "child_factors": {
            "schools": {"selected": True, "value": 43},
            "hospitals": {"selected": True, "value": 57},
        },
    },
    "owner_well_count": {"selected": True, "value": 10},
    "lifelong_production_volume": {
        "selected": True,
        "value": 20,
        "child_factors": {
            "lifelong_gas_production": {"selected": True, "value": 100},
            "lifelong_oil_production": {"selected": True, "value": 0},
        },
    },
    "environment": {
        "selected": True,
        "value": 16,
        "child_factors": {
            "state_wetlands_near": {"selected": True, "value": 100},
            "known_soil_or_water_impact": {"selected": False, "value": 30},
            "water_source_nearby": {"selected": False, "value": 40},
        },
    },
}
# "avg_age": {
#     "selected": True,
#     "value": 10,
# },
# "avg_depth": {
#     "selected": True,
#     "value": 10,
# },

EFFICIENCY_FACTORS = {
    "age_range": {
        "selected": True,
        "value": 10,
    },
    "distance_range": {
        "selected": True,
        "value": 20,
    },
    "num_wells": {
        "selected": True,
        "value": 10,
    },
    "depth_range": {
        "selected": True,
        "value": 30,
    },
    "avg_distance_to_nearest_road": {
        "selected": True,
        "value": 10,
    },
    "avg_elevation_change_from_nearest_road": {
        "selected": True,
        "value": 10,
    },
    "population_density": {
        "selected": True,
        "value": 10,
    },
}

PACOST = {
    "shallow_gas_well_cost": 10000,
    "deep_gas_well_cost": 30000,
    "shallow_oil_well_cost": 20000,
    "deep_oil_well_cost": 25000,
    "cost_efficiency": 0.9,
}

SOLVER_OPTIONS = {
    "solver_time": 3600,
    "absolute_gap": 1000,
    "relative_gap": 0.0001,
    "model": "impact",
    "use_lazy_constraints": False,
}

DATA_QUALITY_CHECKS = {
    "basic_data_checks": True,
    "handle_missing_depth": "specify-value",
    "handle_missing_production": "specify-value",
    "handle_missing_type": "specify-value",
    "handle_missing_well_age": "specify-value",
    "specified_age": 225,
    "specified_depth": 3340,
    "specified_annual_gas_production": 22.32,
    "specified_annual_oil_production": 38.32,
    "specified_lifetime_gas_production": 22000,
    "specified_lifetime_oil_production": 22000,
    "specified_type": "oil",
}

GENERAL_SPECIFICATIONS = {
    "name": "Scenario 1",
    "budget": 4000000,
    "well_type": ["Oil"],
    "dataset_id": 1,
    "organization_id": 2,
    "additional_datasets": [],
    "min_wells_in_project": 2,
    "max_wells_in_project": 10,
    "max_distance_between_project_wells": 10,
    "well_depth_limit": 4000,
    "max_wells_per_owner": 10,
    "min_lifetime_gas_production": 0,
    "max_lifetime_gas_production": 100000,
    "min_lifetime_oil_production": 0,
    "max_lifetime_oil_production": 10000,
    **DATA_QUALITY_CHECKS,
    **SOLVER_OPTIONS,
    **PACOST,
}

SCENARIO_PARAM_EXAMPLE = {
    "scenario_id": 1,
    "impact_factors": IMPACT_FACTORS,
    "efficiency_factors": EFFICIENCY_FACTORS,
    "general_specifications": GENERAL_SPECIFICATIONS,
}

RANKWELLS_PARAM_EXAMPLE = {
    "impact_factors": IMPACT_FACTORS,
    "efficiency_factors": EFFICIENCY_FACTORS,
    "general_specifications": GENERAL_SPECIFICATIONS,
}


MANUAL_OVERRIDE_REQUEST_EXAMPLE = {
    "scenario_id": 1,
    "impact_factors": IMPACT_FACTORS,
    "efficiency_factors": EFFICIENCY_FACTORS,
    "general_specifications": GENERAL_SPECIFICATIONS,
    "child_scenario_id": 1,
    "parent_project_ids": [201, 202, 203, 204],
    "projects_remove": [40, 49],
    "wells_remove": {
        "7": [3100029384732, 10923847492],
        "13": [310003948570000, 310009283740000],
    },
    "projects_lock": [20, 14],
    "wells_lock": {
        "6": [3100029385732, 10923847292],
        "12": [310003648570000, 310009203740000],
    },
    "wells_reassign_from": {
        "5": [3100129384732, 10923127492],
        "8": [310003912570000, 310009281240000],
        "unassigned": [31000356720000, 31000637240000],
    },
    "wells_reassign_to": {
        "7": [3100023384732, 10923823492],
        "16": [310003942370000, 310009233740000],
    },
}

DATA_INPUT_CHECK_EXAMPLE = {
    "file_path": "/var/www/netl-mwu/netl-mwu/api/storage/app/tmp/FILENAMEHERE",
    "dataset_id": 31415926535,
}

# HTTP Response detail when successful connection to backend databases is possible
SUCCESSFUL_CONNECTION = {
    "description": "Response when successfully connected",
    "content": {
        "application/json": {
            "example": {
                "Status": "OK",
                "Connection Status": "Successfully connected",
            }
        }
    },
}
# HTTP Response detail when impact/efficiency metrics are invalid
INVALID_METRIC_SELECTIONS = {
    "description": "Error when ranking cannot be executed with provided parameters",
    "content": {
        "application/json": {
            "example": {"detail": "Impact/Efficiency Weight selections are invalid"}
        }
    },
}


# HTTP Response detail when a task is not found
TASK_NOT_FOUND = {
    "description": "Error when task id is not found",
    "content": {
        "application/json": {"example": {"detail": "Could not find task task_id"}}
    },
}

# HTTP Response detail when a well dataset is not found
WELL_DATA_NOT_FOUND = {
    "description": "Error when well dataset is not found in backend",
    "content": {
        "application/json": {
            "example": {
                "detail": "Could not find data in MongoDB: is it correctly uploaded?"
            }
        }
    },
}

KPI_SUMMARY_EXAMPLE = {**SCENARIO_PARAM_EXAMPLE, "project_ids": [1, 2, 3, 4, 5]}

FULL_LIST_IMPACT_FACTORS = {
    "well_age": {"value": 0, "selected": False},
    "losses": {
        "value": 0,
        "selected": False,
        "child_factors": {
            "leak": {"value": 0, "selected": False},
            "violation": {"value": 0, "selected": False},
            "compliance": {"value": 0, "selected": False},
            "incident": {"value": 0, "selected": False},
            "hydrocarbon_losses": {"value": 0, "selected": False},
        },
    },
    "sensitive_receptors": {
        "value": 0,
        "selected": False,
        "child_factors": {
            "schools": {"value": 0, "selected": False},
            "hospitals": {"value": 0, "selected": False},
            "agriculture_area_nearby": {"value": 0, "selected": False},
            "buildings_far": {"value": 0, "selected": False},
            "buildings_near": {"value": 0, "selected": False},
        },
    },
    "owner_well_count": {"value": 0, "selected": False},
    "lifelong_production_volume": {
        "value": 2,
        "selected": False,
        "child_factors": {
            "lifelong_gas_production": {"value": 50, "selected": False},
            "lifelong_oil_production": {"value": 50, "selected": False},
        },
    },
    "environment": {
        "value": 0,
        "selected": False,
        "child_factors": {
            "water_source_nearby": {"value": 0, "selected": False},
            "known_soil_or_water_impact": {"value": 0, "selected": False},
            "fed_wetlands_near": {"value": 0, "selected": False},
            "fed_wetlands_far": {"value": 0, "selected": False},
            "state_wetlands_near": {"value": 0, "selected": False},
            "state_wetlands_far": {"value": 0, "selected": False},
        },
    },
    "ecological_receptors": {
        "value": 1,
        "selected": False,
        "child_factors": {
            "endangered_species_on_site": {"value": 100, "selected": False}
        },
    },
    "other_losses": {
        "value": 43,
        "selected": True,
        "child_factors": {
            "brine_leak": {"value": 50, "selected": True},
            "h2s_leak": {"value": 50, "selected": False},
        },
    },
    "five_year_production_volume": {
        "value": 2,
        "selected": False,
        "child_factors": {
            "five_year_gas_production": {"value": 50, "selected": False},
            "five_year_oil_production": {"value": 50, "selected": False},
        },
    },
    "ann_production_volume": {
        "value": 2,
        "selected": False,
        "child_factors": {
            "ann_gas_production": {"value": 50, "selected": False},
            "ann_oil_production": {"value": 50, "selected": False},
        },
    },
    "site_considerations": {
        "value": 4,
        "selected": False,
        "child_factors": {
            "historical_preservation_site": {"value": 20, "selected": False},
            "home_use_gas_well": {"value": 30, "selected": False},
            "post_plugging_land_use": {"value": 25, "selected": False},
            "surface_equipment_on_site": {"value": 25, "selected": False},
        },
    },
    "cost_of_plugging": {"value": 0, "selected": False},
    "high_pressure_observed": {"value": 0, "selected": False},
    "idle_status_duration": {"value": 0, "selected": False},
    "in_tribal_land": {"value": 0, "selected": False},
    "likely_to_be_orphaned": {"value": 0, "selected": False},
    "number_of_mcws_nearby": {"value": 0, "selected": False},
    "mechanical_integrity_test": {"value": 0, "selected": False},
    "otherwise_incentivized_well": {"value": 0, "selected": False},
    "well_integrity": {"value": 0, "selected": False},
    "placeholder_one": {"value": 0, "selected": False},
    "placeholder_two": {"value": 0, "selected": False},
    "placeholder_three": {"value": 0, "selected": False},
    "placeholder_four": {"value": 0, "selected": False},
    "placeholder_five": {"value": 0, "selected": False},
    "placeholder_six": {"value": 0, "selected": False},
    "placeholder_seven": {"value": 0, "selected": False},
    "placeholder_eight": {"value": 0, "selected": False},
    "placeholder_nine": {"value": 0, "selected": False},
    "placeholder_ten": {"value": 0, "selected": False},
    "placeholder_eleven": {"value": 0, "selected": False},
    "placeholder_twelve": {"value": 0, "selected": False},
    "placeholder_thirteen": {"value": 0, "selected": False},
    "placeholder_fourteen": {"value": 0, "selected": False},
    "placeholder_fifteen": {"value": 0, "selected": False},
    "placeholder_sixteen": {"value": 0, "selected": False},
    "placeholder_seventeen": {"value": 0, "selected": True},
    "placeholder_eighteen": {"value": 0, "selected": False},
    "placeholder_nineteen": {"value": 0, "selected": False},
    "placeholder_twenty": {"value": 0, "selected": False},
}
