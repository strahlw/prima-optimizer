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
# pylint: disable=missing-function-docstring, too-many-lines, wrong-spelling-in-comment

# Standard libs
import copy
import time

# Installed libs
import pytest
import requests

# User-defined libs
# pylint: disable=unused-import
from parameters import MONGO_RANK_COLLECTION
from tests.request_bodies import (
    DATA_AVAIL_CHECK_BODY,
    DATASET_ID,
    DATASET_ID_USER_PRIORITY_SCORES,
    INPUT_DATA_REQUEST_BODY,
    INPUT_DATA_REQUEST_BODY_EXHAUSTIVE_CLUSTERING,
    INPUT_DATA_REQUEST_BODY_USER_PRIORITY_SCORES,
    KPI_SUMMARY_BODY,
    KPI_SUMMARY_BODY_NO_EFFICIENCY_FACTORS,
    KPI_SUMMARY_BODY_NO_IMPACT_FACTORS,
    MANUAL_OVERRIDE_RECALCULATION_REQUEST_BODY,
    MANUAL_OVERRIDE_RECALCULATION_REQUEST_BODY_NO_IMPACT_FACTORS,
    MANUAL_OVERRIDE_RECALCULATION_REQUEST_BODY_SUFFICIENT_BUDGET,
    MANUAL_OVERRIDE_REOPTIMIZATION_CHECK_REQUEST_BODY,
    MANUAL_OVERRIDE_REOPTIMIZATION_CHECK_REQUEST_BODY_NO_IMPACT_FACTORS,
    NUM_BINS,
    RANK_WELLS_REQUEST_BODY,
    RANK_WELLS_REQUEST_BODY_NO_EFFICIENCY_FACTORS,
    RANK_WELLS_REQUEST_BODY_NO_IMPACT_FACTORS,
    RUN_PRIMO_REQUEST_BODY,
    RUN_PRIMO_REQUEST_BODY_NO_IMPACT_FACTORS,
    RUN_PRIMO_REQUEST_BODY_SUFFICIENT_BUDGET,
)
from utils.mongo_io import (
    collect_well_data,
    get_well_ids_data_from_wells_table,
    query_database,
)
from utils.mysql_io import get_list_of_project_data, get_map_project_ids_well_obj_str

# file:
TEST_FILE = "/usr/src/app/data_testing/test_data_random.csv"
TIMEOUT = 30
BASE_URL = "http://0.0.0.0:9090"
# run primo test 1
MYSQL_RESULTS_1 = [206, 207, 208]
# manual override recalculation
MYSQL_RESULTS_3 = [214, 215]
# manual override re-optimization
MYSQL_RESULTS_5 = [220, 221]

# run primo test 1 with user priority scores
# MYSQL_RESULTS_2 = [206, 207, 208, 209, 210]
MYSQL_RESULTS_2 = [209, 210, 211]
# run manual override recalculation with user priority scores
MYSQL_RESULTS_4 = [216, 217]
# run manual override re-optimization with user priority scores
MYSQL_RESULTS_6 = [222, 223]

# run primo with sufficient budget
MYSQL_RESULTS_7 = [212, 213]
# manual override recalculation
MYSQL_RESULTS_8 = [218, 219]


def test_container_health_check():
    response = requests.get(BASE_URL + "/ping", timeout=TIMEOUT)
    assert response.json() == "PRIMO API is running!"


def test_uptime():
    response = requests.get(BASE_URL + "/uptime", timeout=TIMEOUT).json()
    assert response["Status"] == "OK"
    assert "Uptime" in response


# simple test for the docs request
def test_swagger_docs():
    response = requests.get(BASE_URL + "/docs", timeout=TIMEOUT)
    assert "PRIMO-API" in response.text


def test_redoc_docs():
    response = requests.get(BASE_URL + "/redoc", timeout=TIMEOUT)
    assert "PRIMO-API" in response.text


def test_redis_check():
    response = requests.get(BASE_URL + "/redis_check", timeout=TIMEOUT).json()
    assert response == {"Status": "OK", "Connection Status": "Successfully connected"}


def test_mongo_check():
    response = requests.get(BASE_URL + "/mongo_check", timeout=TIMEOUT).json()
    assert response == {"Status": "OK", "Connection Status": "Successfully connected"}


@pytest.mark.parametrize(
    "request_body,contains_ranking",
    [
        (INPUT_DATA_REQUEST_BODY, False),
        (INPUT_DATA_REQUEST_BODY_USER_PRIORITY_SCORES, True),
        (INPUT_DATA_REQUEST_BODY_EXHAUSTIVE_CLUSTERING, False),
    ],
)
def test_data_input_check(request_body, contains_ranking):
    response = requests.post(
        BASE_URL + "/data_input_check", timeout=TIMEOUT, json=request_body
    )
    assert response.json()["status"] == "SUCCESS"

    # actually check that the data is in the database
    data = collect_well_data(request_body["dataset_id"], ["Gas", "Oil", "Combined"])
    if (
        request_body["file_path"]
        == INPUT_DATA_REQUEST_BODY_EXHAUSTIVE_CLUSTERING["file_path"]
    ):
        assert len(data) == 20
    else:
        assert len(data) == 571
    assert len(data.columns) == 75
    assert response.json()["contains_ranking"] is contains_ranking


# pylint: disable=duplicate-code
def test_check_available_data():
    """
    Runs check_available_data endpoint and tests for
    a correct and successful response.
    """
    response = requests.post(
        BASE_URL + "/check_for_avail_data", timeout=TIMEOUT, json=DATA_AVAIL_CHECK_BODY
    )
    # Check to make sure the endpoint succeeded
    assert response.json()["status"] == "SUCCESS"

    expected_impact_factors_result = {
        "well_age": {"value": 0, "selected": True},
        "losses": {
            "value": 0,
            "selected": True,
            "child_factors": {
                "leak": {"value": 0, "selected": True},
                "violation": {"value": 0, "selected": True},
                "compliance": {"value": 0, "selected": True},
                "incident": {"value": 0, "selected": True},
                "hydrocarbon_losses": {"value": 0, "selected": True},
            },
        },
        "sensitive_receptors": {
            "value": 0,
            "selected": True,
            "child_factors": {
                "schools": {"value": 0, "selected": True},
                "hospitals": {"value": 0, "selected": True},
                "agriculture_area_nearby": {"value": 0, "selected": True},
                "buildings_far": {"value": 0, "selected": True},
                "buildings_near": {"value": 0, "selected": True},
            },
        },
        "owner_well_count": {"value": 0, "selected": True},
        "environment": {
            "value": 0,
            "selected": True,
            "child_factors": {
                "water_source_nearby": {"value": 0, "selected": True},
                "known_soil_or_water_impact": {"value": 0, "selected": True},
                "fed_wetlands_near": {"value": 0, "selected": True},
                "fed_wetlands_far": {"value": 0, "selected": True},
                "state_wetlands_near": {"value": 0, "selected": True},
                "state_wetlands_far": {"value": 0, "selected": True},
            },
        },
        "ecological_receptors": {
            "value": 1,
            "selected": True,
            "child_factors": {
                "endangered_species_on_site": {"value": 100, "selected": True}
            },
        },
        "other_losses": {
            "value": 43,
            "selected": True,
            "child_factors": {
                "brine_leak": {"value": 50, "selected": True},
                "h2s_leak": {"value": 50, "selected": True},
            },
        },
        "five_year_production_volume": {
            "value": 2,
            "selected": True,
            "child_factors": {
                "five_year_gas_production": {"value": 50, "selected": True},
                "five_year_oil_production": {"value": 50, "selected": True},
            },
        },
        "lifelong_production_volume": {
            "value": 2,
            "selected": True,
            "child_factors": {
                "lifelong_gas_production": {"value": 50, "selected": True},
                "lifelong_oil_production": {"value": 50, "selected": True},
            },
        },
        "ann_production_volume": {
            "value": 2,
            "selected": True,
            "child_factors": {
                "ann_gas_production": {"value": 50, "selected": True},
                "ann_oil_production": {"value": 50, "selected": True},
            },
        },
        "site_considerations": {
            "value": 4,
            "selected": True,
            "child_factors": {
                "historical_preservation_site": {"value": 20, "selected": True},
                "home_use_gas_well": {"value": 30, "selected": True},
                "post_plugging_land_use": {"value": 25, "selected": True},
                "surface_equipment_on_site": {"value": 25, "selected": True},
            },
        },
        "cost_of_plugging": {"value": 0, "selected": True},
        "high_pressure_observed": {"value": 0, "selected": True},
        "idle_status_duration": {"value": 0, "selected": True},
        "in_tribal_land": {"value": 0, "selected": True},
        "likely_to_be_orphaned": {"value": 0, "selected": True},
        "number_of_mcws_nearby": {"value": 0, "selected": True},
        "mechanical_integrity_test": {"value": 0, "selected": True},
        "otherwise_incentivized_well": {"value": 0, "selected": True},
        "well_integrity": {"value": 0, "selected": True},
        "placeholder_one": {"value": 0, "selected": True},
        "placeholder_two": {"value": 0, "selected": True},
        "placeholder_three": {"value": 0, "selected": True},
        "placeholder_four": {"value": 0, "selected": True},
        "placeholder_five": {"value": 0, "selected": True},
        "placeholder_six": {"value": 0, "selected": True},
        "placeholder_seven": {"value": 0, "selected": True},
        "placeholder_eight": {"value": 0, "selected": True},
        "placeholder_nine": {"value": 0, "selected": True},
        "placeholder_ten": {"value": 0, "selected": True},
        "placeholder_eleven": {"value": 0, "selected": True},
        "placeholder_twelve": {"value": 0, "selected": True},
        "placeholder_thirteen": {"value": 0, "selected": True},
        "placeholder_fourteen": {"value": 0, "selected": True},
        "placeholder_fifteen": {"value": 0, "selected": True},
        "placeholder_sixteen": {"value": 0, "selected": True},
        "placeholder_seventeen": {"value": 0, "selected": True},
        "placeholder_eighteen": {"value": 0, "selected": True},
        "placeholder_nineteen": {"value": 0, "selected": True},
        "placeholder_twenty": {"value": 0, "selected": True},
    }
    expected_eff_factors_result = {
        "age_range": {
            "selected": True,
            "value": 0,
        },
        "distance_range": {
            "selected": True,
            "value": 0,
        },
        "num_wells": {
            "selected": True,
            "value": 0,
        },
        "depth_range": {
            "selected": True,
            "value": 0,
        },
        "avg_distance_to_nearest_road": {
            "selected": True,
            "value": 0,
        },
        "avg_elevation_change_from_nearest_road": {
            "selected": True,
            "value": 0,
        },
        "population_density": {
            "selected": True,
            "value": 0,
        },
    }
    # Grab results as a JSON from the response
    impact_factors_result = response.json()["impact_factors"]
    eff_factors_result = response.json()["efficiency_factors"]

    # Check to see that all impact factors were correctly selected as True/False or None
    for factor in impact_factors_result.keys():
        if "child_factors" in impact_factors_result[factor]:
            for child_factor in impact_factors_result[factor]["child_factors"].keys():

                assert (
                    impact_factors_result[factor]["child_factors"][child_factor][
                        "selected"
                    ]
                    == expected_impact_factors_result[factor]["child_factors"][
                        child_factor
                    ]["selected"]
                )

        assert (
            impact_factors_result[factor]["selected"]
            == expected_impact_factors_result[factor]["selected"]
        )

    # Check to see that all efficiency factors were correctly selected as True/False or None
    for factor in eff_factors_result.keys():
        assert (
            eff_factors_result[factor]["selected"]
            == expected_eff_factors_result[factor]["selected"]
        )


def test_data_summary():
    """
    Test for data_summary endpoint
    """
    response = requests.get(
        BASE_URL + f"/data_summary/{DATASET_ID}/{NUM_BINS}", timeout=TIMEOUT
    )
    assert response.json()["status"] == "SUCCESS"
    data = response.json()["data"]

    # Top-level checks
    assert isinstance(data, list)
    assert len(data) == 2

    summary = data[0]
    histograms = data[1]

    # Wells summary
    assert summary["wells"]["num_all_wells"] == 571
    assert summary["wells"]["num_gas_wells"] == 190
    assert summary["wells"]["num_oil_wells"] == 191
    assert summary["wells"]["num_combined_wells"] == 190
    assert summary["wells"]["average_wells_per_operator"] == 1.0

    # Depth summary
    assert summary["depth"]["average_depth"] == 715
    assert summary["depth"]["max_depth"] == 1000.00
    assert summary["depth"]["min_depth"] == 430.00
    assert summary["depth"]["range_depth"] == 570.00

    # Age summary
    assert summary["age"]["average_age"] == 105
    assert summary["age"]["range_age"] == 225.00

    # Histograms (expecting empty lists)
    assert histograms["histogram_age_x"] == [
        "0-22",
        "22-45",
        "45-67",
        "67-90",
        "90-112",
        "112-135",
        "135-157",
        "157-180",
        "180-202",
        "202-225",
    ]
    assert histograms["histogram_age_y"] == [71, 57, 63, 66, 57, 49, 58, 51, 48, 51]
    assert histograms["histogram_depth_x"] == [
        "430-487",
        "487-544",
        "544-601",
        "601-658",
        "658-715",
        "715-772",
        "772-829",
        "829-886",
        "886-943",
        "943-1000",
    ]
    assert histograms["histogram_depth_y"] == [57, 57, 57, 57, 57, 57, 57, 57, 57, 58]


def check_rank_well_results(response, request_body):
    """
    Checks well ranking data
    """
    user_supplied_scores = (
        request_body["general_specifications"]["dataset_id"]
        == DATASET_ID_USER_PRIORITY_SCORES
    )
    task_id = response.json()["id"]
    query = {"task_id": task_id}
    well_ranking_data = query_database(query, collection_id=MONGO_RANK_COLLECTION)
    assert len(well_ranking_data) == 191
    # check details of wells in mongo db - ensure correct integration
    for obj in well_ranking_data:
        if obj["well_id"] == 517:
            if not user_supplied_scores:
                assert obj["well_rank"] == pytest.approx(1)
                assert obj["leak_score"] == pytest.approx(10)
                assert obj["violation_score"] == pytest.approx(10)
                assert obj["state_wetlands_near_score"] == pytest.approx(0)
                assert obj["well_age_score"] == pytest.approx(18.2648401826484)
                assert obj["owner_well_count_score"] == pytest.approx(10)
                assert obj["hospitals_score"] == pytest.approx(0)
                assert obj["schools_score"] == pytest.approx(0)
                assert obj["life_gas_production_score"] == pytest.approx(
                    17.818369808719627
                )
            assert obj["priority_score"] == pytest.approx(66.08320999136802)

        if obj["well_id"] == 496:
            assert obj["well_rank"] == 2
            assert obj["priority_score"] == pytest.approx(63.81189229000587)

        if obj["well_id"] == 487:
            assert obj["well_rank"] == 6
            assert obj["priority_score"] == pytest.approx(59.86398941816428)

        if obj["well_id"] == 553:
            assert obj["well_rank"] == 58
            assert obj["priority_score"] == pytest.approx(45.38730950846554)

        # project 1
        if obj["well_id"] == 85:
            assert obj["well_rank"] == 4
            assert obj["priority_score"] == pytest.approx(62.318144370295)
        if obj["well_id"] == 181:
            assert obj["well_rank"] == 8
            assert obj["priority_score"] == pytest.approx(58.73405898539332)
        if obj["well_id"] == 175:
            assert obj["well_rank"] == 11
            assert obj["priority_score"] == pytest.approx(57.56694104844211)


def test_check_request_bodies():
    """
    Check to make sure the request bodies are correct
    """
    assert "efficiency_factors" not in RANK_WELLS_REQUEST_BODY_NO_EFFICIENCY_FACTORS
    assert "impact_factors" not in INPUT_DATA_REQUEST_BODY_USER_PRIORITY_SCORES
    assert "impact_factors" not in RUN_PRIMO_REQUEST_BODY_NO_IMPACT_FACTORS
    assert (
        "impact_factors"
        not in MANUAL_OVERRIDE_RECALCULATION_REQUEST_BODY_NO_IMPACT_FACTORS
    )
    assert (
        "impact_factors"
        not in MANUAL_OVERRIDE_REOPTIMIZATION_CHECK_REQUEST_BODY_NO_IMPACT_FACTORS
    )


@pytest.mark.parametrize(
    "request_body",
    [
        (RANK_WELLS_REQUEST_BODY_NO_IMPACT_FACTORS),
        (RANK_WELLS_REQUEST_BODY),
        (RANK_WELLS_REQUEST_BODY_NO_EFFICIENCY_FACTORS),
    ],
)
def test_rank_wells(request_body):
    """
    Runs rank wells endpoint
    Checks mongo db for correct results
    """
    response = requests.post(
        BASE_URL + "/rank_wells", timeout=TIMEOUT, json=request_body
    )
    # print(response.json()["detail"])
    assert response.json()["status"] == "SUCCESS"
    check_rank_well_results(response, request_body)


# , 100/52.130271147737305, 26.765521330376462300189592805606
@pytest.mark.parametrize(
    "request_body",
    [
        (RUN_PRIMO_REQUEST_BODY),
        (RUN_PRIMO_REQUEST_BODY_NO_IMPACT_FACTORS),
        (RUN_PRIMO_REQUEST_BODY_SUFFICIENT_BUDGET),
    ],
)
def test_run_primo(request_body):
    response = requests.post(
        BASE_URL + "/run_primo", timeout=TIMEOUT, json=request_body
    )
    response_data = response.json()
    # print(response.json())
    # assert False
    assert response_data["status"] == "PENDING"

    # check every 5 seconds if it has completed
    while True:
        status = requests.get(
            BASE_URL + f"/status/{response_data['id']}", timeout=TIMEOUT
        ).json()["status"]

        if status not in ("PROCESSING", "PENDING"):
            break

        time.sleep(5)

    assert (
        requests.get(
            BASE_URL + f"/status/{response_data['id']}", timeout=TIMEOUT
        ).json()["status"]
        == "SUCCESS"
    )


def test_run_primo_no_budget():
    run_primo_request_body_no_budget = copy.deepcopy(RUN_PRIMO_REQUEST_BODY)
    del run_primo_request_body_no_budget["general_specifications"]["budget"]
    response = requests.post(
        BASE_URL + "/run_primo", timeout=TIMEOUT, json=run_primo_request_body_no_budget
    )
    response_data = response.json()
    assert response_data["detail"] == "The budget was not included in the request body."


# pylint: disable=too-many-branches
def test_run_primo_results():
    # checks the entries of the wells mysql table
    project_well_id_obj_str_map = get_map_project_ids_well_obj_str(MYSQL_RESULTS_1)
    for project, wells in project_well_id_obj_str_map.items():
        well_data = get_well_ids_data_from_wells_table(wells)
        if project == MYSQL_RESULTS_1[0]:
            assert list(well_data.keys()) == [
                517,
                496,
                487,
                541,
                547,
                31,
                100,
                334,
                142,
                424,
            ]
        if project == MYSQL_RESULTS_1[1]:
            assert list(well_data.keys()) == [85, 181, 175, 91]
        if project == MYSQL_RESULTS_1[2]:
            assert list(well_data.keys()) == [76, 187]

        # # check the actual well data in the MONGO_WELL_COLLECTION
        if project == MYSQL_RESULTS_1[0]:
            for well in well_data.values():
                assert well["cluster_id"] == 0

        if project == MYSQL_RESULTS_1[1]:
            for well_id, well in well_data.items():
                assert well["cluster_id"] == 1
                if well_id == 85:
                    assert well["priority_score"] == pytest.approx(62.318144370295)
                if well_id == 181:
                    assert well["priority_score"] == pytest.approx(58.734058985393325)
                if well_id == 175:
                    assert well["priority_score"] == pytest.approx(57.56694104844211)

        if project == MYSQL_RESULTS_1[2]:
            for well in well_data.values():
                assert well["cluster_id"] == 2

    # check the entries to the project mysql table
    project_data = get_list_of_project_data(MYSQL_RESULTS_1)
    for project_id, project_scores in project_data.items():
        if project_id == MYSQL_RESULTS_1[0]:
            assert project_scores["impact_score"] == pytest.approx(
                56.43002871093883, rel=1e-3
            )
            assert project_scores["efficiency_score"] == pytest.approx(
                25.779930279828303, rel=1e-3
            )
        if project_id == MYSQL_RESULTS_1[1]:
            assert project_scores["impact_score"] == pytest.approx(
                58.663931111053415, rel=1e-3
            )
            assert project_scores["efficiency_score"] == pytest.approx(
                55.74566988620547, rel=1e-3
            )
        if project_id == MYSQL_RESULTS_1[2]:
            assert project_scores["impact_score"] == pytest.approx(
                61.14462130672452, rel=1e-3
            )
            assert project_scores["efficiency_score"] == pytest.approx(
                60.47090249707765, rel=1e-3
            )


# pylint: disable=too-many-branches
def test_run_primo_results_user_input_priority_scores():
    # checks the entries of the wells mysql table
    project_well_id_obj_str_map = get_map_project_ids_well_obj_str(MYSQL_RESULTS_2)
    for project, wells in project_well_id_obj_str_map.items():
        well_data = get_well_ids_data_from_wells_table(wells)
        if project == MYSQL_RESULTS_2[0]:
            assert list(well_data.keys()) == [
                517,
                496,
                487,
                541,
                547,
                31,
                100,
                334,
                142,
                424,
            ]
        if project == MYSQL_RESULTS_2[1]:
            assert list(well_data.keys()) == [85, 181, 175, 91]
        if project == MYSQL_RESULTS_2[2]:
            assert list(well_data.keys()) == [76, 187]

        # # check the actual well data in the MONGO_WELL_COLLECTION
        if project == MYSQL_RESULTS_2[0]:
            for well in well_data.values():
                assert well["cluster_id"] == 0

        if project == MYSQL_RESULTS_2[1]:
            for well_id, well in well_data.items():
                assert well["cluster_id"] == 1
                if well_id == 85:
                    assert well["priority_score"] == pytest.approx(62.318144370295)
                if well_id == 181:
                    assert well["priority_score"] == pytest.approx(58.734058985393325)
                if well_id == 175:
                    assert well["priority_score"] == pytest.approx(57.56694104844211)

        if project == MYSQL_RESULTS_2[2]:
            for well in well_data.values():
                assert well["cluster_id"] == 2

    # check the entries to the project mysql table
    project_data = get_list_of_project_data(MYSQL_RESULTS_2)
    impact_scores = [
        81.48257996160451,
        85.7678106907372,
        90.52644734804915,
    ]
    efficiency_scores = [
        25.779930279828303,
        55.74566988620547,
        60.47090249707765,
    ]
    for idx, (_, project_scores) in enumerate(project_data.items()):
        assert project_scores["impact_score"] == pytest.approx(
            impact_scores[idx], rel=1e-3
        )
        assert project_scores["efficiency_score"] == pytest.approx(
            efficiency_scores[idx], rel=1e-3
        )


def test_run_primo_budget_sufficient():
    # checks the entries of the wells mysql table
    project_well_id_obj_str_map = get_map_project_ids_well_obj_str(MYSQL_RESULTS_7)
    for project, wells in project_well_id_obj_str_map.items():
        well_data = get_well_ids_data_from_wells_table(wells)
        if project == MYSQL_RESULTS_7[0]:
            assert list(well_data.keys()) == [16, 19, 4, 1, 7]
        if project == MYSQL_RESULTS_7[1]:
            assert list(well_data.keys()) == [10, 13]

    # check the entries to the project mysql table
    project_data = get_list_of_project_data(MYSQL_RESULTS_7)
    impact_scores = [
        41.063313758751214,
        26.55559147349155,
    ]
    efficiency_scores = [
        13.90386155717962,
        44.67102773415527,
    ]
    for idx, (_, project_scores) in enumerate(project_data.items()):
        assert project_scores["impact_score"] == pytest.approx(
            impact_scores[idx], rel=1e-3
        )
        assert project_scores["efficiency_score"] == pytest.approx(
            efficiency_scores[idx], rel=1e-3
        )


@pytest.mark.parametrize(
    "request_body",
    [(RUN_PRIMO_REQUEST_BODY), (RUN_PRIMO_REQUEST_BODY_NO_IMPACT_FACTORS)],
)
def test_valid_well_ids(request_body):

    # base case test
    response = requests.post(
        BASE_URL + "/valid_well_ids",
        timeout=TIMEOUT,
        json=request_body,
    )
    assert response.json()["status"] == "SUCCESS"
    assert 1 in response.json()["data"]
    assert len(response.json()["data"]) == 191
    # test for min_lifetime_gas_production
    request_1 = copy.deepcopy(request_body)
    request_1["general_specifications"]["min_lifetime_gas_production"] = 597

    response = requests.post(
        BASE_URL + "/valid_well_ids",
        timeout=TIMEOUT,
        json=request_1,
    )
    assert response.json()["status"] == "SUCCESS"
    assert 1 not in response.json()["data"]
    assert len(response.json()["data"]) == 83

    # test for max_lifetime_gas_production
    request_2 = copy.deepcopy(request_body)
    request_2["general_specifications"]["max_lifetime_gas_production"] = 595

    response = requests.post(
        BASE_URL + "/valid_well_ids",
        timeout=TIMEOUT,
        json=request_2,
    )
    assert response.json()["status"] == "SUCCESS"
    assert 1 not in response.json()["data"]
    assert len(response.json()["data"]) == 107

    # test for min_lifetime_oil_production
    request_3 = copy.deepcopy(request_body)
    request_3["general_specifications"]["min_lifetime_oil_production"] = 195

    response = requests.post(
        BASE_URL + "/valid_well_ids",
        timeout=TIMEOUT,
        json=request_3,
    )
    assert response.json()["status"] == "SUCCESS"
    assert 1 not in response.json()["data"]
    assert len(response.json()["data"]) == 24

    # test for man_lifetime_oil_production
    request_4 = copy.deepcopy(request_body)
    request_4["general_specifications"]["max_lifetime_oil_production"] = 193

    response = requests.post(
        BASE_URL + "/valid_well_ids",
        timeout=TIMEOUT,
        json=request_4,
    )
    assert response.json()["status"] == "SUCCESS"
    assert 1 not in response.json()["data"]
    assert len(response.json()["data"]) == 163

    # sanity test
    request_5 = copy.deepcopy(request_body)

    response = requests.post(
        BASE_URL + "/valid_well_ids",
        timeout=TIMEOUT,
        json=request_5,
    )
    assert response.json()["status"] == "SUCCESS"
    assert 1 in response.json()["data"]
    assert len(response.json()["data"]) == 191


@pytest.mark.parametrize(
    "request_body",
    [
        (MANUAL_OVERRIDE_RECALCULATION_REQUEST_BODY),
        (MANUAL_OVERRIDE_RECALCULATION_REQUEST_BODY_NO_IMPACT_FACTORS),
        (MANUAL_OVERRIDE_RECALCULATION_REQUEST_BODY_SUFFICIENT_BUDGET),
    ],
)
def test_manual_override_recalculation(request_body):
    response = requests.post(
        BASE_URL + "/manual_override_recalculation",
        timeout=TIMEOUT,
        json=request_body,
    )
    assert response.json()["status"] == "SUCCESS"


@pytest.mark.parametrize(
    "results",
    [
        (MYSQL_RESULTS_3),
        (MYSQL_RESULTS_4),
    ],
)
def test_manual_override_recalculation_results(results):
    project_well_id_obj_str_map = get_map_project_ids_well_obj_str(results)
    for project, wells in project_well_id_obj_str_map.items():
        well_data = get_well_ids_data_from_wells_table(wells)
        if project == results[0]:
            assert all(
                well_id
                in [487, 541, 547, 31, 100, 334, 142, 424, 181, 10, 1, 52, 55, 13, 58]
                for well_id in list(well_data.keys())
            )
            assert len(list(well_data.keys())) == 15

        if project == results[1]:
            assert all(
                well_id in [517, 496, 76, 85, 175, 91]
                for well_id in list(well_data.keys())
            )
            assert len(list(well_data.keys())) == 6

    # check the entries to the project mysql table
    project_data = get_list_of_project_data(results)
    if results[0] == 214:
        for project_id, project_scores in project_data.items():
            if project_id == results[0]:
                assert project_scores["impact_score"] == pytest.approx(
                    44.64017273109922, rel=1e-3
                )
                assert project_scores["efficiency_score"] == pytest.approx(
                    18.50495439249788, rel=1e-3
                )
            if project_id == results[1]:
                assert project_scores["impact_score"] == pytest.approx(
                    61.54849706405468, rel=1e-3
                )
                assert project_scores["efficiency_score"] == pytest.approx(
                    29.438980475072704, rel=1e-3
                )
    else:
        for project_id, project_scores in project_data.items():
            if project_id == results[0]:
                assert project_scores["impact_score"] == pytest.approx(
                    58.866438286947854, rel=1e-3
                )
                assert project_scores["efficiency_score"] == pytest.approx(
                    18.50495439249788, rel=1e-3
                )
            if project_id == results[1]:
                assert project_scores["impact_score"] == pytest.approx(
                    91.30119060071938, rel=1e-3
                )
                assert project_scores["efficiency_score"] == pytest.approx(
                    29.438980475072704, rel=1e-3
                )


def test_manual_override_recalculation_results_budget_sufficient():
    project_well_id_obj_str_map = get_map_project_ids_well_obj_str(MYSQL_RESULTS_8)
    for project, wells in project_well_id_obj_str_map.items():
        well_data = get_well_ids_data_from_wells_table(wells)
        if project == MYSQL_RESULTS_8[0]:
            assert all(well_id in [1, 13] for well_id in list(well_data.keys()))
            assert len(list(well_data.keys())) == 2

        if project == MYSQL_RESULTS_8[1]:
            assert all(well_id in [19, 4, 7] for well_id in list(well_data.keys()))
            assert len(list(well_data.keys())) == 3

    project_data = get_list_of_project_data(MYSQL_RESULTS_8)
    impact_scores = [
        24.568382631277156,
        37.045687194096324,
    ]
    efficiency_scores = [
        24.119565217391305,
        22.960383296310056,
    ]
    for idx, (_, project_scores) in enumerate(project_data.items()):
        assert project_scores["impact_score"] == pytest.approx(
            impact_scores[idx], rel=1e-3
        )
        assert project_scores["efficiency_score"] == pytest.approx(
            efficiency_scores[idx], rel=1e-3
        )


@pytest.mark.parametrize(
    "request_body,dollars,distance_violation_expected,project_num_expected,project_length_expected",
    [
        (MANUAL_OVERRIDE_RECALCULATION_REQUEST_BODY, 937169, 35, 0, 15),
        (
            MANUAL_OVERRIDE_RECALCULATION_REQUEST_BODY_NO_IMPACT_FACTORS,
            937169,
            35,
            0,
            15,
        ),
    ],
)
def test_manual_override_recalculation_check(
    request_body,
    dollars,
    distance_violation_expected,
    project_num_expected,
    project_length_expected,
):
    response = requests.post(
        BASE_URL + "/manual_override_recalculation_check",
        timeout=TIMEOUT,
        json=request_body,
    )
    assert response.json()["status"] == "SUCCESS"

    # obtain the violation information
    violation_info = response.json()["data"]

    assert violation_info["Project Status:"] == "CONSTRAINT(S) VIOLATED"
    assert len(violation_info) == 4
    assert f"${dollars}" in list(violation_info.keys())[1]
    distance_violation = list(violation_info.values())[2]
    assert all(isinstance(item, dict) for item in distance_violation)
    assert distance_violation[0]["Well 1"] == 487
    assert distance_violation[0]["Well 2"] == 58
    assert len(distance_violation) == distance_violation_expected
    num_well_violation = list(violation_info.values())[3]
    assert num_well_violation[0]["Project"] == project_num_expected
    assert num_well_violation[0]["Length"] == project_length_expected


# @pytest.mark.parametrize(
#     "request_body",
#     [
#         (MANUAL_OVERRIDE_RECALCULATION_REQUEST_BODY),
#         (MANUAL_OVERRIDE_RECALCULATION_REQUEST_BODY_NO_IMPACT_FACTORS),
#     ],
# )
# def test_manual_override_reoptimization(request_body):
#     response = requests.post(
#         BASE_URL + "/manual_override_reoptimization",
#         timeout=TIMEOUT,
#         json=request_body,
#     )
#     response_data = response.json()

#     assert response_data["status"] == "PENDING"

#     # check every 5 seconds if it has completed
#     while True:
#         status = requests.get(
#             BASE_URL + f"/status/{response_data['id']}", timeout=TIMEOUT
#         ).json()["status"]

#         if status not in ("PROCESSING", "PENDING"):
#             break

#         time.sleep(5)

#     assert (
#         requests.get(
#             BASE_URL + f"/status/{response_data['id']}", timeout=TIMEOUT
#         ).json()["status"]
#         == "SUCCESS"
#     )


# # These results are using SCIP 9.2.2. We have seen inconsistent
# # test results based on the solution of the optimizer at termination.
# @pytest.mark.parametrize(
#     "mysql_results,index,impact_score,efficiency_score,well_in_project",
#     [
#         (
#             MYSQL_RESULTS_5,
#             0,
#             33.5996294513972,
#             40.68949465335743,
#             [181, 10, 1, 52, 55, 13, 58],
#         ),
#         (
#             MYSQL_RESULTS_5,
#             1,
#             61.548497062178456,
#             29.561787492616567,
#             [517, 496, 76, 85, 175, 91],
#         ),
#         (
#             MYSQL_RESULTS_6,
#             1,
#             37.687681608878684,
#             40.68949465335743,
#             [181, 10, 1, 52, 55, 13, 58],
#         ),
#         (
#             MYSQL_RESULTS_6,
#             0,
#             58.57696026855632,
#             59.737729537724675,
#             [16, 127],
#         ),
#     ],
# )
# def test_manual_override_reoptimization_result(
#     mysql_results, index, impact_score, efficiency_score, well_in_project
# ):
#     # check the impact score and efficiency score of each project
#     project_data = get_list_of_project_data([mysql_results[index]])
#     assert mysql_results[index] in project_data
#     project_status = project_data[mysql_results[index]]
#     assert project_status["impact_score"] == pytest.approx(impact_score, rel=1e-3)
#     assert project_status["efficiency_score"] == pytest.approx(
#         efficiency_score, rel=1e-3
#     )

#     # check the number of projects being selected in the re-optimization results
#     project_well_id_obj_str_map = get_map_project_ids_well_obj_str(mysql_results)
#     assert len(project_well_id_obj_str_map) == 2

#     # check wells in each project
#     project_well_id_obj_str_map = get_map_project_ids_well_obj_str(
#         [mysql_results[index]]
#     )
#     ((_, wells),) = project_well_id_obj_str_map.items()
#     well_data = get_well_ids_data_from_wells_table(wells)
#     assert set(well_data) == set(well_in_project)

#     # check wells being removed
#     assert 187 not in well_data


# @pytest.mark.parametrize(
#     "request_body",
#     [
#         (MANUAL_OVERRIDE_REOPTIMIZATION_CHECK_REQUEST_BODY),
#         (MANUAL_OVERRIDE_REOPTIMIZATION_CHECK_REQUEST_BODY_NO_IMPACT_FACTORS),
#     ],
# )
# def test_manual_override_reoptimization_check(request_body):
#     response = requests.post(
#         BASE_URL + "/manual_reoptimization_check",
#         timeout=TIMEOUT,
#         json=request_body,
#     )
#     assert response.json()["status"] == "SUCCESS"

#     # obtain the violation information
#     violation_info = response.json()["data"]

#     assert violation_info["Project Status:"] == "CONSTRAINT(S) VIOLATED"
#     assert len(violation_info) == 2
#     assert "$937169" not in list(violation_info.keys())[1]
#     distance_violation = list(violation_info.values())[1]
#     assert all(isinstance(item, dict) for item in distance_violation)
#     assert distance_violation[0]["Well 1"] == 517
#     assert distance_violation[0]["Well 2"] == 52
#     assert len(distance_violation) == 18


KPI_SUMMARY_BODY_RESULTS = {
    "num_candidate_wells": 191,
    "num_oil_wells": 191,
    "num_gas_wells": 0,
    "num_combined_wells": 0,
    "cost": 3987465.175050278,
    "budget_remaining": 12534.824949721806,
    "priority_impact_score_min": 56.43002871093883,
    "priority_impact_score_max": 61.14462130672452,
    "priority_impact_score_avg": 58.74619370850058,
    "efficiency_score_min": 25.779930279828303,
    "efficiency_score_max": 60.47090249707765,
    "efficiency_score_avg": 47.33216755437047,
    "overall_impact_weight": None,
    "overall_efficiency_weight": None,
    "num_projects": 3,
}
KPI_SUMMARY_BODY_NO_IMPACT_FACTORS_RESULTS = {
    "num_candidate_wells": 191,
    "num_oil_wells": 191,
    "num_gas_wells": 0,
    "num_combined_wells": 0,
    "cost": 3987465.175050278,
    "budget_remaining": 12534.824949721806,
    "priority_impact_score_min": 81.48257996160451,
    "priority_impact_score_max": 90.52644734804915,
    "priority_impact_score_avg": 85.92561266679695,
    "efficiency_score_min": 25.779930279828303,
    "efficiency_score_max": 60.47090249707765,
    "efficiency_score_avg": 47.33216755437047,
    "overall_impact_weight": None,
    "overall_efficiency_weight": None,
    "num_projects": 3,
}
KPI_SUMMARY_BODY_NO_EFFICIENCY_FACTORS_RESULTS = {
    "num_candidate_wells": 191,
    "num_oil_wells": 191,
    "num_gas_wells": 0,
    "num_combined_wells": 0,
    "cost": None,
    "budget_remaining": None,
    "priority_impact_score_min": 13.952938843630715,
    "priority_impact_score_max": 66.08320999136802,
    "priority_impact_score_avg": 39.92541810646991,
    "efficiency_score_min": None,
    "efficiency_score_max": None,
    "efficiency_score_avg": None,
    "overall_impact_weight": None,
    "overall_efficiency_weight": None,
    "num_projects": None,
}


@pytest.mark.parametrize(
    "request_body,expected_result",
    [
        (KPI_SUMMARY_BODY, KPI_SUMMARY_BODY_RESULTS),
        (
            KPI_SUMMARY_BODY_NO_IMPACT_FACTORS,
            KPI_SUMMARY_BODY_NO_IMPACT_FACTORS_RESULTS,
        ),
        (
            KPI_SUMMARY_BODY_NO_EFFICIENCY_FACTORS,
            KPI_SUMMARY_BODY_NO_EFFICIENCY_FACTORS_RESULTS,
        ),
    ],
)
def test_kpi_summary(request_body, expected_result):
    response = requests.post(
        BASE_URL + "/kpi_summary",
        timeout=TIMEOUT,
        json=request_body,
    )
    # print(response.json()["detail"])
    assert response.json()["status"] == "SUCCESS"

    final_output = response.json()["data"]

    # check result
    for key in final_output:
        if final_output[key] is None:
            assert expected_result[key] is None
        else:
            assert final_output[key] == pytest.approx(expected_result[key])
