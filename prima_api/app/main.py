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
# pylint: disable=too-many-lines
"""
Implements the main body of the PRIMO API
"""
# Standard libs
import copy
import datetime
import functools
import json
import logging
import traceback
import uuid
from types import SimpleNamespace

# pylint: disable=no-name-in-module
from typing import Annotated, Dict, Union

# Installed libs
import fastapi
import pandas as pd
import pymongo
import redis
import uvicorn
from fastapi import Body, HTTPException, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from primo.data_parser.input_config import ScenarioType

# pylint: disable=no-name-in-module
from primo.data_parser.well_data import WellData
from primo.utils.override_utils import AssessFeasibility
from pymongo import MongoClient

# User-defined libs
from app_setup import initialize_app
from parameters import (
    DATA_INPUT_CHECK_EXAMPLE,
    EFFICIENCY_FACTORS,
    FULL_LIST_IMPACT_FACTORS,
    GENERAL_SPECIFICATIONS,
    INVALID_METRIC_SELECTIONS,
    KPI_SUMMARY_EXAMPLE,
    MANUAL_OVERRIDE_REQUEST_EXAMPLE,
    MONGO_DATABASE,
    MONGO_DATASET_COLLECTION,
    MONGO_RANK_COLLECTION,
    MONGO_URI,
    RANKWELLS_PARAM_EXAMPLE,
    REDIS_HOST,
    REDIS_PORT,
    SCENARIO_PARAM_EXAMPLE,
    START_TIME,
    SUCCESSFUL_CONNECTION,
    TASK_NOT_FOUND,
    WELL_DATA_NOT_FOUND,
)
from primo_executor.primo_queue_manager import (
    QUEUE_APP,
    add_job_to_queue,
    get_primo_job_status,
    kill_primo_job,
    run_primo_instance,
)
from primo_executor.primo_worker import (
    construct_override_campaign,
    create_histogram,
    create_mobilization_cost,
    handle_general_specifications_well_data,
    infer_use_case_type,
    metric_data_check,
    retrieve_well_data,
    verify_parameter_validity,
)
from primo_executor.primo_worker_parameters import get_well_data_columns
from utils import COLUMN_MAP
from utils.data_parsing import validate_data
from utils.models import (
    DataAvailCheckResults,
    DataInputCheckResponse,
    DataSummaryResults,
    GeneralSpecifications,
    KPISummaryRequest,
    KPISummaryResponse,
    ManualOverrideRequest,
    OptimizerResults,
    OverrideRecalculationCheckResponse,
    OverrideReoptimizationCheckRequest,
    OverrideReoptimizationCheckResponse,
    PrimoResponse,
    RankResults,
    RankWellsParameters,
    ScenarioParameters,
    Status,
    ValidateDataRequest,
    ValidWellIdsResults,
)
from utils.mongo_io import (
    convert_rank_results,
    get_map_of_well_ids_in_wells_table,
    insert_data,
    remove_rank_results,
)
from utils.mysql_io import (
    get_list_of_project_data,
    get_map_project_ids_well_obj_str,
    get_wells_ids_from_project_id,
)
from utils.result_format_util import process_override_results
from utils.valid_inputs import is_valid_scenario_dependent

LOGGER = logging.getLogger(__name__)

app, swagger_ui_html, redoc_ui_html = initialize_app()
LOGGER.info("PRIMO API initialized!")


def robust_endpoint(status_code=422):
    """
    A decorator factory wraps the target function in a try/except block and reports
    exception as an error.

    Returns
    -------
    decorator
        A decorator to be applied to functions.
    """

    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as exc:
                raise HTTPException(
                    status_code=status_code,
                    detail=traceback.format_exc(),
                ) from exc

        return wrapper

    return decorator


@app.get("/docs", include_in_schema=False)
def swagger_docs():
    """
    Override swagger documentation to include a favicon
    """
    return swagger_ui_html


@app.get("/redoc", include_in_schema=False)
def redoc_docs():
    """
    Override redoc documentation to include a favicon
    """
    return redoc_ui_html


@app.get(
    "/ping",
    responses={
        fastapi.status.HTTP_200_OK: {
            "description": "Response when successfully connected",
            "content": {"application/json": {"example": {"PRIMO API is running!"}}},
        },
    },
    name="A basic health check",
)
async def health_check():
    """
    A basic ping utility to confirm the API service is running
    """
    LOGGER.info("Received ping request")
    return "PRIMO API is running!"


@app.get(
    "/uptime",
    responses={
        fastapi.status.HTTP_200_OK: {
            "description": "Uptime",
            "content": {
                "application/json": {
                    "example": {"Status": "OK", "Uptime": "0:00:20.371513"}
                }
            },
        },
    },
    name="Returns the uptime for the app",
)
async def uptime() -> Dict[str, str]:
    """
    A utility to check how long the API service has been running
    """
    time_alive = datetime.datetime.now() - START_TIME
    LOGGER.info(f"Received uptime request, current uptime: {time_alive}")
    return {"Status": "OK", "Uptime": f"{time_alive}"}


@app.get(
    "/redis_check",
    responses={
        fastapi.status.HTTP_404_NOT_FOUND: {
            "description": "Error when API could not connect to Redis in backend",
            "content": {
                "application/json": {
                    "example": {"detail": "Could not connect to Redis in the backend"}
                }
            },
        },
        fastapi.status.HTTP_200_OK: SUCCESSFUL_CONNECTION,
    },
    name="Returns whether API successfully connects with Redis on the backend",
)
async def redis_check() -> Dict[str, str]:
    """
    A utility to check if the API can connect with Redis successfully.
    Without the Redis connection, the API won't function properly
    """
    try:
        redis_obj = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=0)
        redis_obj.ping()
        return {"Status": "OK", "Connection Status": "Successfully connected"}
    except redis.exceptions.ConnectionError as exc:
        raise HTTPException(
            status_code=fastapi.status.HTTP_404_NOT_FOUND,
            detail="Could not connect to Redis in the backend",
        ) from exc


@app.get(
    "/mongo_check",
    responses={
        fastapi.status.HTTP_404_NOT_FOUND: {
            "description": "Error when API could not connect to MongoDB in backend",
            "content": {
                "application/json": {
                    "example": {"detail": "Could not connect to MongoDB in the backend"}
                }
            },
        },
        fastapi.status.HTTP_200_OK: SUCCESSFUL_CONNECTION,
    },
    name="Returns whether API successfully connects with MongoDB on the backend",
)
async def mongo_check(timeout: int | None = 5000) -> Dict[str, str]:
    """
    A utility to check if the API can connect with MongoDB successfully.
    Without the MongoDB connection, the API won't function properly

    Parameters:
    -----------
    timeout : int
        The time in milliseconds to wait for MongoDB to respond

    Returns
    -------
    Dict[str, str]
        A dictionary signifying successful connection

    Raises
    ------
    HTTPException
        If connection cannot be successfully established
    """
    server_timeout = timeout
    if server_timeout is None:
        server_timeout = 5000
    try:
        with MongoClient(MONGO_URI, serverSelectionTimeoutMS=server_timeout) as client:
            client.server_info()
        return {"Status": "OK", "Connection Status": "Successfully connected"}
    except pymongo.errors.ServerSelectionTimeoutError as exc:
        raise HTTPException(
            status_code=fastapi.status.HTTP_404_NOT_FOUND,
            detail="Could not connect to MongoDB in the backend",
        ) from exc


@app.get(
    "/status/{task_id}",
    responses={
        fastapi.status.HTTP_400_BAD_REQUEST: TASK_NOT_FOUND,
        fastapi.status.HTTP_200_OK: {"description": "Successful Response"},
    },
    name="Get status",
)
async def get_status(task_id: str) -> OptimizerResults:
    """
    Returns the status of a task identified with the id: task_id.

    Parameters
    ----------
    task_id : str
        The task whose status is to be queried

    Returns
    -------
    PrimoResponse
        The status of the task

    Raises
    ------
    HTTPException
        If the task to be queried cannot be found
    """
    LOGGER.info(f"Received get_status request with task_id: {task_id}")

    if not QUEUE_APP.is_valid_job_id(task_id):
        raise HTTPException(
            status_code=fastapi.status.HTTP_400_BAD_REQUEST,
            detail=f"Could not find task {task_id}",
        )
    job_status = get_primo_job_status(task_id)
    if job_status is None:
        raise HTTPException(
            status_code=fastapi.status.HTTP_400_BAD_REQUEST,
            detail=f"Could not find task {task_id}",
        )

    # extract information
    status_string = str(job_status.status)
    try:
        status_info_string = str(job_status.info)
    except TypeError:
        LOGGER.debug("Could not convert Celery Task status to String. Setting to None")
        status_info_string = None

    if status_string == Status.STARTED:
        status_string = "PROCESSING"
    LOGGER.debug(f"Task status is: {status_string}")
    LOGGER.debug(f"Task description is: {status_info_string}")

    return OptimizerResults(
        id=job_status.task_id,
        status=status_string,
        date=job_status.date_done,
        description=status_info_string,
    )


# pylint: disable=too-many-locals
@app.get(
    "/data_summary/{dataset_id}/{num_bins}",
    name="summarize data",
    responses={
        fastapi.status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "description": "Unknown data set"
        },
        fastapi.status.HTTP_200_OK: {"description": "Successful Response"},
    },
    description="Provides information for summarizing a well data set.",
)
def data_summary(dataset_id: str, num_bins: int) -> DataSummaryResults:
    """
    Receives a data set with priorities and general specifications and returns
    important summary items

    Parameters
    ----------
    dataset_id : str
        str parsed from endpoint for the dataset id

    """
    LOGGER.info("Received a data summary request")

    parameters = SimpleNamespace(
        general_specifications=SimpleNamespace(
            well_type=["Oil", "Gas", "Combined"],
            dataset_id=int(dataset_id),
        )
    )
    well_data = retrieve_well_data(parameters)

    LOGGER.debug("Retrieved well data")
    LOGGER.debug(f"Column names = {well_data.columns}")

    ### create summary statistics to be returned by the end point
    # note this is before ranking
    num_all_wells = len(well_data)
    num_gas_wells = len(well_data[well_data[COLUMN_MAP["well_type"]] == "Gas"])
    num_oil_wells = len(well_data[well_data[COLUMN_MAP["well_type"]] == "Oil"])
    num_combined_wells = len(
        well_data[well_data[COLUMN_MAP["well_type"]] == "Combined"]
    )

    # averages
    average_depth = int(well_data[COLUMN_MAP["depth"]].mean())
    average_age = int(well_data[COLUMN_MAP["age"]].mean())
    average_wells_per_operator = (
        well_data.groupby(COLUMN_MAP["operator_name"])
        .count()[COLUMN_MAP["well_id"]]
        .mean()
    )

    # max/min
    max_depth = well_data[COLUMN_MAP["depth"]].max()
    min_depth = well_data[COLUMN_MAP["depth"]].min()

    # ranges
    range_depth = max_depth - min_depth
    range_age = well_data[COLUMN_MAP["age"]].max() - well_data[COLUMN_MAP["age"]].min()

    # max/min
    max_depth = well_data[COLUMN_MAP["depth"]].max()
    min_depth = well_data[COLUMN_MAP["depth"]].min()

    LOGGER.info(
        f"Values in well_type column : {set(well_data[COLUMN_MAP['well_type']].values)} "
    )

    histogram_age_x, histogram_age_y = create_histogram(
        well_data, COLUMN_MAP["age"], num_bins
    )
    histogram_depth_x, histogram_depth_y = create_histogram(
        well_data, COLUMN_MAP["depth"], num_bins
    )
    LOGGER.info("Histograms created for age and depth column")

    # put into dictionary for response body
    output = [
        {
            "wells": {
                "num_all_wells": num_all_wells,
                "num_gas_wells": num_gas_wells,
                "num_oil_wells": num_oil_wells,
                "num_combined_wells": num_combined_wells,
                "average_wells_per_operator": float(
                    round(average_wells_per_operator, 2)
                ),
            },
            "depth": {
                "average_depth": average_depth,
                "max_depth": float(round(max_depth, 2)),
                "min_depth": float(round(min_depth, 2)),
                "range_depth": float(round(range_depth, 2)),
            },
            "age": {
                "average_age": average_age,
                "range_age": float(round(range_age, 2)),
            },
        },
        {
            "histogram_age_x": histogram_age_x,
            "histogram_age_y": histogram_age_y,
            "histogram_depth_x": histogram_depth_x,
            "histogram_depth_y": histogram_depth_y,
        },
    ]

    return DataSummaryResults(
        id=str(uuid.uuid4()),
        status=Status.SUCCESS,
        date=datetime.datetime.now(),
        data=output,
    )


# pylint: disable=too-many-locals
@app.post(
    "/kpi_summary",
    name="KPI Summary",
    responses={
        fastapi.status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "description": "Data input error info"
        },
        fastapi.status.HTTP_200_OK: {"description": "Successful Response"},
    },
    description="Returns a high-level information for a scenario",
)
@robust_endpoint(status_code=422)
async def kpi_summary(
    parameters: Annotated[
        KPISummaryRequest,
        Body(examples=[KPI_SUMMARY_EXAMPLE]),
    ],
) -> KPISummaryResponse:
    """
    KPI summary endpoint
    """

    LOGGER.info("Received KPI Summary Request")

    scenario_type = infer_use_case_type(parameters)

    # obtain the impact and efficiency choices of the user
    im_metrics, eff_metrics = verify_parameter_validity(scenario_type, parameters)

    parameter_obj = json.dumps(parameters.model_dump(mode="json"), indent=4)
    LOGGER.debug(f"Scenario parameters are: {parameter_obj}")

    # data post-filtering - get number of wells post filtering
    well_data = retrieve_well_data(parameters)
    well_data_options = handle_general_specifications_well_data(
        scenario_type, im_metrics, eff_metrics, parameters.general_specifications
    )
    # pylint: disable=duplicate-code
    data = WellData(
        data=well_data,
        column_names=get_well_data_columns(scenario_type),
        **well_data_options,
    )

    LOGGER.debug("Computed priority scores")
    data.compute_priority_scores()
    data.data = data.data.sort_values(by="Priority Score [0-100]", ascending=False)

    num_candidate_wells = len(data)
    # pylint: disable=(protected-access)
    num_oil_wells = len(data._well_types["oil"])
    # pylint: disable=(protected-access)
    num_gas_wells = len(data._well_types["gas"])
    num_combined_wells = 0  # this needs to be revisited on the well_plugging repository

    final_output = {
        "num_candidate_wells": num_candidate_wells,
        "num_oil_wells": num_oil_wells,
        "num_gas_wells": num_gas_wells,
        "num_combined_wells": num_combined_wells,
        "cost": None,
        "budget_remaining": None,
        "priority_impact_score_min": None,
        "priority_impact_score_max": None,
        "priority_impact_score_avg": None,
        "efficiency_score_min": None,
        "efficiency_score_max": None,
        "efficiency_score_avg": None,
        "overall_impact_weight": None,
        "overall_efficiency_weight": None,
        "num_projects": None,
    }

    if scenario_type.well_ranking:
        # only have impact factors
        final_output["priority_impact_score_min"] = data.data[
            "Priority Score [0-100]"
        ].min()
        final_output["priority_impact_score_max"] = data.data[
            "Priority Score [0-100]"
        ].max()
        final_output["priority_impact_score_avg"] = data.data[
            "Priority Score [0-100]"
        ].mean()

    if scenario_type.project_recommendation:
        # project data for the table
        project_data = get_list_of_project_data(parameters.project_ids)
        # well data for the projects
        wells_in_projects = [
            get_wells_ids_from_project_id(project_id)
            for project_id in parameters.project_ids
        ]

        # cost curve
        cost_curve = create_mobilization_cost(
            max(len(project) for project in wells_in_projects),
            parameters.general_specifications,
        )

        # budget
        final_output["cost"] = sum(
            cost_curve[len(project)] for project in wells_in_projects
        )
        final_output["budget_remaining"] = (
            parameters.general_specifications.budget - final_output["cost"]
        )

        # project details
        project_impact_scores = [
            project_data[parameters.project_ids[index]]["impact_score"]
            for index in range(len(parameters.project_ids))
        ]
        project_efficiency_scores = [
            project_data[parameters.project_ids[index]]["efficiency_score"]
            for index in range(len(parameters.project_ids))
        ]

        # over-write priority scores with project impact scores
        # if they selected project recommendations
        final_output["priority_impact_score_min"] = min(project_impact_scores)
        final_output["priority_impact_score_max"] = max(project_impact_scores)
        final_output["priority_impact_score_avg"] = sum(project_impact_scores) / len(
            project_impact_scores
        )

        # minimum, maximum, and average efficiency scores for projects
        final_output["efficiency_score_min"] = min(project_efficiency_scores)
        final_output["efficiency_score_max"] = max(project_efficiency_scores)
        final_output["efficiency_score_avg"] = sum(project_efficiency_scores) / len(
            project_efficiency_scores
        )

        # number of project
        final_output["num_projects"] = len(parameters.project_ids)

    # create the final result
    task_id = str(uuid.uuid4())

    return KPISummaryResponse(
        id=task_id,
        status=Status.SUCCESS,
        date=datetime.datetime.now(),
        data=final_output,
    )


@app.post(
    "/data_input_check",
    name="Check input data",
    responses={
        fastapi.status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "description": "Data input error info"
        },
        fastapi.status.HTTP_200_OK: {"description": "Successful Response"},
    },
    description="Checks input data from the user",
)
@robust_endpoint(status_code=422)
async def data_input_check(
    parameters: Annotated[
        ValidateDataRequest,
        Body(examples=[DATA_INPUT_CHECK_EXAMPLE]),
    ],
) -> DataInputCheckResponse:
    """
    Receives an input file and checks the input data converting the values appropriately
    and validating

    Parameters
    ----------
    parameters : ValidateDataRequest
        The parameters sent by the front end for data validation

    Returns
    -------
    DataInputCheckResponse
        The status of the task with "contains_ranking" field

    Raises
    ------
    HTTPException
        If the data is not in the correct format
    """

    parameter_object = json.dumps(parameters.model_dump(mode="json"), indent=4)
    LOGGER.debug(f"Data input check parameters are: {parameter_object}")

    file_path = str(parameters.file_path)

    task_id = str(uuid.uuid4())

    validated_data = validate_data(file_path)

    LOGGER.info("Validated data successfully")

    contains_ranking_data = (
        "priority_score_user_input" in validated_data.columns
        and validated_data["priority_score_user_input"].isna().sum() == 0
    )

    data_dict = validated_data.to_dict(orient="records")

    LOGGER.info("Writing data to MongoDB")
    write_data = []
    for well_data in data_dict:
        # replaces Nan with None
        well_data = {
            key: None if pd.isnull(value) else value for key, value in well_data.items()
        }
        well_obj = {
            "dataset_id": parameters.dataset_id,
            "json": well_data,
        }
        write_data.append(well_obj)

    LOGGER.info(f"Well data written to db example : {write_data[0]}")

    insert_data(write_data, MONGO_URI, MONGO_DATABASE, MONGO_DATASET_COLLECTION)

    return DataInputCheckResponse(
        id=task_id,
        status=Status.SUCCESS,
        date=datetime.datetime.now(),
        contains_ranking=contains_ranking_data,
    )


@app.post(
    "/run_primo",
    name="Run PRIMO job",
    responses={
        fastapi.status.HTTP_422_UNPROCESSABLE_ENTITY: INVALID_METRIC_SELECTIONS,
        fastapi.status.HTTP_200_OK: {
            "description": "Successful Response",
            "content": {
                "application/json": {
                    "example": {
                        "id": "a7bee1a5-4d24-4a2c-b3e3-5375c4636358",
                        "status": "PENDING",
                        "date": "2024-10-08T11:18:37.841Z",
                    }
                }
            },
        },
        fastapi.status.HTTP_404_NOT_FOUND: WELL_DATA_NOT_FOUND,
    },
    description="Triggers a PRIMO job",
)
def run_primo(
    parameters: Annotated[
        ScenarioParameters,
        Body(examples=[SCENARIO_PARAM_EXAMPLE]),
    ],
) -> PrimoResponse:
    """
    Runs a PRIMO job based on the requirements received in the JSON body. The job
    is added to the Queue

    Parameters
    ----------
    parameters : ScenarioParameters
        Parameters defining the scenario to be executed

    Returns
    -------
    PrimoResponse
        The status of the task
    """
    LOGGER.info("Received run_primo request")

    if parameters.general_specifications.budget in (-1, 0):
        raise HTTPException(
            status_code=fastapi.status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="The budget was not included in the request body.",
        )

    parameter_obj = json.dumps(parameters.model_dump(mode="json"), indent=4)
    LOGGER.debug(f"Scenario parameters are: {parameter_obj}")

    # Ensure we have data available otherwise throw an exception right away
    retrieve_well_data(parameters)

    # For delayed execution, objects must be encoded as JSON
    task = run_primo_instance.delay(jsonable_encoder(parameters))

    # Update redis object
    add_job_to_queue(task.task_id)

    return PrimoResponse(
        id=task.task_id, status=Status.PENDING, date=datetime.datetime.now()
    )


@app.post(
    "/rank_wells",
    name="Runs a PRIMO job for ranking wells",
    responses={
        fastapi.status.HTTP_422_UNPROCESSABLE_ENTITY: INVALID_METRIC_SELECTIONS,
        fastapi.status.HTTP_404_NOT_FOUND: WELL_DATA_NOT_FOUND,
        fastapi.status.HTTP_200_OK: {
            "description": (
                "Response when return_results is False and "
                "results are written to MongoDB"
            ),
            "content": {
                "application/json": {
                    "example": {
                        "id": "a7bee1a5-4d24-4a2c-b3e3-5375c4636358",
                        "status": "SUCCESS",
                        "date": "2024-10-08T11:18:37.841Z",
                    }
                }
            },
        },
    },
    description="Runs a PRIMO ranking job",
)
@robust_endpoint(status_code=422)
async def rank_wells(
    parameters: Annotated[
        RankWellsParameters, Body(examples=[RANKWELLS_PARAM_EXAMPLE])
    ],
    return_results: bool | None = False,
) -> Union[PrimoResponse, RankResults]:
    """
    Ranks wells based on the impact factors/program requirements specified.


    Parameters
    ----------
    parameters : ScenarioParameters
        Parameters defining the scenario with which wells are to be ranked

    return_results : bool
        If True, results are written immediately in the request response body.
        If False, results are written to MongoDB

    Returns
    -------
    PrimoResponse
        The status of the task
    """
    LOGGER.info("Received rank_wells request")
    scenario_type = infer_use_case_type(parameters)

    LOGGER.info("Scenario type is: %s", scenario_type)

    LOGGER.info("Validating Parameters")
    im_metrics, eff_metrics = verify_parameter_validity(scenario_type, parameters)

    if not is_valid_scenario_dependent(scenario_type, im_metrics, eff_metrics):
        raise HTTPException(
            status_code=fastapi.status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Impact/Efficiency Weight selections are invalid",
        )
    parameter_obj = json.dumps(parameters.model_dump(mode="json"), indent=4)
    LOGGER.debug(f"Scenario parameters are: {parameter_obj}")

    well_data = retrieve_well_data(parameters)

    LOGGER.debug("Retrieved well data")
    LOGGER.debug(f"Column names = {well_data.columns}")
    well_data_options = handle_general_specifications_well_data(
        scenario_type, im_metrics, eff_metrics, parameters.general_specifications
    )
    LOGGER.info(f"well data options {well_data_options}")

    data = WellData(
        data=well_data,
        column_names=get_well_data_columns(scenario_type),
        **well_data_options,
    )
    LOGGER.debug("Created well data object")

    data.compute_priority_scores()
    LOGGER.debug("Computed priority scores")
    ranked_wells = data.data.sort_values(by="Priority Score [0-100]", ascending=False)
    task_id = str(uuid.uuid4())
    output = convert_rank_results(task_id, ranked_wells, scenario_type.well_ranking)

    LOGGER.info("Ranking Results")
    for entry in output:
        LOGGER.info(
            f"{entry['well_rank']}, {entry['well_id']}, {entry['priority_score']}"
        )
    # Results are desired in response body
    if return_results:
        LOGGER.debug("Returning results to user")

        return RankResults(
            id=task_id, status=Status.SUCCESS, date=datetime.datetime.now(), data=output
        )
    # Results are desired in MongoDB
    LOGGER.debug("Started writing rank results to MongoDB")
    insert_data(output, collection_id=MONGO_RANK_COLLECTION)
    LOGGER.debug("Finished writing results to MongoDB")
    LOGGER.debug(f"Mongo DB well input example: {output[0]}")
    return PrimoResponse(
        id=task_id, status=Status.SUCCESS, date=datetime.datetime.now()
    )


@app.post(
    "/manual_override_recalculation_check",
    name="Manual override recalculation check",
    responses={
        fastapi.status.HTTP_200_OK: {
            "description": ("Success"),
            "content": {
                "application/json": {
                    "example": {
                        "id": "a7bee1a5-4d24-4a2c-b3e3-5375c4636358",
                        "status": "SUCCESS",
                        "date": "2024-10-08T11:18:37.841Z",
                        "data": {},
                    }
                }
            },
        },
        fastapi.status.HTTP_422_UNPROCESSABLE_ENTITY: INVALID_METRIC_SELECTIONS,
        fastapi.status.HTTP_404_NOT_FOUND: WELL_DATA_NOT_FOUND,
    },
    description="Returns constraint violations from override re-optimization",
)
@robust_endpoint(status_code=422)
async def manual_override_recalculation_check(
    parameters: Annotated[
        ManualOverrideRequest,
        Body(examples=[MANUAL_OVERRIDE_REQUEST_EXAMPLE]),
    ],
) -> OverrideRecalculationCheckResponse:
    """
    Endpoint for returning the information on constraints that are violated by projects
    after the manual override


    Parameters
    ----------
    parameters : ManualOverrideRequest
        Parameters defining the request from the user to manually override the recommendation

    Returns
    -------
    OverrideRecalculationCheckResponse
        The status of the task and violation information
    """

    LOGGER.info("Received manual override recalculation check request")

    scenario_type = infer_use_case_type(parameters)
    LOGGER.info("Scenario type is: %s", scenario_type)

    override_campaign, _, _, _ = construct_override_campaign(parameters, scenario_type)

    override_campaign_violation_info = override_campaign.violation_info

    # convert DataFrame in the violation info into dict, which can be accepted by
    # response json body
    serialized_violation_info = {
        msg: df.to_dict(orient="records") if isinstance(df, pd.DataFrame) else df
        for msg, df in override_campaign_violation_info.items()
    }

    task_id = str(uuid.uuid4())

    LOGGER.info("Returning response")
    for msg, df in serialized_violation_info.items():
        LOGGER.info(f"{msg}")
        LOGGER.info(f"{df}")

    return OverrideRecalculationCheckResponse(
        id=task_id,
        status=Status.SUCCESS,
        date=datetime.datetime.now(),
        data=serialized_violation_info,
    )


# pylint: disable=too-many-locals
# pylint: disable=too-many-statements
@app.post(
    "/manual_override_recalculation",
    name="Manual override recalculation",
    responses={
        fastapi.status.HTTP_200_OK: {
            "description": (
                "Successful response when " "results are written to MongoDB"
            ),
            "content": {
                "application/json": {
                    "example": {
                        "id": "a7bee1a5-4d24-4a2c-b3e3-5375c4636358",
                        "status": "SUCCESS",
                        "date": "2024-10-08T11:18:37.841Z",
                    }
                }
            },
        },
        fastapi.status.HTTP_422_UNPROCESSABLE_ENTITY: INVALID_METRIC_SELECTIONS,
        fastapi.status.HTTP_404_NOT_FOUND: WELL_DATA_NOT_FOUND,
    },
    description="Recalculates impact and efficiency scores based on a manual override",
)
@robust_endpoint(status_code=422)
async def manual_override_recalculation(
    # this will change based on the request body sent from the front end
    parameters: Annotated[
        ManualOverrideRequest,
        Body(examples=[MANUAL_OVERRIDE_REQUEST_EXAMPLE]),
    ],
) -> PrimoResponse:
    """
    Endpoint for the manual override recalculation capability

    Parameters
    ----------
    parameters : ManualOverrideRequest
        Parameters defining the request from the user to manually override the recommendation

    Returns
    -------
    PrimoResponse
        The status of the task
    """

    scenario_type = infer_use_case_type(parameters)
    LOGGER.info("Scenario type is: %s", scenario_type)

    LOGGER.info("Received manual override recalculation request")
    override_campaign, project_id_map, _, _ = construct_override_campaign(
        parameters, scenario_type
    )

    override_campaign_recalculate = override_campaign.recalculate()

    task_id = str(uuid.uuid4())

    process_override_results(
        override_campaign_recalculate,
        parameters,
        project_id_map,
        scenario_type.well_ranking,
    )

    LOGGER.info("Returning response")
    return PrimoResponse(
        id=task_id,
        status=Status.SUCCESS,
        date=datetime.datetime.now(),
    )


@app.post(
    "/valid_well_ids",
    name="Valid Well IDs",
    responses={
        fastapi.status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "description": "Data input error info"
        },
        fastapi.status.HTTP_200_OK: {"description": "Successful Response"},
    },
    description="Returns a list of valid well IDs",
)
@robust_endpoint(status_code=422)
async def valid_well_ids(
    parameters: Annotated[
        ScenarioParameters,
        Body(examples=[SCENARIO_PARAM_EXAMPLE]),
    ],
) -> ValidWellIdsResults:
    """
    Endpoint to return a list of valid well ids in the data

    Parameters
    ----------
    parameters : ScenarioParameters
        Parameters defining the scenario to be executed

    Returns
    -------
    ValidWellIdsResults
        The status of the task and the list of all valid well ids
    """

    scenario_type = infer_use_case_type(parameters)

    LOGGER.info("Scenario type is: %s", scenario_type)

    im_metrics, eff_metrics = verify_parameter_validity(scenario_type, parameters)

    if not is_valid_scenario_dependent(scenario_type, im_metrics, eff_metrics):
        raise HTTPException(
            status_code=fastapi.status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Impact/Efficiency Weight selections are invalid",
        )
    well_data = retrieve_well_data(parameters)

    LOGGER.debug(f"Column names = {well_data.columns}")
    well_data_options = handle_general_specifications_well_data(
        scenario_type, im_metrics, eff_metrics, parameters.general_specifications
    )
    LOGGER.debug(f"well data options {well_data_options}")
    data = WellData(
        data=well_data,
        column_names=get_well_data_columns(scenario_type),
        **well_data_options,
    )
    task_id = str(uuid.uuid4())

    LOGGER.debug("Created Well data object")

    output = data.data["Well ID"].tolist()

    LOGGER.debug("created list of well ids")

    return ValidWellIdsResults(
        id=task_id, status=Status.SUCCESS, date=datetime.datetime.now(), data=output
    )


@app.post(
    "/manual_override_reoptimization",
    name="Manual override reoptimization",
    responses={
        fastapi.status.HTTP_200_OK: {
            "description": (
                "Successful response when " "results are written to MongoDB"
            ),
            "content": {
                "application/json": {
                    "example": {
                        "id": "a7bee1a5-4d24-4a2c-b3e3-5375c4636358",
                        "status": "PENDING",
                        "date": "2024-10-08T11:18:37.841Z",
                    }
                }
            },
        },
        fastapi.status.HTTP_422_UNPROCESSABLE_ENTITY: INVALID_METRIC_SELECTIONS,
        fastapi.status.HTTP_404_NOT_FOUND: WELL_DATA_NOT_FOUND,
    },
    description="Trigger the PRIMO job based on a manual override",
)
@robust_endpoint(status_code=422)
async def manual_override_reoptimization(
    # this will change based on the request body sent from the front end
    parameters: Annotated[
        ManualOverrideRequest,
        Body(examples=[MANUAL_OVERRIDE_REQUEST_EXAMPLE]),
    ],
) -> PrimoResponse:
    """
    Endpoint for the manual override re-optimization capability
    Parameters
    ----------
    parameters : ManualOverrideRequest
        Parameters defining the request from the user to manually override the recommendation
    Returns
    -------
    PrimoResponse
        The status of the task
    """

    LOGGER.info("Received manual override reoptimization request")

    LOGGER.info(f"Parameters are: {parameters}")

    parameter_obj = json.dumps(parameters.model_dump(mode="json"), indent=4)
    LOGGER.debug(f"Scenario parameters are: {parameter_obj}")

    # Ensure we have data available otherwise throw an exception right away
    retrieve_well_data(parameters)

    # For delayed execution, objects must be encoded as JSON
    task = run_primo_instance.delay(
        parameters=jsonable_encoder(parameters), override=True
    )

    # Update redis object
    add_job_to_queue(task.task_id)

    LOGGER.info("Returning response")

    return PrimoResponse(
        id=task.task_id, status=Status.PENDING, date=datetime.datetime.now()
    )


@app.post(
    "/manual_reoptimization_check",
    name="reoptimization check",
    responses={
        fastapi.status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "description": "Project error info"
        },
        fastapi.status.HTTP_200_OK: {"description": "Successful Response"},
    },
    description="Returns constraint violations from override re-optimization",
)
@robust_endpoint(status_code=422)
async def manual_reoptimization_check(
    parameters: Annotated[
        OverrideReoptimizationCheckRequest,
        Body(examples=[KPI_SUMMARY_EXAMPLE]),
    ],
) -> OverrideReoptimizationCheckResponse:
    """
    Endpoint for checking constraint violations after override-based re-optimization

    Parameters
    ----------
    parameters :  OverrideReoptimizationCheckRequest
        Parameters defining the request from the user to manually override the recommendation
        and id of projects obtained from the re-optimization

    Returns
    -------
    OverrideReoptimizationCheckResponse
        The status of the task and violation information
    """

    LOGGER.info("Received re-optimization violation check request")

    scenario_type = infer_use_case_type(parameters)
    LOGGER.info("Scenario type is: %s", scenario_type)

    (
        _,
        _,
        opt_model_inputs,
        override_selections_add_return,
    ) = construct_override_campaign(parameters, scenario_type)

    LOGGER.info("Update the well cluster based on the override info")
    opt_model_inputs.update_cluster(override_selections_add_return)

    # get well obj str ids for all wells in the re-optimized results
    project_id_to_well_id_obj_str = get_map_project_ids_well_obj_str(
        parameters.re_optimized_project_ids
    )

    # all the well obj str ids
    all_well_obj_str_ids = []
    for _, well_str_ids in project_id_to_well_id_obj_str.items():
        all_well_obj_str_ids.extend(well_str_ids)
    LOGGER.info(f"all the well obj str ids : {all_well_obj_str_ids}")

    # well_id obj str : well id int
    well_id_int_to_well_id_obj_str = dict(
        get_map_of_well_ids_in_wells_table(all_well_obj_str_ids).items()
    )
    LOGGER.info(f"well obj str to well id int map : {well_id_int_to_well_id_obj_str}")

    wd = opt_model_inputs.config.well_data
    well_id_int_to_well_index = {}

    # well id int to well index
    # pylint: disable=protected-access
    for well_id_int in well_id_int_to_well_id_obj_str:
        well_index = wd.data[wd.data[wd._col_names.well_id] == well_id_int].index.item()
        well_id_int_to_well_index[well_index] = well_id_int
    LOGGER.info(f"well id to well index map : {well_id_int_to_well_index}")

    # all well id index
    well_index_list = list(well_id_int_to_well_index.keys())
    LOGGER.info(f"well id list : {well_index_list}")

    campaign_candidates = opt_model_inputs.campaign_candidates

    # dictionary contains cluster number and well index corresponding to
    # the re-optimization results
    project_map = {}
    for well in well_index_list:
        for cluster, well_list in campaign_candidates.items():
            if well in well_list:
                project_map.setdefault(cluster, []).append(well)
                break
    LOGGER.debug(f"Constructing a dictionary of projects: {project_map}")

    reoptimization_campaign = AssessFeasibility(opt_model_inputs, project_map)
    violation_info_dict_reoptimization = reoptimization_campaign.violation_info()

    # convert DataFrame in the violation info into dict, which can be accepted by
    # response json body
    serialized_violation_info = {
        msg: df.to_dict(orient="records") if isinstance(df, pd.DataFrame) else df
        for msg, df in violation_info_dict_reoptimization.items()
    }

    task_id = str(uuid.uuid4())

    LOGGER.info("Returning response")
    for msg, df in serialized_violation_info.items():
        LOGGER.info(f"{msg}")
        LOGGER.info(f"{df}")

    return OverrideReoptimizationCheckResponse(
        id=task_id,
        status=Status.SUCCESS,
        date=datetime.datetime.now(),
        data=serialized_violation_info,
    )


@app.delete(
    "/kill/{task_id}",
    name="Kill a PRIMO job",
    description="Kills a previously started PRIMO job",
    responses={
        fastapi.status.HTTP_400_BAD_REQUEST: TASK_NOT_FOUND,
        fastapi.status.HTTP_200_OK: {"description": "Successful Response"},
    },
)
async def kill(task_id: str) -> PrimoResponse:
    """
    Kills a PRIMO job identified with the id: task_id.

    Parameters
    ----------
    task_id : str
        The task to be killed

    Returns
    -------
    PrimoResponse
        The status of the task

    Raises
    ------
    HTTPException
        If the task to be queried cannot be found
    """
    LOGGER.info(f"Received kill request with task_id: {task_id}")

    job_status = get_primo_job_status(task_id)
    if job_status is None:
        raise HTTPException(
            status_code=fastapi.status.HTTP_400_BAD_REQUEST,
            detail=f"Could not find task {task_id}",
        )
    kill_primo_job(task_id)
    return PrimoResponse(
        id=job_status.task_id, status=Status.KILLED, date=job_status.date_done
    )


@app.delete(
    "/del_rank_results/{task_id}",
    name="Removes results from previous rank_well calls from MongoDB",
    responses={
        fastapi.status.HTTP_200_OK: {"description": "Successful Response"},
    },
)
async def del_rank_results(task_id: str) -> PrimoResponse:
    """
    Removes results from a rank_well call from MongoDB identified by task_id.
    API does not check if task_id is valid

    Parameters
    ----------
    task_id : str
        The task to be killed

    Returns
    -------
    PrimoResponse
        The status of the task
    """
    LOGGER.info(f"Received remove_rank_results request with task_id: {task_id}")
    remove_rank_results(task_id)
    LOGGER.info(
        f"Finished processing remove_rank_results request with task_id: {task_id}"
    )
    return PrimoResponse(
        id=task_id, status=Status.SUCCESS, date=datetime.datetime.now()
    )


@app.get(
    "/",
    responses={
        fastapi.status.HTTP_200_OK: {
            "description": "Response when successfully connected",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Welcome to the PRIMO API!",
                    }
                }
            },
        },
    },
    name="Homepage ping",
)
async def home_page():
    """
    Root API endpoint response
    """
    LOGGER.info("Received home page request")

    return {"message": "Welcome to the PRIMO API!"}


# pylint: disable=broad-exception-caught
# pylint: disable=unused-argument
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """
    Method provides a minor modification to the validation error that is automatically
    generated when a Pydantic validation error is observed.

    The key change is creation of a new field 'field' in the response body

    Parameters
    ----------
    request : Request
        The HTTP request that triggered the pydantic validation error

    exc : RequestValidationError
        The RequestValidationError that fastapi library would have thrown in the
        absence of this exception handler

    Returns
    -------
    JSONResponse
        The modified response
    """
    try:
        original_response_body = exc.errors()
        modified_response_body = []
        for info in original_response_body:
            if all(["msg", "type", "loc", "input", "ctx"] in info):
                new_msg = info["msg"].replace("Input ", "")
                new_msg = new_msg.capitalize()
                modified_response_body.append(
                    {
                        "type": info["type"],
                        "loc": info["loc"],
                        "field": ".".join([str(loc) for loc in info["loc"][1:]]),
                        "msg": new_msg,
                        "input": info["input"],
                        "ctx": info["ctx"],
                    }
                )
        if len(modified_response_body) > 0:
            return JSONResponse(
                status_code=fastapi.status.HTTP_422_UNPROCESSABLE_ENTITY,
                content=jsonable_encoder({"detail": modified_response_body}),
            )
        return JSONResponse(
            status_code=fastapi.status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=jsonable_encoder({"detail": original_response_body}),
        )
    except Exception:
        return JSONResponse(
            status_code=fastapi.status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=jsonable_encoder({"detail": exc.errors()}),
        )


@app.post(
    "/check_for_avail_data",
    name="Check for Available Data",
    responses={
        fastapi.status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "description": "Data input error info"
        },
        fastapi.status.HTTP_200_OK: {"description": "Successful Response"},
    },
    description="Checks available data from the user",
)
@robust_endpoint(status_code=422)
async def check_available_data(
    parameters_raw: Annotated[
        GeneralSpecifications,
        Body(examples=[GENERAL_SPECIFICATIONS]),
    ],
) -> DataAvailCheckResults:
    """
    This method checks to see if a user has the available data to use each of the available impact
    and efficiency factors on the web app.

    Parameters
    ----------
    parameters : CheckDataAvailParameters
        Parameters defining the general specifications.

    Returns
    -------
    impact_factors: Dict[str,Union[dict,None]]
        A dictionary containing the true or false values for whether the dataset contains the data
        necessary to use an impact factor for each impact factor.

    efficiency_factors: Dict[str,Union[dict,None]]
        A dictionary containing the true or false values for whether the dataset contains the data
        necessary to use an efficiency factor for each efficiency factor
    """
    im_metrics = copy.deepcopy(FULL_LIST_IMPACT_FACTORS)
    eff_metrics = copy.deepcopy(EFFICIENCY_FACTORS)

    parameters = SimpleNamespace(general_specifications=parameters_raw)
    # this information is not used, but now is a required argument for get_well_data_columns
    scenario_type_dummy = ScenarioType(
        well_ranking=False, project_recommendation=False, project_comparison=False
    )
    # retrieve the well data from mongoDB
    well_data = retrieve_well_data(parameters)

    # The well data object expects priority scores if
    # the well_ranking scenario type is False
    well_data["Priority Score User Input"] = [1] * len(well_data)

    LOGGER.info(f"Column names = {well_data.columns}")
    well_data_options = handle_general_specifications_well_data(
        scenario_type_dummy, im_metrics, eff_metrics, parameters.general_specifications
    )
    LOGGER.info(f"well data options {well_data_options}")

    data = WellData(
        data=well_data,
        column_names=get_well_data_columns(scenario_type_dummy),
        **well_data_options,
    )
    LOGGER.info("Created well data object")

    # Check if there's available data for each impact metric.
    # If there is, set selected = True, otherwise keep selected as False
    LOGGER.info("Start Impact metric data check")
    impact_factors = metric_data_check(im_metrics, data, "impact")
    LOGGER.info("Finished Impact metric data check")

    # Check if there's available data for each efficiency metric.
    # If there is, set selected = True, otherwise keep selected as False or yes
    LOGGER.info("Start efficiency metric data check")
    efficiency_factors = metric_data_check(eff_metrics, data, "efficiency")
    LOGGER.info("Finished efficiency metric data check")

    return DataAvailCheckResults(
        id=str(uuid.uuid4()),
        status=Status.SUCCESS,
        date=datetime.datetime.now(),
        impact_factors=impact_factors,
        efficiency_factors=efficiency_factors,
    )


if __name__ == "__main__":
    # Simple initialization of app for easy testing and debugging
    uvicorn.run("main:app", host="0.0.0.0", port=9090, reload=True)
