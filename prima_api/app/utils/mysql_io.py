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
Implements methods for reading and writing from MySQL database 
"""
# Standard libs
import logging
from typing import Dict, List

# Installed libs
import fastapi
import mysql.connector
import numpy as np
from fastapi import HTTPException

# User-defined libs
from parameters import (
    MYSQL_DATABASE,
    MYSQL_HOST,
    MYSQL_PASS,
    MYSQL_PORT,
    MYSQL_PROJECT_COLLECTION,
    MYSQL_PROJECT_WELL_COLLECTION,
    MYSQL_USER,
)

LOGGER = logging.getLogger(__name__)

# pylint: disable=too-many-positional-arguments, too-many-arguments, unused-argument
# TODO: change the inputs using **kwargs
def query_database(
    query: str,
    host: str = MYSQL_HOST,
    port: str = MYSQL_PORT,
    db: str = MYSQL_DATABASE,
    user: str = MYSQL_USER,
    password: str = MYSQL_PASS,
) -> List[Dict]:
    """
    Queries a MySQL database and collection

    Parameters
    ----------
    query : str
        The query to run in the database

    host : str
        Host for the MySQL database

    port : str
        Port for the MySQL database

    db : str
        Database in MySQL to be queried

    user : str
        User name for accessing the MySQL

    password : str
        Password for accessing the MySQL

    collection_id : str
        Collection in a specific database to be queried

    Returns
    -------
    List[Dict]
        Returns the result of the query
    """
    try:
        # Connect to MySQL database
        connection = mysql.connector.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=db,
        )
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query)
        results = cursor.fetchall()  # Get all results
        cursor.close()
        connection.close()

        return results
    except mysql.connector.Error as err:
        LOGGER.error(f"Error: {err}")
        return []


def get_wells_ids_from_project_id(project_id: int) -> List[str]:
    """
    Queries the project_well table and returns a list of
    strings corresponding to the wells that are included
    in all the projects included in the project_ids parameter.

    Parameters
    ----------
    project_id :
        project id

    Returns
    -------
    List[str]
        List of well obj ids (as strings) from the wells table
        that are in the project_ids
    """

    query = (
        f"SELECT well_id FROM {MYSQL_PROJECT_WELL_COLLECTION} "
        f"WHERE project_id IN ({project_id});"
    )
    well_ids = [well["well_id"] for well in query_database(query)]
    if len(well_ids) == 0:
        raise HTTPException(
            status_code=fastapi.status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                "The project wells table query returned an empty list."
                " Check your project id."
            ),
        )
    return well_ids


def get_list_of_well_obj_str(project_ids: List[int]) -> List[str]:
    """
    Queries the project_well table and returns a list of
    strings corresponding to the wells that are included
    in all the projects included in the project_ids parameter.

    Parameters
    ----------
    project_ids : List[int]
        List of integers corresponding to project ids to query

    Returns
    -------
    List[str]
        List of well obj ids (as strings) from the wells table
        that are in the project_ids
    """

    query = (
        f"SELECT well_id FROM {MYSQL_PROJECT_WELL_COLLECTION} "
        f"WHERE project_id IN (%s);"
    )
    query_expanded = query % ",".join("%s" for i in range(len(project_ids)))
    final_query = query_expanded % tuple(project_ids)
    well_ids = [well["well_id"] for well in query_database(final_query)]
    if len(well_ids) == 0:
        raise HTTPException(
            status_code=fastapi.status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                "The project wells table query returned an empty list."
                "This should never happen. Check that valid project"
                "ids were supplied."
            ),
        )
    return well_ids


def get_list_of_project_data(project_ids: List[int]) -> Dict[int, Dict[str, float]]:
    """
    Queries the projects table and returns a dictionary of project_id : project_data
    where project_data includes the impact and efficiency score for the project

    Parameters
    ----------
    project_ids : List[int]
        List of integers corresponding to project ids to query

    Returns
    -------
    Dict[int, Dict[str, float]]
        Dictionary of project data including impact scores and efficiency scores
    """

    query = f"SELECT * FROM {MYSQL_PROJECT_COLLECTION} " f"WHERE id IN (%s);"
    query_expanded = query % ",".join("%s" for i in range(len(project_ids)))
    final_query = query_expanded % tuple(project_ids)
    project_data = {
        project_id: {
            "impact_score": project["impact_score"],
            "efficiency_score": project["efficiency_score"],
        }
        for project_id, project in zip(project_ids, query_database(final_query))
    }
    if len(project_data) == 0:
        raise HTTPException(
            status_code=fastapi.status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=("The projects table query returned an empty list."),
        )
    return project_data


def get_map_project_id_well_obj_str(project_id: int) -> Dict[int, List[str]]:
    """
    Queries the project_well table and returns a list of well obj strings
    that correspond to a project id

    Parameters
    ----------
    project_id : int
        project id from mysql

    Returns
    -------
    Dict[int, List[str]]
        Dictionary mapping the project id to the list
        of well string object ids in the wells table
    """
    return {project_id: get_list_of_well_obj_str([project_id])}


def get_map_project_ids_well_obj_str(project_ids: List[int]) -> Dict[int, List[str]]:
    """
    Queries the project_well table and returns a list of well obj strings
    that correspond to a project id

    Parameters
    ----------
    project_ids : List[int]
        project id list from mysql

    Returns
    -------
    Dict[int, List[str]]
        Dictionary mapping the project id to the list
        of well string object ids in the wells table
    """
    return {
        project_id: well_ids
        for projects in [
            get_map_project_id_well_obj_str(project_id) for project_id in project_ids
        ]
        for project_id, well_ids in projects.items()
    }


# pylint: disable=too-many-positional-arguments, too-many-arguments,too-many-locals
# TODO: change the inputs using **kwargs
def insert_data_to_mysql(
    data: List[Dict],
    host: str = MYSQL_HOST,
    port: str = MYSQL_PORT,
    user: str = MYSQL_USER,
    password: str = MYSQL_PASS,
    db: str = MYSQL_DATABASE,
    collection_id: str = MYSQL_PROJECT_COLLECTION,
):
    """
    Inserts data into MySQL database.

    Parameters
    ----------
    data : List[Dict]
        The data to be inserted into MySQL.
    host : str
        Host for the MySQL database.
    port : str
        Port for the MySQL database.
    user : str
        User name for accessing the MySQL
    password : str
        Password for accessing the MySQL
    db : str
        Database in MySQL to be queried.
    collection_id : str
        Collection in a specific database to be queried.

    """
    for record in data:
        for key, value in record.items():
            if isinstance(value, np.float64):
                record[key] = float(value)

    try:
        # Connect to MySQL database
        connection = mysql.connector.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=db,
        )
        cursor = connection.cursor()

        columns = ", ".join(data[0].keys())
        values_list = [tuple(record.values()) for record in data]

        insert_query = (
            f"INSERT INTO {collection_id} ({columns}) "
            f"VALUES ({', '.join(['%s'] * len(data[0]))})"
        )

        cursor.executemany(insert_query, values_list)

        inserted_ids = []
        start_id = cursor.lastrowid  # Get the first inserted data ID
        for i in range(len(data)):
            inserted_ids.append(start_id + i)

        connection.commit()
        cursor.close()
        connection.close()
        LOGGER.info(f"Inserted {len(data)} records into {collection_id}")

    except mysql.connector.Error as err:
        LOGGER.error(f"Error inserting data into MySQL: {err}")
        connection.rollback()

    return inserted_ids


# pylint: disable=too-many-positional-arguments, too-many-arguments
# TODO: change the inputs using **kwargs
def remove_data(
    query: Dict[str, str],
    host: str = MYSQL_HOST,
    port: str = MYSQL_PORT,
    user: str = MYSQL_USER,
    password: str = MYSQL_PASS,
    db: str = MYSQL_DATABASE,
    collection_id: str = MYSQL_PROJECT_COLLECTION,
):
    """
    Deletes data that matches query from MySQL collection
    Parameters
    ----------
    query : Dict[str, str]
        Query identifying the data to be removed (where condition).
    host : str
        Host for the MySQL database.
    port : str
        Port for the MySQL database.
    user : str
        User name for accessing the MySQL
    password : str
        Password for accessing the MySQL
    db : str
        Database in MySQL to be queried.
    collection_id : str
        Table in the MySQL database to delete from.
    """
    try:
        # Connect to MySQL database
        connection = mysql.connector.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=db,
        )
        cursor = connection.cursor()

        # Construct DELETE query using the provided
        # query dictionary (assume it's a simple WHERE clause)
        where_clause = " AND ".join([f"{key} = %s" for key in query.keys()])
        delete_query = f"DELETE FROM {collection_id} WHERE {where_clause}"
        cursor.execute(delete_query, tuple(query.values()))

        connection.commit()  # Commit the transaction
        cursor.close()
        connection.close()
        LOGGER.info(f"Deleted records from {collection_id} where {where_clause}")
    except mysql.connector.Error as err:
        LOGGER.error(f"Error deleting data from MySQL: {err}")
        # Rollback in case of error
        connection.rollback()
