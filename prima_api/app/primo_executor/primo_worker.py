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
# pylint: disable=no-name-in-module
"""
Implements classes and methods for the PRIMO worker to execute
a PRIMO job
"""

# Standard libs
import json
import logging
import time
from types import SimpleNamespace
from typing import Dict, List, Optional, Tuple, Union

# Installed libs
import fastapi
import numpy as np
import pandas as pd
from fastapi import HTTPException
from primo.data_parser import EfficiencyMetrics, ImpactMetrics
from primo.data_parser.default_data import CONVERSION_FACTOR
from primo.data_parser.input_config import ScenarioType
from primo.data_parser.well_data import WellData
from primo.opt_model.model_options import OptModelInputs
from primo.utils.config_utils import (
    OverrideAddInfo,
    OverrideRemoveLockInfo,
    OverrideSelections,
)
from primo.utils.override_utils import OverrideCampaign

# User-defined libs
from parameters import (
    MONGO_DATABASE,
    MONGO_URI,
    MONGO_WELL_COLLECTION,
    MYSQL_PROJECT_WELL_COLLECTION,
    SOLVER,
)
from primo_executor.primo_worker_parameters import (
    FACTOR_MAP,
    LOUVAIN_SWITCH_SIZE,
    MINIMUM_MAX_SIZE,
    MULTIPLIER_FOR_LOUVAIN_CLUSTER_SIZE_BUDGET,
    MULTIPLIER_FOR_LOUVAIN_CLUSTER_SIZE_MAX_WELLS,
    SUPP_EFF_METRICS,
    SUPP_IMPACT_METRICS,
    get_well_data_columns,
)
from utils import COLUMN_MAP
from utils.models import (
    EfficiencyFactors,
    Factor,
    GeneralSpecifications,
    ImpactFactors,
    KPISummaryRequest,
    ManualOverrideRequest,
    OverrideReoptimizationCheckRequest,
    RankWellsParameters,
    ScenarioParameters,
)
from utils.mongo_io import (
    collect_well_data,
    get_cluster_id_from_well_id,
    get_map_of_well_ids_in_wells_table,
    get_well_id_object_id_map,
    insert_data,
    rename_cols_for_mongodb,
)
from utils.mysql_io import get_map_project_ids_well_obj_str, insert_data_to_mysql
from utils.result_format_util import (
    process_override_results,
    reformat_campaign_results_for_db_storage,
    reformat_campaign_well_data_results_for_db_storage,
    reformat_campaign_well_data_results_for_mysql_storage,
    well_id_to_index,
)
from utils.valid_inputs import is_valid_scenario_dependent

# pylint: disable=duplicate-code
LOGGER = logging.getLogger(__name__)


def infer_use_case_type(
    parameters: (
        KPISummaryRequest
        | ManualOverrideRequest
        | OverrideReoptimizationCheckRequest
        | ScenarioParameters
        | RankWellsParameters
    ),
) -> ScenarioType:
    """
    Infers the type of scenario based on the request data

    Parameters
    ----------
    parameters : KPISummaryRequest | ManualOverrideRequest | OverrideReoptimizationCheckRequest
                    | ScenarioParameters | RankWellsParameters
        The scenario parameters to use to infer

    Returns
    -------
    ScenarioType
        A ScenarioType object with the appropriate data members assigned
    """
    return ScenarioType(
        well_ranking="Well Ranking" in parameters.use_cases.cases,
        project_recommendation="P&A Project Recommendations"
        in parameters.use_cases.cases,
        project_comparison="P&A Project Comparisons" in parameters.use_cases.cases,
    )


def handle_general_specifications_well_data(
    scenario_type: ScenarioType,
    im_metrics: ImpactMetrics,
    eff_metrics: EfficiencyMetrics,
    general_specifications: GeneralSpecifications,
) -> Dict[str, Optional[int]]:
    """
    Handles all of the general specification entries relevant to the well data class

    Parameters
    ----------
    scenario_type : ScenarioType
        The type of scenario

    im_metrics : ImpactMetrics
        User selections for factors related to impact metrics

    eff_metrics : Efficiency Metrics
        User selections for factors related to efficiency metrics

    general_specifications : GeneralSpecifications
        The general specifications object from the request body

    Returns
    -------
    kwargs : Dict[str, Optional[int]]
        A dictionary of keyword arguments and values for the well data class
    """
    kwargs = {}

    general_specifications.specified_type = (
        general_specifications.specified_type.capitalize()
    )

    kwargs["preliminary_data_check"] = general_specifications.basic_data_checks
    kwargs[
        "min_lifetime_gas_production"
    ] = general_specifications.min_lifetime_gas_production
    kwargs[
        "max_lifetime_gas_production"
    ] = general_specifications.max_lifetime_gas_production
    kwargs[
        "min_lifetime_oil_production"
    ] = general_specifications.min_lifetime_oil_production
    kwargs[
        "max_lifetime_oil_production"
    ] = general_specifications.max_lifetime_oil_production
    kwargs["well_depth_limit"] = general_specifications.well_depth_limit

    missing_data_fields = [
        "missing_age",
        "missing_depth",
        "missing_ann_gas_production",
        "missing_ann_oil_production",
        "missing_life_gas_production",
        "missing_life_oil_production",
        "missing_well_type",
    ]

    # order must match missing data fields
    general_specifications_missing_data_values = [
        general_specifications.handle_missing_well_age,
        general_specifications.handle_missing_depth,
        general_specifications.handle_missing_production,
        general_specifications.handle_missing_production,
        general_specifications.handle_missing_production,
        general_specifications.handle_missing_production,
        general_specifications.handle_missing_type,
    ]

    # order must match missing_data_fields
    specify_data_fields = [
        "fill_age",
        "fill_depth",
        "fill_ann_gas_production",
        "fill_ann_oil_production",
        "fill_life_gas_production",
        "fill_life_oil_production",
        "fill_well_type",
    ]

    general_specifications_specify_data_values = [
        general_specifications.specified_age,
        general_specifications.specified_depth,
        general_specifications.specified_annual_gas_production,
        general_specifications.specified_annual_oil_production,
        general_specifications.specified_lifetime_gas_production,
        general_specifications.specified_lifetime_oil_production,
        general_specifications.specified_type,
    ]

    for (
        primo_missing_option_field,
        missing_request_body_value,
        primo_specify_field,
        specify_request_body_value,
    ) in zip(
        missing_data_fields,
        general_specifications_missing_data_values,
        specify_data_fields,
        general_specifications_specify_data_values,
    ):
        if missing_request_body_value == "specify-value":
            kwargs[primo_missing_option_field] = "fill"
            kwargs[primo_specify_field] = specify_request_body_value
        if missing_request_body_value == "remove-wells":
            kwargs[primo_missing_option_field] = "remove"

    kwargs["scenario_type"] = scenario_type

    if scenario_type.well_ranking:
        kwargs["impact_metrics"] = im_metrics

    if scenario_type.project_recommendation:
        kwargs["efficiency_metrics"] = eff_metrics

    return kwargs


def update_metrics(
    metrics: Union[ImpactMetrics, EfficiencyMetrics],
    factors: Union[ImpactFactors, EfficiencyFactors],
) -> Union[ImpactMetrics, EfficiencyMetrics]:
    """
    Translates the specific input parameters selected by a user on the webapp GUI
    and received via a POST request into the data structures required by the PRIMO backend
    Parameters
    ----------
    metrics : Union[ImpactMetrics, EfficiencyMetrics]
        An object containing the default Impact/Efficiency metrics for the PRIMO run
    factors : Union[ImpactFactors, EfficiencyFactors]
        User selections for the corresponding factors via the GUI

    Returns
    -------
    Union[ImpactMetrics, EfficiencyMetrics]
        Updated metrics object per user selections
    """

    # maps the name from web request to the names required by PRIMO for the
    # efficiency calculation
    # to make general, this will also need to be implemented for the submetrics as well
    # but currently we don't have submetrics for the efficiency computation

    primary_metrics = metrics.get_primary_metrics
    for factor_name, factor_settings in factors.get_primary_factors().items():
        if factor_settings is not None and factor_settings.selected:
            # Skip if user did not select this option
            value = factor_settings.value
            factor_name_mapped = FACTOR_MAP.get(factor_name, factor_name)
            primary_metrics[factor_name_mapped].weight = value

            # Also ensure sub-factors/child factors are also updated
            child_factors = factor_settings.get_child_factors()
            for (
                sub_factor_name,
                sub_factor_settings,
            ) in child_factors.items():
                if sub_factor_settings is not None and sub_factor_settings.selected:
                    value = sub_factor_settings.value
                    sub_factor_mapped = FACTOR_MAP.get(sub_factor_name, sub_factor_name)
                    primary_metrics[factor_name_mapped].submetrics[
                        sub_factor_mapped
                    ].weight = value

    return metrics


def translate_input_selections(
    scenario_type: ScenarioType,
    parameters: Union[ScenarioParameters, ManualOverrideRequest],
) -> Tuple[ImpactMetrics, EfficiencyMetrics]:
    """
    Translates the input parameters received from the API Post Request
    into data structures that PRIMO backend is expecting for impact and efficiency

    Parameters
    ----------
    scenarioType : ScenarioType
        The type of scenario

    parameters : Union[ScenarioParameters, ManualOverrideRequest]
        The ScenarioParameters or the ManualOverrideRequest received by the API

    Returns
    -------
    Tuple[ImpactMetrics, EfficiencyMetrics]
        A tuple containing the ImpactMetrics and EfficiencyMetrics objects
    """
    im_metrics = ImpactMetrics(SUPP_IMPACT_METRICS)
    impact_factors = parameters.impact_factors
    if scenario_type.well_ranking:
        im_metrics = update_metrics(im_metrics, impact_factors)

    eff_metrics = EfficiencyMetrics(SUPP_EFF_METRICS)
    efficiency_factors = parameters.efficiency_factors
    if scenario_type.project_recommendation:
        eff_metrics = update_metrics(eff_metrics, efficiency_factors)

    return im_metrics, eff_metrics


def create_mobilization_cost(
    max_num_wells: int, parameters: GeneralSpecifications
) -> Dict[int, float]:
    """
    Creates the mobilization cost curve based on the options of the general specifications

    Parameters
    ----------
    max_num_wells : int
        The maximum number of wells possible in a project

    parameters : GeneralSpecifications
        The general specification values sent through the request body

    Returns
    -------
    Dict [int, float]
        A Dictionary that indicates the cost of plugging for a project
        as a function of the number of wells in a project

    """
    cost_parameters = [
        parameters.shallow_gas_well_cost,
        parameters.deep_gas_well_cost,
        parameters.shallow_oil_well_cost,
        parameters.deep_oil_well_cost,
    ]

    # use the maximum for now
    base_well_cost = max(cost_parameters)

    return {
        i: (base_well_cost * i**parameters.cost_efficiency)
        for i in range(1, max_num_wells + 1)
    }


def get_max_num_wells_allowable_by_budget(
    mobilization_cost: Dict[int, float], parameters: GeneralSpecifications
) -> int:
    """
    Creates the mobilization cost curve based on the options of the general specifications

    Parameters
    ----------
    mobilization_cost : Dict[int, float]
        The mobilization cost curve of the instance

    parameters : GeneralSpecifications
        The general specification values sent through the request body

    Returns
    -------
    int
        Maximum number of wells that can be plugged given the budget

    """
    for num_wells in mobilization_cost:
        if mobilization_cost[num_wells] > parameters.budget:
            return num_wells - 1

    return list(mobilization_cost.keys())[-1]


def translate_general_specifications_to_opt_model_inputs(
    general_specifications: GeneralSpecifications,
    well_data: WellData,
    cluster_mapping: Dict[int, List[int]] = None,
):
    """
    Translates the user input program requirements into an OptModelInputs object

    Parameters
    ----------
    general_specifications: GeneralSpecifications
        The program requirements sent through the request body

    well_data: WellData
        The well data that will be used in the optimization step

    cluster_mapping: Dict[int, List[int]]
        Cluster ids mapped to indices of wells

    Returns
    -------
    OptModelInputs
        Input configuration object for the optimization

    """

    # Mobilization cost: cost map for plugging 1 up to all the wells
    # also not yet a user input
    mobilization_cost = create_mobilization_cost(len(well_data), general_specifications)
    # LOGGER.info(f"MOBILIZATION COST = {mobilization_cost}")

    if mobilization_cost[1] > general_specifications.budget:
        raise HTTPException(
            status_code=fastapi.status.HTTP_400_BAD_REQUEST,
            detail="The budget is not sufficient to plug any wells",
        )

    max_num_wells_allowable_by_budget = get_max_num_wells_allowable_by_budget(
        mobilization_cost, general_specifications
    )

    obj_weight_impact = 50
    if general_specifications.model == "impact":
        obj_weight_impact = 100

    options = {
        "cluster_mapping": cluster_mapping,
        "well_data": well_data,
        "total_budget": general_specifications.budget,
        "mobilization_cost": mobilization_cost,
        "min_wells_in_project": general_specifications.min_wells_in_project,
        "max_wells_in_project": general_specifications.max_wells_in_project,
        "threshold_distance": general_specifications.max_distance_between_project_wells,
        "max_wells_per_owner": general_specifications.max_wells_per_owner,
        # Deactivate the following line in corresponds to the removal of
        # lazy_constraint in code base
        # "lazy_constraints": general_specifications.use_lazy_constraints,
        "objective_weight_impact": obj_weight_impact,
    }

    if len(well_data) > LOUVAIN_SWITCH_SIZE:
        LOGGER.info("Louvain clustering")
        options["cluster_method"] = "Louvain"
        options["threshold_cluster_size"] = max(
            MINIMUM_MAX_SIZE,
            min(
                MULTIPLIER_FOR_LOUVAIN_CLUSTER_SIZE_MAX_WELLS
                * general_specifications.max_wells_in_project,
                MULTIPLIER_FOR_LOUVAIN_CLUSTER_SIZE_BUDGET
                * max_num_wells_allowable_by_budget,
            ),
        )

    if OptModelInputs.check_sufficient_budget_static(
        well_data,
        general_specifications.max_wells_in_project,
        mobilization_cost,
        general_specifications.budget,
    ):
        options["cluster_method"] = "Exhaustive"

    return OptModelInputs(**options)


def translate_general_specifications_to_solver_inputs(
    general_specifications: GeneralSpecifications,
):
    """Translates the user inputs into solver options based on solver used.

    Parameters
    ----------
    general_specifications: GeneralSpecifications
        The program requirements sent through the request body
    """

    solver_option = {}

    if SOLVER == "gurobi":
        solver_option["TimeLimit"] = general_specifications.solver_time
        solver_option["MIPGap"] = general_specifications.relative_gap
        solver_option["MIPGapAbs"] = general_specifications.absolute_gap
        solver_option["Threads"] = 1

    if SOLVER == "scip":
        solver_option["limits/time"] = general_specifications.solver_time
        solver_option["limits/gap"] = general_specifications.relative_gap
        solver_option["limits/absgap"] = general_specifications.absolute_gap

    return solver_option


# pylint: disable=too-many-locals, too-many-statements
def solve_primo_model(parameters: ScenarioParameters):
    """
    Solves a PRIMO job. Results for projects and wells are written to MongoDB

    Parameters
    ----------
    parameters : Scenario Parameters
        The parameters for the scenario

    Returns
    -------
    None
    """
    LOGGER.info("Received manual override recalculation check request")

    general_specifications = parameters.general_specifications
    scenario_id = parameters.scenario_id

    LOGGER.info(f"Running scenario: {scenario_id}")

    dataset_id = general_specifications.dataset_id
    well_type = general_specifications.well_type

    scenario_type = infer_use_case_type(parameters)
    LOGGER.info("Scenario type is: %s", scenario_type)

    im_metrics, eff_metrics = verify_parameter_validity(scenario_type, parameters)

    if not is_valid_scenario_dependent(scenario_type, im_metrics, eff_metrics):
        raise HTTPException(
            status_code=fastapi.status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Impact/Efficiency Weight selections are invalid",
        )
    # well_data = collect_well_data(dataset_id, well_type)
    LOGGER.info("Impact metrics selected for scenario are:")
    LOGGER.info(str(im_metrics))

    LOGGER.info("Efficiency metrics selected for scenario are:")
    LOGGER.info(str(eff_metrics))

    LOGGER.info("Collecting the well data")
    well_data_from_db = collect_well_data(dataset_id, list(well_type))

    LOGGER.info("Adding the lifetime production column")
    # first we get the well data from the database
    well_data_options = handle_general_specifications_well_data(
        scenario_type, im_metrics, eff_metrics, general_specifications
    )
    # pylint: disable=duplicate-code
    well_data = WellData(
        data=well_data_from_db,
        column_names=get_well_data_columns(scenario_type),
        **well_data_options,
    )

    LOGGER.info("Computing priority scores")
    # for the optimization we need impact scores
    well_data.compute_priority_scores()

    LOGGER.info("Adding rank column to data")
    # this is necessary for the output
    well_data.data = well_data.data.sort_values(
        by="Priority Score [0-100]", ascending=False
    )
    well_data.data.reset_index(inplace=True, drop=True)
    well_data.data["well_rank"] = well_data.data.index + 1

    get_well_id_object_id_map(dataset_id)

    LOGGER.info("Configuring optimization inputs from program requirements")
    # configure the optimization inputs
    opt_model_inputs = translate_general_specifications_to_opt_model_inputs(
        general_specifications=general_specifications,
        well_data=well_data,
    )

    LOGGER.info("Building optimization model")
    # build the optimization model
    opt_model_inputs.build_optimization_model()

    LOGGER.info("Solving model")
    # obtain the solver options
    solver_option = translate_general_specifications_to_solver_inputs(
        general_specifications
    )
    LOGGER.info(f"{solver_option}")

    start_time = time.time()

    # create the campaigns
    opt_campaigns = opt_model_inputs.solve_model(
        solver=SOLVER, solver_options=solver_option
    )

    # Record the end time
    end_time = time.time()

    # Calculate the computation time
    computation_time = end_time - start_time

    LOGGER.info(f"The computation time is: {computation_time} seconds")

    LOGGER.info("Formatting results for database")
    project_data = reformat_campaign_results_for_db_storage(opt_campaigns, scenario_id)

    LOGGER.info("Extracting well id map information")
    well_id_object_id_map = get_well_id_object_id_map(dataset_id)

    well_data_db = reformat_campaign_well_data_results_for_db_storage(
        opt_campaigns, well_id_object_id_map, None, scenario_type.well_ranking
    )

    if len(well_data_db) == 0:
        LOGGER.info("The optimization problem returned no wells in the solution")
        LOGGER.info("This is likely due to a contradiction in constraints and data")
        LOGGER.info("Example: there is no well in DAC, but DAC constraint > 0")
        raise HTTPException(
            status_code=fastapi.status.HTTP_400_BAD_REQUEST,
            detail=(
                "The optimization model returned no wells in the solution."
                "Please check data and optional constraints to ensure a "
                "feasible solution with at least one well"
            ),
        )

    LOGGER.info(f"Well data result example : {well_data_db[0]}")
    LOGGER.debug(f"Full set of well results : {well_data_db}")

    column_unmap = {value: key for key, value in COLUMN_MAP.items()}

    # get project results for comparison
    for _, project in opt_campaigns.projects.items():
        column_names = project.well_data.col_names
        well_data = rename_cols_for_mongodb(
            project.well_data.data, scenario_type.well_ranking
        )
        well_data = well_data.to_dict(orient="records")
        LOGGER.info(f"Project : {project.project_id}")
        for _, well_entry in enumerate(well_data):
            LOGGER.info(f"Well Id : {well_entry[column_unmap[column_names.well_id]]}")
    LOGGER.info("\n")
    campaign_information = opt_campaigns.get_campaign_summary().to_dict(
        orient="records"
    )
    for project in campaign_information:
        LOGGER.info(f"Project ID : {project['Project ID']}")
        LOGGER.info(f"Impact Score : {project['Impact Score [0-100]']}")
        LOGGER.info(f"Efficiency Score [0-100] : {project['Efficiency Score [0-100]']}")
    LOGGER.info("\n")

    LOGGER.info(
        "Inserting project well data into the wells mongo db table for primo solve"
    )
    wells_table_ids = [
        str(obj)
        for obj in insert_data(
            well_data_db, MONGO_URI, MONGO_DATABASE, MONGO_WELL_COLLECTION
        ).inserted_ids
    ]

    LOGGER.info(f"wells table ids : {wells_table_ids}")

    LOGGER.info("Inserting project results for primo solve")
    LOGGER.info(f"Project data: {project_data}")
    project_id_mysql = insert_data_to_mysql(project_data)

    LOGGER.info(f"Length of project ids : {len(project_data)}")
    LOGGER.info(f"Length of wells table ids : {len(wells_table_ids)}")

    LOGGER.info(
        f"Example data for solve primo model inserted to projects mysql table : {project_data[0]}"
    )
    LOGGER.info(f"Project data written to projects table : {project_data}")

    project_well_map = reformat_campaign_well_data_results_for_mysql_storage(
        opt_campaigns, project_id_mysql, wells_table_ids
    )

    LOGGER.info(
        "Writing results to project_well table of MySQL database for primo solve"
    )
    insert_data_to_mysql(
        project_well_map,
        collection_id=MYSQL_PROJECT_WELL_COLLECTION,
    )

    LOGGER.info(
        f"All the data for solve primo model"
        f"inserted to the project_well mysql table : {project_well_map}"
    )


def solve_primo_model_override(
    general_specifications: GeneralSpecifications,
    scenario_id: int,
    parameters: ManualOverrideRequest,
    scenario_type: ScenarioType,
):
    """
    Solves a PRIMO job with override request. Results for projects and
    wells are written to MongoDB

    Parameters
    ----------
    general_specifications : GeneralSpecifications
        Global configuration parameters related to the program

    parameters : ManualOverrideRequest
        Parameters defining the request from the user to manually override
        the recommendation

    scenario_id : int
        The id of the scenario

    scenario_type : ScenarioType
        The type of scenario

    Returns
    -------
    None
    """

    LOGGER.info(f"Running scenario: {scenario_id}")
    (
        override_campaign,
        project_id_map,
        opt_model_inputs,
        override_selections_add_return,
    ) = construct_override_campaign(parameters, scenario_type)

    LOGGER.info("Obtain the override dictionary for reoptimization")
    override_dict = override_campaign.re_optimize_data()

    LOGGER.info(
        f"Update the cluster based on the override info, {override_selections_add_return}"
    )
    opt_model_inputs.update_cluster(override_selections_add_return)

    LOGGER.info("Build the optimization model for reoptimization")
    opt_model_inputs.build_optimization_model(override_dict)

    LOGGER.info("Solving model")
    solver_option = translate_general_specifications_to_solver_inputs(
        general_specifications
    )
    LOGGER.info(f"{solver_option}")

    opt_campaign_reoptimize = opt_model_inputs.solve_model(
        solver=SOLVER, solver_options=solver_option
    )

    process_override_results(
        opt_campaign_reoptimize, parameters, project_id_map, scenario_type.well_ranking
    )


def construct_override_campaign(
    parameters: Union[ManualOverrideRequest, OverrideReoptimizationCheckRequest],
    scenario_type: ScenarioType,
):
    """
    Function for constructing the override campaign

    Parameters
    ----------
    parameters : ManualOverrideRequest
        Parameters defining the request from the user to manually override the recommendation

    scenario_type : ScenarioType
        The type of scenario

    Returns
    -------
    override_campaign : OverrideCampaign
        The status of the task

    project_id_map : Dict
        A dictionary map project id to project db object str

    opt_model_inputs : OptimizationModelInputs
        Input configuration object for the optimization

    override_selections : OverrideSelections
        An object for storing the return from the remove_widget, add_widget, and lock_widget
    """
    LOGGER.info(f"Parameters are: {parameters}")

    im_metrics, eff_metrics = verify_parameter_validity(scenario_type, parameters)

    parameter_obj = json.dumps(parameters.model_dump(mode="json"), indent=4)
    LOGGER.debug(f"Scenario parameters are: {parameter_obj}")

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

    LOGGER.info("Adding rank column to data")
    # we need the indices of the wells in the SAME ORDER that they were optimized - maybe not
    data.data = data.data.sort_values(by="Priority Score [0-100]", ascending=False)
    data.data.reset_index(inplace=True, drop=True)
    data.data["well_rank"] = data.data.index + 1

    LOGGER.info("Configuring optimization inputs from program requirements")
    # configure the optimization inputs
    opt_model_inputs = translate_general_specifications_to_opt_model_inputs(
        parameters.general_specifications, data
    )

    LOGGER.info("Retrieving project data from the database")

    # project_ids to well_id_strings
    project_id_to_well_id_obj_str = get_map_project_ids_well_obj_str(
        parameters.parent_project_ids
    )
    LOGGER.info(f"project ids to well id obj str : {project_id_to_well_id_obj_str}")

    # project_ids to cluster_ids
    project_ids_to_cluster_ids = {
        project_id: get_cluster_id_from_well_id(
            project_id_to_well_id_obj_str[project_id][0]
        )
        for project_id in project_id_to_well_id_obj_str
    }
    LOGGER.info(f"project ids to cluster ids : {project_ids_to_cluster_ids}")
    # cluster_ids to project_ids
    project_id_map = {
        cluster_id: project_id
        for project_id, cluster_id in project_ids_to_cluster_ids.items()
    }
    LOGGER.info(f"project id map : {project_id_map}")
    # all the well obj str ids
    all_well_obj_str_ids = []
    for _, well_str_ids in project_id_to_well_id_obj_str.items():
        all_well_obj_str_ids.extend(well_str_ids)
    LOGGER.info(f"all the well obj str ids : {all_well_obj_str_ids}")

    # well_id obj str : well id int
    well_id_obj_str_to_well_id_int = {
        well_id_obj_str: well_id_int
        for well_id_int, well_id_obj_str in get_map_of_well_ids_in_wells_table(
            all_well_obj_str_ids
        ).items()
    }
    LOGGER.info(f"well obj str to well id int map : {well_id_obj_str_to_well_id_int}")

    # cluster_id to well_id_str
    cluster_id_to_well_id_str = {
        project_ids_to_cluster_ids[project_id]: project_id_to_well_id_obj_str[
            project_id
        ]
        for project_id in project_id_to_well_id_obj_str
    }
    LOGGER.info(f"cluster id to well id str : {cluster_id_to_well_id_str}")

    # cluster_id to well_id_int
    project_map = {
        cluster_id: [
            well_id_obj_str_to_well_id_int[id]
            for id in cluster_id_to_well_id_str[cluster_id]
        ]
        for cluster_id in cluster_id_to_well_id_str
    }

    LOGGER.info(f"project map : {project_map}")

    LOGGER.info("Mapping well ids to indices")
    # now map well ids to indices
    project_index_map = {
        key: [well_id_to_index(data, i) for i in value]
        for key, value in project_map.items()
    }

    LOGGER.info("Loading user override information")
    # now create the user selection object for the override campaign from the user
    # change the well_id to index
    override_remove = OverrideRemoveLockInfo(
        [
            project_ids_to_cluster_ids[int(project_id)]
            for project_id in parameters.projects_remove
        ],
        {
            project_ids_to_cluster_ids[int(key)]: [
                well_id_to_index(data, i) for i in value
            ]
            for key, value in parameters.wells_remove.items()
        },
    )
    LOGGER.info("Well removed constructed")
    override_lock = OverrideRemoveLockInfo(
        [
            project_ids_to_cluster_ids[int(project_id)]
            for project_id in parameters.projects_lock
        ],
        {
            project_ids_to_cluster_ids[int(key)]: [
                well_id_to_index(data, i) for i in value
            ]
            for key, value in parameters.wells_lock.items()
        },
    )
    LOGGER.info("Well locked constructed")
    override_reassign_from = {}
    wd = opt_model_inputs.config.well_data
    col_name = wd.column_names
    for key, value in parameters.wells_reassign_from.items():
        # process scenarios where the wells were selected originally
        if key.isdigit():
            override_reassign_from[project_ids_to_cluster_ids[int(key)]] = [
                well_id_to_index(data, i) for i in value
            ]
        # process scenarios where the wells were not selected originally,
        # thus the parent_id of the wells are "unassigned"
        else:
            for i in value:
                cluster = wd.data[wd.data[col_name.well_id] == i][
                    col_name.cluster
                ].item()
                override_reassign_from[cluster] = [well_id_to_index(data, i)]

    override_add = OverrideAddInfo(
        override_reassign_from,
        {
            project_ids_to_cluster_ids[int(key)]: [
                well_id_to_index(data, i) for i in value
            ]
            for key, value in parameters.wells_reassign_to.items()
        },
    )

    all_remove_values = list(parameters.wells_remove.values())
    all_remove_values = [entry for entries in all_remove_values for entry in entries]
    all_remove_indices = [well_id_to_index(data, i) for i in all_remove_values]

    all_add_values = list(parameters.wells_reassign_to.values())
    all_add_values = [entry for entries in all_add_values for entry in entries]
    all_add_indices = [well_id_to_index(data, i) for i in all_add_values]

    LOGGER.info("Checking validity of input data")
    for well in all_add_indices:
        for project_wells in project_index_map.values():
            if well in project_wells and well not in all_remove_indices:
                raise HTTPException(
                    status_code=fastapi.status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Wells that are already in projects must "
                    + "be removed to assign to other projects",
                )

    override_selections = OverrideSelections(
        override_remove, override_add, override_lock
    )

    # Create opt model inputs, reassign wells to clusters, then re-instantiate
    # with the updated well data object and then pass the
    # new opt_model_inputs object to the Override Campaign

    # remove - reassign the well to another cluster (just say UNASSIGNED_CLUSTER)
    # add - change the cluster value of the add wells

    # a list of all the wells to remove from clusters
    remove_wells_cluster_id_to_well_id = {
        project_ids_to_cluster_ids[int(key)]: [well_id_to_index(data, i) for i in value]
        for key, value in parameters.wells_remove.items()
    }

    remove_wells_from_clusters_individual = {
        key: i
        for key, value in remove_wells_cluster_id_to_well_id.items()
        for i in value
    }

    add_wells_to_clusters = {
        project_ids_to_cluster_ids[int(key)]: [well_id_to_index(data, i) for i in value]
        for key, value in parameters.wells_reassign_to.items()
    }

    add_wells_to_clusters_individual = {
        key: i for key, value in add_wells_to_clusters.items() for i in value
    }

    LOGGER.info(f" Add wells to clusters {add_wells_to_clusters_individual}")
    LOGGER.info(f" Remove wells from clusters {remove_wells_from_clusters_individual}")

    LOGGER.info("Creating override campaign")
    override_campaign = OverrideCampaign(
        override_selections, opt_model_inputs, project_index_map, eff_metrics
    )
    override_selections_add_return = override_selections.add_widget_return
    return (
        override_campaign,
        project_id_map,
        opt_model_inputs,
        override_selections_add_return,
    )


def verify_parameter_validity(
    scenario_type: ScenarioType,
    parameters: Union[ScenarioParameters, ManualOverrideRequest],
) -> Tuple[ImpactMetrics, EfficiencyMetrics]:
    """
    Verifies that the impact and efficiency metrics selected by an end user
    are valid

    Parameters
    ----------
    scenarioType : ScenarioType
        The type of scenario

    parameters : Union[ScenarioParameters, ManualOverrideRequest]
        The ScenarioParameters or the ManualOverrideRequest received by the API
        to be executed

    Returns
    -------
    Tuple[ImpactMetrics, EfficiencyMetrics]
        A tuple containing the ImpactMetrics and EfficiencyMetrics objects

    Raises
    ------
    fastapi.status.HTTP_422_UNPROCESSABLE_ENTITY
        In case the parameters are invalid
    """
    im_metrics, eff_metrics = translate_input_selections(scenario_type, parameters)

    if not is_valid_scenario_dependent(scenario_type, im_metrics, eff_metrics):
        raise HTTPException(
            status_code=fastapi.status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Impact/Efficiency Weight selections are invalid",
        )
    return im_metrics, eff_metrics


def retrieve_well_data(
    parameters: Union[ScenarioParameters, ManualOverrideRequest, SimpleNamespace],
) -> pd.DataFrame:
    """
    Retrieve well data from MongoDB

    Parameters
    ----------
    parameters : Union[ScenarioParameters, ManualOverrideRequest, SimpleNamespace]
        The ScenarioParameters, the ManualOverrideRequest, or the SimpleNamespace
        (in the case of the data summary endpoint)
    Returns
    -------
    well data : pd.DataFrame
        The uploaded well data information from the data base

    Raises
    ------
    fastapi.status.HTTP_422_UNPROCESSABLE_ENTITY
        In case the parameters are invalid
    """
    well_data = collect_well_data(
        parameters.general_specifications.dataset_id,
        parameters.general_specifications.well_type,
    )

    if len(well_data) == 0:
        raise HTTPException(
            status_code=fastapi.status.HTTP_404_NOT_FOUND,
            detail="Could not find data in MongoDB: is it correctly uploaded?",
        )
    LOGGER.debug("Retrieved well data")
    return well_data


def get_lifetime_production(data: WellData) -> WellData:
    """
    Calculate an equivalent lifetime production in BoE for well data
    that combines both oil and gas production for individual wells

    Parameters
    ----------
    data : WellData
        WellData object

    Returns
    -------
    WellData
        WellData object with lifetime production calculated
    """
    col_names = data.col_names
    oil_prod_col = col_names.life_oil_production
    gas_prod_col = col_names.life_gas_production
    lifetime_prod_col = col_names.lifetime_production
    data.data[lifetime_prod_col] = (
        data.data[oil_prod_col] + data.data[gas_prod_col] / CONVERSION_FACTOR
    )
    return data


# pylint: disable = too-many-nested-blocks
def metric_data_check(
    metric_dictionary: Dict[str, Factor], well_data: WellData, eff_or_im: str
):
    """
    This method takes a dictionary of metrics and sets the value for
    "selected" to be True if the required data for that metric is available
    or False if the data is not available.

    Parameters
    ----------
    metric_dictionary: Dict[str, Factor]
        Dictionary containing the metrics.

    well_data: WellData
        Well Data class containing the user's input data

    eff_or_im: str
        Whether the set of factors are for impact or efficiency.

    Returns
    -------
    metric_dictionary: Dict[str, Factor]
        Dictionary containing all the metrics where each factor object
        has the value for "selected" set to false or true depending if
        the user had the required data or not.
    """

    for factor in metric_dictionary:
        if "child_factors" in metric_dictionary[factor]:
            for child_factor in metric_dictionary[factor]["child_factors"]:
                LOGGER.info(
                    f"Checking for available data for child factor: {child_factor}"
                )
                metric_dictionary[factor]["child_factors"][child_factor][
                    "selected"
                ] = check_for_required_data(child_factor, well_data, eff_or_im)

            if any(
                metric_dictionary[factor]["child_factors"][child_factor]["selected"]
                for child_factor in metric_dictionary[factor]["child_factors"]
            ):
                metric_dictionary[factor]["selected"] = True
            else:
                metric_dictionary[factor]["selected"] = False
        else:
            LOGGER.info(f"Checking for available data for factor: {factor}")
            metric_dictionary[factor]["selected"] = check_for_required_data(
                factor, well_data, eff_or_im
            )

    return metric_dictionary


def check_for_required_data(factor: str, well_data: WellData, eff_or_im: str):
    """
    Used to get determine if the required data is available and complete.
    Returns true if the user has the required data and False if that user does not

    Parameters
    ----------
    factor: str
       The name of the factor or child factor that requires specific data to use.

    well_data: WellData
       The data class containing the user's input data.

    eff_or_im: str
        Whether the set of factors are for impact or efficiency.

    Returns
    -------
    flag: True or False
       The flag indicating whether a user has the complete required data.
    """
    # Find the required data needed to use the factor
    code_base_factor = (
        FACTOR_MAP[factor] if factor in list(FACTOR_MAP.keys()) else factor
    )
    required_data_attr_name = (
        SUPP_IMPACT_METRICS[code_base_factor].required_data
        if eff_or_im == "impact"
        else SUPP_EFF_METRICS[code_base_factor].required_data
    )
    data_column_name = getattr(
        well_data.column_names,
        required_data_attr_name,
    )

    return well_data.has_fully_incomplete_data(data_column_name) is False


def create_histogram(data: WellData, column_name: str, num_bins: int):
    """
    Return bins and count values for the histogram created using
    a column of the dataset

    Parameters
    ----------
    column_name : str
        The column name in str format

    Returns
    -------
    x_values: List[str]
        The bins ranges of the histogram
    y_values: List[int]
        The counts of the histogram

    """
    counts, bins = np.histogram(data[column_name], bins=num_bins)
    x_values = [f"{int(bins[i])}-{int(bins[i + 1])}" for i in range(len(bins) - 1)]
    y_values = counts.tolist()
    return x_values, y_values
