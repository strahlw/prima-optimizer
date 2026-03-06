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
Implements methods for reading and writing from MongoDB 
"""
# Standard libs
import logging
from typing import Dict, List, Optional

# Installed libs
import fastapi
import pandas as pd
import pymongo
from bson.objectid import ObjectId
from fastapi import HTTPException
from pymongo import DeleteMany, MongoClient

# User-defined libs
from parameters import (
    MONGO_DATABASE,
    MONGO_DATASET_COLLECTION,
    MONGO_RANK_COLLECTION,
    MONGO_URI,
    MONGO_WELL_COLLECTION,
)
from primo_executor.primo_worker_parameters import SCORE_COLUMN_MAP
from utils import COLUMN_MAP

LOGGER = logging.getLogger(__name__)


def read_cols_from_mongodb(data: pd.DataFrame) -> pd.DataFrame:
    """
    Front use column names that are different from what backend uses.
    Translate column names written in MongoDB to what backend expects

    Parameters
    ----------
    data : pd.DataFrame
        DataFrame that uses column names as backend expects

    Returns
    ----------
    pd.DataFrame
        DataFrame that uses column names as front end expects

    """
    return data.rename(columns=COLUMN_MAP)


def rename_cols_for_mongodb(
    data: pd.DataFrame, well_ranking: Optional[bool] = True
) -> pd.DataFrame:
    """
    Front use column names that are different from what backend uses.
    Correct col names before writing to MongoDB to ensure front end works
    as expected

    Parameters
    ----------
    data : pd.DataFrame
        DataFrame that uses column names as backend expects

    well_ranking : bool
        Whether or not the user has selected well-ranking
    Returns
    ----------
    pd.DataFrame
        DataFrame that uses column names as front end expects

    """
    # Rename columns to what MongoDB expects before writing
    column_names_map = {
        col_name: mongo_db_col_name
        for mongo_db_col_name, col_name in COLUMN_MAP.items()
    }

    score_column_map = {**SCORE_COLUMN_MAP}
    if not well_ranking:
        score_column_map.pop("Priority Score [0-100]", None)
        score_column_map.update({"Priority Score User Input": "priority"})

    # add scoring columns
    original_columns = data.columns
    for column in original_columns:
        for col_name in score_column_map:
            if column.startswith(col_name) and "Score" in column:
                column_names_map[column] = score_column_map[col_name] + "_score"

    return data.rename(columns=column_names_map)


def query_database(
    query: Dict[str, str],
    uri: str = MONGO_URI,
    db: str = MONGO_DATABASE,
    collection_id: str = MONGO_DATASET_COLLECTION,
) -> List[Dict]:
    """
    Queries a MongoDB database and collection

    Parameters
    ----------
    query : Dict[str, str]
        The query to run in database

    uri : str
        URI for the MongoDB

    db : str
        Database in MongoDB to be queried

    collection_id : str
        Collection in a specific database to be queried

    Returns
    -------
    List[Dict]
        Returns the result of the query
    """
    with MongoClient(uri) as client:
        database = client[db]
        collection = database[collection_id]
        return list(collection.find(query))


def collect_well_data(dataset_id: int, well_types: List[str]) -> pd.DataFrame:
    """
    Collects all relevant well data from MongoDB and returns as a pandas DataFrame


    Parameters
    ----------
    dataset_id : int
        ID of dataset for which data is to be collected

    well_types : List[str]
        Well types under consideration for which data is to be collected

    Returns
    -------
    pd.DataFrame
        All wells collected belonging to a given organization for a given dataset
        and with matching well types

    """
    query = {"dataset_id": dataset_id}
    well_data = query_database(query)
    LOGGER.info(f"In collect_well_data, length of data retrieved is: {len(well_data)}")

    if len(well_data) == 0:
        raise ValueError("The database query returned no well data!")

    data = []

    for obj in well_data:
        row = []
        well_type = obj["json"].get("well_type")
        if well_type in well_types:
            # Is the well of type we want to consider?
            for col_name in COLUMN_MAP:
                row.append(obj["json"].get(col_name))
            row.append(str(obj["_id"]))
            data.append(row)

    column_names = list(COLUMN_MAP.values())
    column_names.append("dataset_json_id")

    return pd.DataFrame(data, columns=column_names)


def get_well_id_object_id_map(dataset_id: int) -> Dict[int, str]:
    """
    Returns a map of well id integers to well id object strings (_id in datasets_json)


    Parameters
    ----------
    dataset_id : int
        ID of dataset for which data is to be collected

    Returns
    -------
    Dict[int, str]
        Dictionary mapping well ids (int) to the string object id of the datasets table (str)

    """
    query = {"dataset_id": dataset_id}
    well_data = query_database(query)
    return {obj["json"]["well_id"]: str(obj["_id"]) for obj in well_data}


def get_map_of_well_ids_in_wells_table(
    well_str: List[str],
) -> Dict[int, str]:
    """
    Returns the set of well ids that correspond to
    all the wells in the wells table

    Parameters
    ----------
    well_str : List[str]
        List of strings corresponding to object ids on the wells table
    Returns
    -------
    Dict[int, str]
        Map of well ids to object id strings in the
        wells table
    """
    LOGGER.info(f"Well strings for mongo db wells table query = {well_str}")
    wells_table_records = query_database(
        {"_id": {"$in": [ObjectId(id) for id in well_str]}},
        collection_id=MONGO_WELL_COLLECTION,
    )
    if len(wells_table_records) == 0:
        raise HTTPException(
            status_code=fastapi.status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="The wells table query returned an empty list. This should never happen.",
        )
    return {
        obj["well_id"]: well_str[idx] for idx, obj in enumerate(wells_table_records)
    }


def get_well_ids_data_from_wells_table(
    well_str: List[str],
) -> Dict[int, Dict[str, float]]:
    """
    Returns the well data from the wells table
    given a list of well ids for the table

    Parameters
    ----------
    well_str : List[str]
        List of strings corresponding to object ids on the wells table
    Returns
    -------
    Dict[int, Dict[str, float]]
        Dictionary of well_id to well data including well_rank, cluster_id, and priority_score
    """
    LOGGER.info(f"Well strings for mongo db wells table query = {well_str}")
    wells_table_records = query_database(
        {"_id": {"$in": [ObjectId(id) for id in well_str]}},
        collection_id=MONGO_WELL_COLLECTION,
    )
    if len(wells_table_records) == 0:
        raise HTTPException(
            status_code=fastapi.status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="The wells table query returned an empty list. This should never happen.",
        )
    return {
        obj["well_id"]: {
            "cluster_id": obj["cluster_id"],
            "well_rank": obj["well_rank"],
            "priority_score": obj["priority_score"],
        }
        for obj in wells_table_records
    }


def get_cluster_id_from_well_id(well_str: str) -> int:
    """
    Returns the cluster id that corresponds
    to a well obj string id of the wells table

    Parameters
    ----------
    well_str : List[str]
        List of strings corresponding to object ids on the wells table
    Returns
    -------
    int
        cluster_id associated with the well_id
    """
    LOGGER.info(f"Well strings for mongo db wells table query = {well_str}")
    wells_table_records = query_database(
        {"_id": ObjectId(well_str)}, collection_id=MONGO_WELL_COLLECTION
    )
    if len(wells_table_records) == 0:
        raise HTTPException(
            status_code=fastapi.status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="The wells table query returned an empty list. This should never happen.",
        )
    return wells_table_records[0]["cluster_id"]


def insert_data(
    data: List[Dict],
    uri: str = MONGO_URI,
    db: str = MONGO_DATABASE,
    collection_id: str = MONGO_DATASET_COLLECTION,
) -> pymongo.results.InsertManyResult:
    """
    Inserts data into MongoDB collection

    Parameters
    ----------
    data : List[Dict]
        The data to be inserted into MongoDB
    uri : str
        URI for the MongoDB

    db : str
        Database in MongoDB to be queried

    collection_id : str
        Collection in a specific database to be queried

    Returns
    -------
    pymongo.results.InsertManyResult
        Returns the insertion object
    """
    with MongoClient(uri) as client:
        database = client[db]
        collection = database[collection_id]
        results = collection.insert_many(data)
    return results


def remove_data(
    query: Dict[str, str],
    uri: str = MONGO_URI,
    db: str = MONGO_DATABASE,
    collection_id: str = MONGO_DATASET_COLLECTION,
):
    """
    Deletes data that matches query from MongoDB collection
    Parameters
    ----------
    query : Dict[str, str]
        Query identifying the data to be removed

    uri : str
        URI for the MongoDB

    db : str
        Database in MongoDB to be queried

    collection_id : str
        Collection in a specific database to be queried
    """
    with MongoClient(uri) as client:
        database = client[db]
        collection = database[collection_id]
        collection.bulk_write([DeleteMany(query)])


def convert_rank_results(
    task_id: str, ranked_data: pd.DataFrame, well_ranking: Optional[bool] = True
):
    """
    Converts rank results in a format that can be easily written to MongoDB

    Parameters
    ----------
    task_id : str
        The ID of the task being run

    ranked_data : pd.DataFrame
        Ranked well data

    well_ranking : Optional[bool]
        whether or not the user has selected well ranking

    Returns
    -------
    None
    """
    well_data = rename_cols_for_mongodb(ranked_data, well_ranking)
    well_data = well_data.to_dict(orient="records")
    output = []
    for rank, well_info in enumerate(well_data):
        well_info["well_rank"] = rank + 1
        well_details = {
            "task_id": task_id,
            "well_id": well_info["well_id"],
            "well_rank": well_info["well_rank"],
            "dataset_json_id": well_info["dataset_json_id"],
        }
        score_fields = {
            score_name: well_info[score_name]
            for score_name in well_info
            if "score" in score_name
        }
        well_details.update(score_fields)
        output.append(well_details)
    return output


def write_rank_results(task_id: str, ranked_data: pd.DataFrame):
    """
    Writes the results obtained for ranking wells back to Mongo Database

    Parameters
    ----------

    task_id : str
        The ID of the task being run

    ranked_data : pd.DataFrame
        Ranked well data

    Returns
    -------
    None
    """
    output = convert_rank_results(task_id, ranked_data)

    insert_data(output, collection_id=MONGO_RANK_COLLECTION)


def remove_rank_results(task_id: str):
    """
    Remove the results obtained for ranking wells back to Mongo Database.
    The results are identified by task_id

    Parameters
    ----------
    task_id : str
        The ID of the task whose results are to be removed

    Returns
    -------
    None
    """

    remove_data({"task_id": task_id}, collection_id=MONGO_RANK_COLLECTION)


# pylint: disable=too-many-arguments
def _add_data_to_database(
    file_path: str,
    dataset_id: str,
    uri: str = MONGO_URI,
    db: str = MONGO_DATABASE,
    collection_id: str = MONGO_DATASET_COLLECTION,
):
    """
    Adds data from an Excel file to database.
    This function is primarily useful for testing and development.
    NOTE: Method does no error checking/validation

    Parameters
    ----------
    file_path : str
        Path of the csv file to write locally to MongoDB

    dataset_id : str
        Dataset id to attach to dataset

    uri : str
        URI for the MongoDB

    db : str
        Database in MongoDB to be queried

    collection_id : str
        Collection in a specific database to be queried

    """
    data = pd.read_csv(file_path)
    data = rename_cols_for_mongodb(data)
    data_dict = data.to_dict(orient="records")
    write_data = []
    for well_data in data_dict:
        well_obj = {
            "dataset_id": dataset_id,
            "json": well_data,
        }
        write_data.append(well_obj)

    insert_data(write_data, uri, db, collection_id)
