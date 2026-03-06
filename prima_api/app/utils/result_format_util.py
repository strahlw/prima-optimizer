# Standard libs
import logging
from typing import Dict, List, Optional, Set, Union

# Installed libs
import fastapi
from fastapi import HTTPException
from primo.data_parser.well_data import WellData
from primo.opt_model.result_parser import Campaign, Project

# User-defined libs
from parameters import (
    MONGO_DATABASE,
    MONGO_URI,
    MONGO_WELL_COLLECTION,
    MYSQL_PROJECT_WELL_COLLECTION,
)
from utils import COLUMN_MAP
from utils.models import ManualOverrideRequest
from utils.mongo_io import (
    get_map_of_well_ids_in_wells_table,
    get_well_id_object_id_map,
    insert_data,
    rename_cols_for_mongodb,
)
from utils.mysql_io import get_list_of_well_obj_str, insert_data_to_mysql

LOGGER = logging.getLogger(__name__)


def reformat_project_results_for_db_storage(
    project: Project, project_id_map: Dict[int, str] = None
) -> Dict[str, Union[str, float, int]]:
    """
    Return a dictionary with all of the fields from the project class

    Parameters
    ----------
    project : Project
        a project

    Returns
    -------
    dict[str, Union[int, float]]
        information from projects for database storage
    """

    main_body = {
        "impact_score": project.impact_score,
        "efficiency_score": project.efficiency_score,
    }

    if project_id_map is not None and project.project_id in project_id_map:
        main_body["parent_project_id"] = project_id_map[project.project_id]
    else:
        main_body["parent_project_id"] = None

    return main_body


def reformat_campaign_results_for_db_storage(
    campaign: Campaign,
    scenario_id: int,
    project_id_map: Dict[int, Set[str]] = None,
) -> List[Dict[str, Union[int, float, str]]]:
    """
    Return a dictionary with the project data

    Parameters
    ---------
    campaign : Campaign
        The campaign consisting of many projects
    scenario_id : int
        scenario_id of the scenario
    task_id : str
        task_id for the optimization problem
    project_map : Dict[int : set[str]]
        mapping of parent project_ids to parent object_id strings

    Returns
    -------
    list[dict[str, Union[int, float, str]]]
        a list of dictionaries summarizing projects for database storage
    """

    project_data = []
    for _, project in campaign.projects.items():
        info = reformat_project_results_for_db_storage(project, project_id_map)
        info["scenario_id"] = scenario_id
        project_data.append(info)

    return project_data


def get_project_well_data_results_for_db_storage(
    project: Project, project_id: Optional[str] = None
):
    """
    Returns the necessary data for creating the well data to insert into the database

    Parameters
    ----------
    project : Project
        a project in a campaign

    project_id : str
        The project identifier to assign to project. If None, the project_id
        attribute from the project argument is used.


    Returns
    -------
    dict[str, Union[int, float]]
        dictionary of project information for database storage
    """
    if project_id is None:
        project_id = project.project_id

    return {
        "project_id": project_id,
        "efficiency_score": project.efficiency_score,
    }


def reformat_campaign_well_data_results_for_db_storage(
    campaign: Campaign,
    well_id_object_id_map: Dict[int, str],
    well_ids: Optional[Dict[int, str]] = None,
    well_ranking: Optional[bool] = True,
):
    """
    Returns the well_data in the format for the database
    Parameters
    ----------
    campaign : Campaign
        the campaign solution of the optimization problem
    well_id_object_id_map : Dict[int, str]
        Dictionary mapping well ids (int) to object ids (str)
    well_ids : Optional[Dict[int, str]]
        List of well_ids corresponding to well id strings that are in
        the wells table and do not need to be added

    Returns
    -------
    well_data_post_opt : list[dict[Union[str, int]]]
        a list of dictionaries that contain the information for the wells table

    """
    column_unmap = {value: key for key, value in COLUMN_MAP.items()}

    well_data_post_opt = []
    for _, project in campaign.projects.items():
        column_names = project.well_data.col_names
        well_data = rename_cols_for_mongodb(project.well_data.data, well_ranking)
        well_data = well_data.to_dict(orient="records")
        for _, well_entry in enumerate(well_data):
            individual_well_data = {
                "well_id": well_entry[column_unmap[column_names.well_id]],
                "cluster_id": project.project_id,
                "well_rank": well_entry["well_rank"],
                "dataset_json_id": well_id_object_id_map[
                    well_entry[column_unmap[column_names.well_id]]
                ],
                "priority_score": well_entry["priority_score"],
            }
            if well_ids is None:
                well_data_post_opt.append(individual_well_data)
            elif well_entry[column_unmap[column_names.well_id]] not in well_ids:
                well_data_post_opt.append(individual_well_data)

    return well_data_post_opt


def reformat_campaign_well_data_results_for_mysql_storage(
    campaign: Campaign, project_id_mysql: List[int], wells_table_ids: List[str]
):
    """
    Returns the well_data in the format for the database
    Parameters
    ----------
    campaign : Campaign
        the campaign solution of the optimization problem
    project_id_mysql : List[int]
        A list of auto-incremented id from the MySQL
        project table
    wells_table_ids : List[str]
        A list of string object ids corresponding to the wells table

    Returns
    -------
    project_well_map : list[dict[str, str]]
        a list of dictionaries that contains the project ids and well ids for
        the project_well table

    """
    project_well_map = []
    idx_well = 0
    for idx, (_, project) in enumerate(campaign.projects.items()):
        well_data = rename_cols_for_mongodb(project.well_data.data)
        well_data = well_data.to_dict(orient="records")
        for _, _ in enumerate(project.well_data):
            project_well = {
                "project_id": project_id_mysql[idx],
                "well_id": wells_table_ids[idx_well],
            }
            project_well_map.append(project_well)
            idx_well += 1
    return project_well_map


def reformat_campaign_well_data_results_for_mysql_storage_override(
    campaign: Campaign, project_id_mysql: List[int], wells_table_id_map: Dict[int, str]
):
    """
    Returns the well_data in the format for the database
    Parameters
    ----------
    campaign : Campaign
        the campaign solution of the optimization problem
    project_id_mysql : List[int]
        A list of auto-incremented id from the MySQL
        project table
    wells_table_id_map : Dict[int, str]
        A mapping of well_id (int) to _id (str) of the well
        in the wells table

    Returns
    -------
    project_well_map : list[dict[str, str]]
        a list of dictionaries that contains the project ids and well ids for
        the project_well table

    """
    column_unmap = {value: key for key, value in COLUMN_MAP.items()}

    project_well_map = []
    for idx, (_, project) in enumerate(campaign.projects.items()):
        column_names = project.well_data.col_names
        well_data = rename_cols_for_mongodb(project.well_data.data)
        well_data = well_data.to_dict(orient="records")
        for _, well_entry in enumerate(well_data):
            project_well = {
                "project_id": project_id_mysql[idx],
                "well_id": wells_table_id_map[
                    well_entry[column_unmap[column_names.well_id]]
                ],
            }
            project_well_map.append(project_well)
    return project_well_map


def well_id_to_index(well_data: WellData, well_id: int) -> int:
    """
    Utility function that returns the index of a well based on its well_id

    Parameters
    ----------
    well_data : WellData
        WellData object corresponding to the well data

    well_id : int
        the id of the well of interest

    Returns
    -------
    int
        the index of the well in the DataFrame
    """
    try:
        return well_data.data[
            well_data.data[well_data.col_names.well_id] == well_id
        ].index[0]
    except Exception as exc:
        raise HTTPException(
            status_code=fastapi.status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Based on your entries for general specifications, the well {well_id}"
                " has been filtered out of the data set. "
                "Please select a different well id for the manual override"
            ),
        ) from exc


# pylint: disable=too-many-locals
def process_override_results(
    opt_campaign: Dict,
    parameters: ManualOverrideRequest,
    project_id_map: Dict,
    well_ranking: Optional[bool],
):
    """
    Utility function to process the override recalculation and reoptimization results

    Parameters
    ----------
    opt_campaign : Dict
        A dictionary where keys are cluster numbers and values
        are list of wells for each cluster in the P&A projects.

    parameters : ManualOverrideRequest
        the id of the well of interest

    project_map : Dict
        mapping of parent project_ids to parent object_id strings

    Returns
    -------
    None
    """
    LOGGER.info("Gathering well ids in wells table from parent project")
    well_obj_str = get_list_of_well_obj_str(parameters.parent_project_ids)
    # map {well_id (int) : _id (MongoDB wells table, str)}
    well_ids_to_object_ids_in_parent = get_map_of_well_ids_in_wells_table(well_obj_str)

    LOGGER.info("Reformatting project results")
    project_data = reformat_campaign_results_for_db_storage(
        opt_campaign,
        parameters.child_scenario_id,
        project_id_map,
    )
    LOGGER.info("Extracting well id map information")
    well_id_object_id_map = get_well_id_object_id_map(
        parameters.general_specifications.dataset_id
    )

    LOGGER.info("Adding wells to the wells table")
    well_data_db_override = reformat_campaign_well_data_results_for_db_storage(
        opt_campaign,
        well_id_object_id_map,
        well_ids_to_object_ids_in_parent,
        well_ranking,
    )

    if len(well_data_db_override) > 0:
        LOGGER.info(f"Well data result example : {well_data_db_override[0]}")
        LOGGER.info("Inserting well data into the wells mongo db table")
        wells_table_ids_override = [
            str(obj)
            for obj in insert_data(
                well_data_db_override, MONGO_URI, MONGO_DATABASE, MONGO_WELL_COLLECTION
            ).inserted_ids
        ]
        LOGGER.info(
            f"Length of wells table ids adding: {len(wells_table_ids_override)}"
        )
        if len(wells_table_ids_override) != len(well_data_db_override):
            LOGGER.info(
                "The wells table ids and well data db override are different lengths!"
            )
            assert False
        LOGGER.info(f"wells table ids : {wells_table_ids_override}")
        well_ids_to_object_ids_in_parent.update(
            {
                well_data_db_override[i]["well_id"]: wells_table_ids_override[i]
                for i in range(len(wells_table_ids_override))
            }
        )

    LOGGER.info("Inserting project results for override reoptimization")
    LOGGER.info(f"Project data: {project_data}")
    project_id_mysql = insert_data_to_mysql(project_data)

    LOGGER.info(f"Length of project ids : {len(project_data)}")

    LOGGER.info(
        f"Example data for override reoptimization"
        f"inserted to projects mysql table : {project_data[0]}"
    )

    project_well_map = reformat_campaign_well_data_results_for_mysql_storage_override(
        opt_campaign,
        project_id_mysql,
        well_ids_to_object_ids_in_parent,
    )

    LOGGER.info(
        "Writing results to project_well table of MySQL"
        "database for override reoptimization"
    )
    insert_data_to_mysql(
        project_well_map,
        collection_id=MYSQL_PROJECT_WELL_COLLECTION,
    )

    LOGGER.info(
        f"Example data for override reoptimization "
        f"inserted to project_well mysql table : {project_well_map[0]}"
    )
    LOGGER.info(
        f"All the data for override reoptimization "
        f"inserted to the project well mysql table : {project_well_map}"
    )

    column_unmap = {value: key for key, value in COLUMN_MAP.items()}
    # get project results for comparison
    for project_override in opt_campaign.projects.values():
        column_names = project_override.well_data.col_names
        well_data = rename_cols_for_mongodb(
            project_override.well_data.data, well_ranking
        )
        well_data = well_data.to_dict(orient="records")
        LOGGER.info(f"Project : {project_override.project_id}")
        for well_entry in well_data:
            LOGGER.info(f"Well id : {well_entry[column_unmap[column_names.well_id]]}")
    LOGGER.info("\n")
    campaign_information = opt_campaign.get_campaign_summary().to_dict(orient="records")
    for project_override in campaign_information:
        LOGGER.info(f"Project ID : {project_override['Project ID']}")
        LOGGER.info(f"Impact Score : {project_override['Impact Score [0-100]']}")
        LOGGER.info(
            f"Efficiency Score [0-100] : {project_override['Efficiency Score [0-100]']}"
        )
    LOGGER.info("\n")
