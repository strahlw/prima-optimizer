# Standard libs
import copy

# pylint: disable=duplicate-code
DATASET_ID = 1
NUM_BINS = 10
DATASET_ID_USER_PRIORITY_SCORES = DATASET_ID + 1
DATASET_ID_EXHAUSTIVE_CLUSTERING = DATASET_ID + 2

INPUT_DATA_REQUEST_BODY = {
    "file_path": "/usr/src/app/data_testing/"
    "2025_07_24_test_data_random_lifelong_adjustments.csv",
    "dataset_id": DATASET_ID,
}

INPUT_DATA_REQUEST_BODY_USER_PRIORITY_SCORES = {
    "file_path": "/usr/src/app/data_testing/"
    "2025_07_24_test_data_random_lifelong_adjustments_user_priority_score_input.csv",
    "dataset_id": DATASET_ID_USER_PRIORITY_SCORES,
}

INPUT_DATA_REQUEST_BODY_EXHAUSTIVE_CLUSTERING = {
    "file_path": "/usr/src/app/data_testing/"
    "2025_07_24_test_data_random_lifelong_adjustments_truncated.csv",
    "dataset_id": DATASET_ID_EXHAUSTIVE_CLUSTERING,
}


DATA_AVAIL_CHECK_BODY = {
    "name": "Scenario 1",
    "budget": 4000000,
    "well_type": ["Oil"],
    "dataset_id": DATASET_ID,
    "organization_id": 2,
    "additional_datasets": [],
    "min_wells_in_project": 2,
    "max_wells_in_project": 10,
    "max_distance_between_project_wells": 10,
    "well_depth_limit": 4000,
    "min_percent_wells_in_disadvantaged_community": 40,
    "max_wells_per_owner": 10,
    "min_lifetime_gas_production": None,
    "max_lifetime_gas_production": None,
    "min_lifetime_oil_production": None,
    "max_lifetime_oil_production": None,
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
    "solver_time": 200,
    "absolute_gap": 50,
    "relative_gap": 0.1,
    "model": "impact-and-efficiency",
    "use_lazy_constraints": False,
    "shallow_gas_well_cost": 100000,
    "deep_gas_well_cost": 300000,
    "shallow_oil_well_cost": 200000,
    "deep_oil_well_cost": 250000,
    "cost_efficiency": 0.9,
}

RANK_WELLS_REQUEST_BODY = {
    "impact_factors": {
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
            "value": 20,
            "selected": True,
            "child_factors": {
                "lifelong_gas_production": {"value": 100, "selected": True},
                "lifelong_oil_production": {"value": 0, "selected": False},
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
    },
    "efficiency_factors": {
        "age_range": {"selected": True, "value": 10},
        "distance_range": {"selected": True, "value": 20},
        "num_wells": {"selected": True, "value": 10},
        "depth_range": {"selected": True, "value": 30},
        "avg_distance_to_nearest_road": {"selected": True, "value": 10},
        "avg_elevation_change_from_nearest_road": {"selected": True, "value": 10},
        "population_density": {"selected": True, "value": 10},
    },
    "general_specifications": {
        "name": "Scenario 1",
        "budget": 4000000,
        "well_type": ["Oil"],
        "dataset_id": DATASET_ID,
        "organization_id": 2,
        "additional_datasets": [],
        "min_wells_in_project": 2,
        "max_wells_in_project": 10,
        "max_distance_between_project_wells": 10,
        "well_depth_limit": 4000,
        "max_wells_per_owner": 10,
        "min_lifetime_gas_production": None,
        "max_lifetime_gas_production": None,
        "min_lifetime_oil_production": None,
        "max_lifetime_oil_production": None,
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
        "solver_time": 3600,
        "absolute_gap": 10,
        "relative_gap": 0.001,
        "model": "impact",
        "use_lazy_constraints": False,
        "shallow_gas_well_cost": 100000,
        "deep_gas_well_cost": 300000,
        "shallow_oil_well_cost": 200000,
        "deep_oil_well_cost": 250000,
        "cost_efficiency": 0.9,
    },
}

RANK_WELLS_REQUEST_BODY_NO_EFFICIENCY_FACTORS = copy.deepcopy(RANK_WELLS_REQUEST_BODY)
del RANK_WELLS_REQUEST_BODY_NO_EFFICIENCY_FACTORS["efficiency_factors"]
RANK_WELLS_REQUEST_BODY_NO_EFFICIENCY_FACTORS["use_cases"] = {"cases": ["Well Ranking"]}

RANK_WELLS_REQUEST_BODY_NO_IMPACT_FACTORS = copy.deepcopy(RANK_WELLS_REQUEST_BODY)
del RANK_WELLS_REQUEST_BODY_NO_IMPACT_FACTORS["impact_factors"]
RANK_WELLS_REQUEST_BODY_NO_IMPACT_FACTORS["general_specifications"][
    "dataset_id"
] = DATASET_ID_USER_PRIORITY_SCORES
RANK_WELLS_REQUEST_BODY_NO_IMPACT_FACTORS["use_cases"] = {
    "cases": ["P&A Project Recommendations"]
}

RUN_PRIMO_REQUEST_BODY = {"scenario_id": 1, **RANK_WELLS_REQUEST_BODY}

RUN_PRIMO_REQUEST_BODY_NO_IMPACT_FACTORS = copy.deepcopy(RUN_PRIMO_REQUEST_BODY)
del RUN_PRIMO_REQUEST_BODY_NO_IMPACT_FACTORS["impact_factors"]
RUN_PRIMO_REQUEST_BODY_NO_IMPACT_FACTORS["general_specifications"][
    "dataset_id"
] = DATASET_ID_USER_PRIORITY_SCORES
RUN_PRIMO_REQUEST_BODY_NO_IMPACT_FACTORS["use_cases"] = {
    "cases": ["P&A Project Recommendations"]
}

RUN_PRIMO_REQUEST_BODY_SUFFICIENT_BUDGET = copy.deepcopy(RUN_PRIMO_REQUEST_BODY)
RUN_PRIMO_REQUEST_BODY_SUFFICIENT_BUDGET["general_specifications"]["budget"] = 3.14e15
RUN_PRIMO_REQUEST_BODY_SUFFICIENT_BUDGET["general_specifications"][
    "dataset_id"
] = DATASET_ID_EXHAUSTIVE_CLUSTERING
RUN_PRIMO_REQUEST_BODY_SUFFICIENT_BUDGET["general_specifications"][
    "relative_gap"
] = 0.001
RUN_PRIMO_REQUEST_BODY_SUFFICIENT_BUDGET["general_specifications"][
    "absolute_gap"
] = 0.01


MANUAL_OVERRIDE_RECALCULATION_REQUEST_BODY = {
    **RUN_PRIMO_REQUEST_BODY,
    "child_scenario_id": 1,
    "parent_project_ids": [206, 207, 208],
    "projects_remove": [208],
    "wells_remove": {
        "206": [517, 496],
        "207": [181],
        "208": [76, 187],
    },
    "projects_lock": [207],
    "wells_lock": {"207": [85, 175, 91]},
    "wells_reassign_from": {
        "207": [181],
        "208": [76],
        "unassigned": [10, 13, 52, 55, 58],
    },
    "wells_reassign_to": {"206": [10, 13, 52, 55, 58, 181, 1], "207": [76, 517, 496]},
}

MANUAL_OVERRIDE_RECALCULATION_REQUEST_BODY_NO_IMPACT_FACTORS = {
    **RUN_PRIMO_REQUEST_BODY_NO_IMPACT_FACTORS,
    "child_scenario_id": 1,
    "parent_project_ids": [209, 210, 211],
    "projects_remove": [211],
    "wells_remove": {
        "209": [517, 496],
        "210": [181],
        "211": [76, 187],
    },
    "projects_lock": [210],
    "wells_lock": {"210": [85, 175, 91]},
    "wells_reassign_from": {
        "210": [181],
        "211": [76],
        "unassigned": [10, 13, 52, 55, 58],
    },
    "wells_reassign_to": {"209": [10, 13, 52, 55, 58, 181, 1], "210": [76, 517, 496]},
}
MANUAL_OVERRIDE_RECALCULATION_REQUEST_BODY_NO_IMPACT_FACTORS["use_cases"] = {
    "cases": ["P&A Project Recommendations"]
}

MANUAL_OVERRIDE_RECALCULATION_REQUEST_BODY_SUFFICIENT_BUDGET = {
    **RUN_PRIMO_REQUEST_BODY_SUFFICIENT_BUDGET,
    "child_scenario_id": 1,
    "parent_project_ids": [212, 213],
    "projects_remove": [],
    "wells_remove": {
        "212": [16, 19, 4, 7],
        "213": [10, 13],
    },
    "projects_lock": [],
    "wells_lock": {},
    "wells_reassign_from": {
        "212": [19, 4, 7],
        "213": [13],
        "unassigned": [],
    },
    "wells_reassign_to": {"212": [13], "213": [19, 4, 7]},
}


MANUAL_OVERRIDE_REOPTIMIZATION_CHECK_REQUEST_BODY = {
    **MANUAL_OVERRIDE_RECALCULATION_REQUEST_BODY,
    "re_optimized_project_ids": [220, 221],
}

MANUAL_OVERRIDE_REOPTIMIZATION_CHECK_REQUEST_BODY_NO_IMPACT_FACTORS = copy.deepcopy(
    MANUAL_OVERRIDE_REOPTIMIZATION_CHECK_REQUEST_BODY
)
del MANUAL_OVERRIDE_REOPTIMIZATION_CHECK_REQUEST_BODY_NO_IMPACT_FACTORS[
    "impact_factors"
]
MANUAL_OVERRIDE_REOPTIMIZATION_CHECK_REQUEST_BODY_NO_IMPACT_FACTORS[
    "general_specifications"
]["dataset_id"] = DATASET_ID_USER_PRIORITY_SCORES
MANUAL_OVERRIDE_RECALCULATION_REQUEST_BODY_NO_IMPACT_FACTORS[
    "re_optimized_project_ids"
] = [222, 223]
MANUAL_OVERRIDE_REOPTIMIZATION_CHECK_REQUEST_BODY_NO_IMPACT_FACTORS["use_cases"] = {
    "cases": ["P&A Project Recommendations"]
}

KPI_SUMMARY_BODY = {**RUN_PRIMO_REQUEST_BODY, "project_ids": [206, 207, 208]}
KPI_SUMMARY_BODY_NO_IMPACT_FACTORS = {
    **RUN_PRIMO_REQUEST_BODY_NO_IMPACT_FACTORS,
    "project_ids": [209, 210, 211],
}
KPI_SUMMARY_BODY_NO_IMPACT_FACTORS["use_cases"] = {
    "cases": ["P&A Project Recommendations"]
}
KPI_SUMMARY_BODY_NO_EFFICIENCY_FACTORS = {
    **RUN_PRIMO_REQUEST_BODY,
    "project_ids": [206, 207, 208],
}
del KPI_SUMMARY_BODY_NO_EFFICIENCY_FACTORS["efficiency_factors"]
KPI_SUMMARY_BODY_NO_EFFICIENCY_FACTORS["use_cases"] = {"cases": ["Well Ranking"]}
