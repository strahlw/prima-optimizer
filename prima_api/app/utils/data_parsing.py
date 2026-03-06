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
Utility for parsing input data (GitHub issue #47)
"""
# Standard libs
import logging
from typing import Any, Dict, List, Set, Union

# Installed libs
import fastapi
import pandas as pd
from fastapi import HTTPException

LOGGER = logging.getLogger(__name__)

# snake case column name to name expected by front end
SNAKECASE_COLUMN_NAME_TO_DB_KEY = {
    "number_of_schools_near_the_well": "num_of_schools_near_well",
    "number_of_hospitals_near_the_well": "num_of_hospitals_near_well",
    "5_year_oil_production": "five_year_oil_production",
    "5_year_gas_production": "five_year_gas_production",
    "well_integrity_issues": "well_integrity",
    "placeholder_1": "placeholder_one",
    "placeholder_2": "placeholder_two",
    "placeholder_3": "placeholder_three",
    "placeholder_4": "placeholder_four",
    "placeholder_5": "placeholder_five",
    "placeholder_6": "placeholder_six",
    "placeholder_7": "placeholder_seven",
    "placeholder_8": "placeholder_eight",
    "placeholder_9": "placeholder_nine",
    "placeholder_10": "placeholder_ten",
    "placeholder_11": "placeholder_eleven",
    "placeholder_12": "placeholder_twelve",
    "placeholder_13": "placeholder_thirteen",
    "placeholder_14": "placeholder_fourteen",
    "placeholder_15": "placeholder_fifteen",
    "placeholder_16": "placeholder_sixteen",
    "placeholder_17": "placeholder_seventeen",
    "placeholder_18": "placeholder_eighteen",
    "placeholder_19": "placeholder_nineteen",
    "placeholder_20": "placeholder_twenty",
    "annual_gas_production": "ann_gas_production",
    "annual_oil_production": "ann_oil_production",
}


BOOLEAN_COLUMN_NAMES_TO_CONVERT = [
    "state_wetlands_close_range",
    "state_wetlands_wide_range",
    "federal_wetlands_close_range",
    "federal_wetlands_wide_range",
    "buildings_close_range",
    "buildings_wide_range",
]

BOOLEAN_COLUMN_NAMES = [
    "h2s_leak",
    "leak",
    "violation",
    "incident",
    "compliance",
    "water_source_nearby",
    "known_soil_or_water_impact",
    "state_wetlands_close_range",
    "state_wetlands_wide_range",
    "federal_wetlands_close_range",
    "federal_wetlands_wide_range",
    "buildings_close_range",
    "buildings_wide_range",
    "brine_leak",
    "high_pressure_observed",
    "in_tribal_land",
    "likely_to_be_orphaned",
    "otherwise_incentivized_well",
    "well_integrity",
    "agriculture_area_nearby",
    "historical_preservation_site",
    "home_use_gas_well",
    "post_plugging_land_use",
    "surface_equipment_on_site",
    "endangered_species_on_site",
    "placeholder_one",
    "placeholder_two",
    "placeholder_three",
    "placeholder_four",
    "placeholder_five",
    "placeholder_eleven",
    "placeholder_twelve",
    "placeholder_thirteen",
    "placeholder_fourteen",
    "placeholder_fifteen",
]

NUMERIC_COLUMN_NAMES = [
    "well_id",
    "census_tract_id",
    "state_code",
    "county_code",
    "land_area",
    "num_of_schools_near_well",
    "num_of_hospitals_near_well",
    "five_year_oil_production",
    "five_year_gas_production",
    "lifelong_oil_production",
    "lifelong_gas_production",
    "ann_oil_production",
    "ann_gas_production",
    "age",
    "depth",
    "elevation_delta",
    "distance_to_road",
    "latitude",
    "longitude",
    "population_density",
    "hydrocarbon_losses",
    "cost_of_plugging",
    "idle_status_duration",
    "mechanical_integrity_test",
    "number_of_mcws_nearby",
    # "proximity_to_geologic_faults",
    "placeholder_six",
    "placeholder_seven",
    "placeholder_eight",
    "placeholder_nine",
    "placeholder_ten",
    "placeholder_sixteen",
    "placeholder_seventeen",
    "placeholder_eighteen",
    "placeholder_nineteen",
    "placeholder_twenty",
    "priority_score_user_input",
]

STRING_COLUMN_NAMES = ["operator_name", "well_type"]

# in the case that the column contains numbers (PA demo)
COLUMNS_TO_CONVERT_TO_STRINGS = ["well_name"]

REQUIRED_COLUMNS = ["well_id", "latitude", "longitude"]

WELL_ID_COL_NAME = "well_id"


def convert_to_snake_case(name: str) -> str:
    """
    Converts a column name to snake case assuming the name is space separated

    Parameters
    ----------
    name : str
        string that is not snake case and space separated

    Returns
    -------
    str
        string that is snake case
    """
    return "_".join(name.lower().split())


def extract_name(name: str) -> str:
    """
    Extracts a name from a column name.
    Assumes that the units at the end of the string are enclosed by brackets.

    Parameters
    ----------
    name : str
        string that has bracketed units at the end

    Returns
    -------
    str
        string without the bracketed units
    """
    if "(Near)" in name:
        return name.split(" (")[0] + " close range"
    if "(Far)" in name:
        return name.split(" (")[0] + " wide range"
    if "(" in name:
        return name.split(" (")[0]
    return name.split(" [")[0]


def convert_hyphen_to_underscore(name: str) -> str:
    """
    Replaces hyphens with underscores

    Parameters
    ----------
    name : str
        string with hyphens

    Returns
    -------
    str
        string with underscores in place of hyphens
    """
    return name.replace("-", "_")


def convert_name(name: str) -> str:
    """
    Converts a name from the template file to the key for the database

    Parameters
    ----------
    name : str
        column name from template file

    Returns
    -------
    str
        key for database
    """
    if "[" in name or "(" in name:
        name = extract_name(name)

    if "-" in name:
        name = convert_hyphen_to_underscore(name)

    return convert_to_snake_case(name)


def replace_boolean_fields(dataframe: pd.DataFrame, col: str) -> pd.DataFrame:
    """
    Replaces string entries with 1s and 0s

    Parameters
    ----------
    dataframe : pd.DataFrame
        dataframe containing column to replace Boolean fields
    col : str
        column to perform the operation

    Returns
    -------
    pd.DataFrame
        the same dataframe with adjusted values
    """
    bool_replace_dict = {
        "Yes": 1,
        "yes": 1,
        "Y": 1,
        "y": 1,
        "No": 0,
        "no": 0,
        "N": 0,
        "n": 0,
        "true": 1,
        "TRUE": 1,
        "True": 1,
        "false": 0,
        "False": 0,
        "FALSE": 0,
    }
    # replaces all entries and leaves any entries that are not in the dictionary
    with pd.option_context("future.no_silent_downcasting", True):
        dataframe[col] = (
            dataframe[col]
            .map(bool_replace_dict)
            .fillna(dataframe[col])
            .infer_objects(copy=False)
        )
    return dataframe


def replace_boolean_columns(dataframe: pd.DataFrame) -> pd.DataFrame:
    """
    Converts all the necessary column entries from Boolean strings to 0s and 1s

    Parameters
    ----------
    dataframe : pd.DataFrame
        dataframe containing column to replace Boolean fields

    Returns
    -------
    pd.DataFrame
        the same dataframe with adjusted values
    """
    for column_name in BOOLEAN_COLUMN_NAMES_TO_CONVERT:
        if column_name in dataframe.columns:
            dataframe = replace_boolean_fields(dataframe, column_name)
    return dataframe


def is_int_or_float(x: Any) -> bool:
    """
    Checks if an element is an integer or float
    Used for pandas filtering

    Parameters
    ----------
    x : Any
        entry of any type to check

    Returns
    -------
    bool
        True if numeric, false if not
    """
    if isinstance(x, (int, float)):
        return True
    try:
        float(x)
        return True
    except ValueError:
        return False


def check_column_numeric(
    dataframe: pd.DataFrame,
    col: str,
    problematic_well_info: Dict[Union[str, int], List[str]],
):
    """
    Checks if all the entries of a column are numeric

    Parameters
    ----------
    dataframe : pd.DataFrame
        dataframe containing column to replace Boolean fields
    col : str
        name of the column to perform the operation
    problematic_well_info : Dict[Union[str, int], List[str]]
        dictionary mapping well id to columns with problematic entries

    Returns
    dataframe : pd.DataFrame
        the dataframe with numeric columns

    """
    problematic_well_ids = dataframe[~dataframe[col].apply(is_int_or_float)][
        WELL_ID_COL_NAME
    ].values
    for well_id in problematic_well_ids:
        update_problematic_entry_dictionary(problematic_well_info, well_id, col)


def check_column_string(
    dataframe: pd.DataFrame,
    col: str,
    problematic_well_info: Dict[Union[str, int], List[str]],
):
    """
    Checks if all the entries of a column are numeric

    Parameters
    ----------
    dataframe : pd.DataFrame
        dataframe containing column to replace Boolean fields
    col : str
        name of the column to perform the operation
    problematic_well_info : Dict[Union[str, int], List[str]]
        dictionary mapping well id to columns with problematic entries


    """
    problematic_well_ids = dataframe[
        ~dataframe[col].apply(lambda x: isinstance(x, str) or pd.isna(x))
    ][WELL_ID_COL_NAME].values
    for well_id in problematic_well_ids:
        update_problematic_entry_dictionary(problematic_well_info, well_id, col)


def update_problematic_entry_dictionary(
    dictionary: Dict[Union[str, int], List[str]], key: Union[str, int], value: str
):
    """
    Updates the problematic well info dictionary

    Parameters:
    -----------
    dict : Dict[Union[str, int], List[str]]
        the dictionary
    key : Union[str, int]
        the key
    value : str
        the value
    """
    if key in dictionary and value not in dictionary[key]:
        dictionary[key].append(value)
    else:
        dictionary[key] = [value]


def create_string_column(
    dataframe: pd.DataFrame,
    col: str,
    problematic_well_info: Dict[Union[str, int], List[str]],
) -> pd.DataFrame:
    """
    Changes all the entries to strings

    Parameters
    ----------
    dataframe : pd.DataFrame
        dataframe containing column to replace Boolean fields
    col : str
        name of the column to perform the operation

    problematic_well_info : Dict[Union[str, int], List[str]]
        dictionary mapping well id to columns with problematic entries

    Returns
    -------
    pd.DataFrame
        a dataframe where the column specified now has string values
    """
    dataframe[col] = dataframe[col].astype(str, errors="ignore")
    problematic_well_ids = dataframe[
        ~dataframe[col].apply(lambda x: isinstance(x, str))
    ][WELL_ID_COL_NAME].values
    for well_id in problematic_well_ids:
        update_problematic_entry_dictionary(problematic_well_info, well_id, col)
    return dataframe


def check_column_boolean(
    dataframe: pd.DataFrame,
    col: str,
    problematic_well_info: Dict[Union[str, int], List[str]],
):
    """
    Checks if all the entries of a column are expected Boolean values
    i.e. "Yes" or "No" or empty

    Parameters
    ----------
    dataframe : pd.DataFrame
        dataframe containing column to replace Boolean fields
    col : str
        name of the column to perform the operation
    problematic_well_info : Dict[Union[str, int], List[str]]
        dictionary mapping well id to columns with problematic entries

    """
    problematic_well_ids = dataframe[
        ~dataframe[col].apply(
            lambda x: x == "Yes"
            or x == "No"
            or pd.isnull(x)
            or x == 1
            or x == 0
            or x == "1"
            or x == "0"
        )
    ][WELL_ID_COL_NAME].values
    for well_id in problematic_well_ids:
        update_problematic_entry_dictionary(problematic_well_info, well_id, col)


def coerce_columns_to_string(
    dataframe: pd.DataFrame, problematic_well_info: Dict[Union[str, int], List[str]]
) -> pd.DataFrame:
    """
    Coerces specific columns into string data types

    Parameters
    ----------
    dataframe : pd.DataFrame
        dataframe containing column to replace Boolean fields

    problematic_well_info : Dict[Union[str, int], List[str]]
        dictionary mapping well id to columns with problematic entries

    Returns
    -------
    pd.DataFrame
        the dataframe with strings as the column entries
    """
    for column in COLUMNS_TO_CONVERT_TO_STRINGS:
        if column in dataframe.columns:
            dataframe = create_string_column(dataframe, column, problematic_well_info)
    return dataframe


def validate_numeric_columns(
    dataframe: pd.DataFrame, problematic_well_info: Dict[Union[str, int], List[str]]
):
    """
    Validates numeric entries for the data set

    Parameters
    ----------
    dataframe : pd.DataFrame
        dataframe containing column to replace Boolean fields

    problematic_well_info : Dict[Union[str, int], List[str]]
        dictionary mapping well id to columns with problematic entries

    """
    for column in NUMERIC_COLUMN_NAMES:
        if column in dataframe.columns:
            check_column_numeric(dataframe, column, problematic_well_info)


def validate_string_columns(
    dataframe: pd.DataFrame, problematic_well_info: Dict[Union[str, int], List[str]]
):
    """
    Validates string entries for the data set
    Parameters
    ----------
    dataframe : pd.DataFrame
        dataframe containing column to replace Boolean fields

    """
    for column in STRING_COLUMN_NAMES:
        if column in dataframe.columns:
            check_column_string(dataframe, column, problematic_well_info)


def validate_boolean_columns(
    dataframe: pd.DataFrame, problematic_well_info: Dict[Union[str, int], List[str]]
):
    """
    Validates Boolean entries for the data set
    Parameters
    ----------
    dataframe : pd.DataFrame
        dataframe containing column to replace Boolean fields
    problematic_well_info : Dict[Union[str, int], List[str]]
        dictionary mapping well id to columns with problematic entries

    """
    for column in BOOLEAN_COLUMN_NAMES:
        if column in dataframe.columns:
            check_column_boolean(dataframe, column, problematic_well_info)


def validate_well_type(
    dataframe: pd.DataFrame, problematic_well_info: Dict[Union[str, int], List[str]]
):
    """
    Checks if all the entries of a the well type column
    are "Oil" or "Gas" or "Both"

    Parameters
    ----------
    dataframe : pd.DataFrame
        dataframe containing column to replace Boolean fields

    Returns
    -------
    bool
        true if the column values are numeric, false otherwise
    """
    problematic_well_ids = dataframe[
        ~dataframe["well_type"].apply(lambda x: x in ("Gas", "Oil", "Combined"))
    ][WELL_ID_COL_NAME].values
    for well_id in problematic_well_ids:
        update_problematic_entry_dictionary(problematic_well_info, well_id, "well_type")


def check_required_columns(
    dataframe: pd.DataFrame, problematic_well_info: Dict[Union[str, int], List[str]]
):
    """
    Checks if required columns are completely populated

    Parameters
    ----------
    dataframe : pd.DataFrame
        dataframe containing column to replace Boolean fields
    problematic_well_info : Dict[Union[str, int], List[str]]
        dictionary mapping well id to columns with problematic entries
    """
    for column_name in REQUIRED_COLUMNS:
        problematic_well_ids = dataframe[
            dataframe[column_name].apply(lambda x: pd.isna(x) or pd.isnull(x))
        ][WELL_ID_COL_NAME].values
        for well_id in problematic_well_ids:
            update_problematic_entry_dictionary(
                problematic_well_info, well_id, column_name
            )


def get_appropriate_column_instructions(
    set_columns_with_errors: Set[str], reverse_original_columns: Dict[str, str]
) -> str:
    """
    Creates a list of details for the columns that had errors

    Parameters
    ----------
    set_columns_with_errors : Set[str]
        set of column names that had problematic data
    reverse_original_columns : Dict[str, str]
        dictionary mapping the database key to the original column name in the spreadsheet

    Returns
    -------
    str
    """
    msg = ""
    for col in set_columns_with_errors:
        if col in BOOLEAN_COLUMN_NAMES:
            msg += (
                f"Entries in column '{reverse_original_columns[col]}' must"
                " be 'Yes' or 'No' or 0 or 1. "
            )
        if col in COLUMNS_TO_CONVERT_TO_STRINGS:
            msg += (
                f"Entries in column '{reverse_original_columns[col]}' "
                "cannot be converted to a string value. "
            )
        if col in NUMERIC_COLUMN_NAMES:
            msg += f"Entries in column '{reverse_original_columns[col]}' must be numeric values. "
        if col in STRING_COLUMN_NAMES and col != "well_type":
            msg += (
                f"Entries in column '{reverse_original_columns[col]}' must be strings. "
            )
        if col in REQUIRED_COLUMNS:
            msg += (
                f"Entries in column '{reverse_original_columns[col]}' "
                "are required; there may be missing entries. "
            )
        if col == "well_type":
            msg += (
                "Entries in column 'Well Type' must be 'Gas' or 'Oil' or 'Combined'. "
            )
    return msg


# pylint: disable=unused-argument
def handle_problematic_info(
    problematic_well_info: Dict[Union[str, int], List[str]],
    reverse_original_columns: Dict[str, str],
    dataframe: pd.DataFrame,
):
    """
    Handles the errors accumulated throughout the data check

    Parameters
    ----------
    problematic_well_info : Dict[Union[str, int], List[str]]
        dictionary mapping well id to columns with problematic entries
    reverse_original_columns : Dict[str, str]
        dictionary mapping the database key to the original column name in the spreadsheet
    dataframe : pd.DataFrame
        the data

    """
    if len(problematic_well_info) == 0:
        return

    detailed_error_msg = ""
    columns_with_errors = set()
    for well_id, problematic_columns in problematic_well_info.items():
        # keep track of columns to display messages for
        columns_with_errors.update(problematic_columns)
        detailed_error_msg += (
            f"(Well ID : {well_id}, "
            "Problematic Columns : "
            f"{[reverse_original_columns[col] for col in problematic_columns]}) "
        )
    detailed_error_msg += get_appropriate_column_instructions(
        columns_with_errors, reverse_original_columns
    )

    # dataframe_original_names = dataframe.rename(columns=reverse_original_columns)
    # original_columns = {value: key for key, value in reverse_original_columns.items()}

    # dataframe_styled = dataframe_original_names.style.apply(
    #     lambda row: [
    #         "background-color: yellow"
    #         if row[reverse_original_columns[WELL_ID_COL_NAME]] in problematic_well_info
    #         and original_columns[column_name]
    #         in problematic_well_info[row[reverse_original_columns[WELL_ID_COL_NAME]]]
    #         else "background_color: none"
    #         for column_name in row.index
    #     ],
    #     axis=1,
    # )
    # dataframe_styled.to_excel('/usr/src/app/highlight_test.xlsx', engine='openpyxl', index=False)

    raise HTTPException(
        status_code=fastapi.status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail=detailed_error_msg,
    )


def validate_data(file_path: str) -> pd.DataFrame:
    """
    Function that performs all of the required validation checks on the data
    and returns the data in a format ready to be sent to the mySQL
    database

    Parameters
    ----------
    file_path : str
        path of the upload file

    Returns
    -------
    pd.DataFrame
        dataframe ready to be inserted into database
    """
    # create the dataframe
    if ".xlsx" in file_path:
        data = pd.read_excel(file_path)
    elif ".csv" in file_path:
        data = pd.read_csv(file_path)
    else:
        raise HTTPException(
            status_code=fastapi.status.HTTP_404_NOT_FOUND,
            detail="Please input either a csv or xlsx file",
        )
    original_columns = {column_name: column_name for column_name in data.columns}
    # first we change all the column names
    data.rename(columns={i: convert_name(i) for i in data.columns}, inplace=True)

    original_columns.update({i: convert_name(i) for i in original_columns})

    # map the column names to the correct keys that the front end expects
    data.rename(columns=SNAKECASE_COLUMN_NAME_TO_DB_KEY, inplace=True)

    # original_columns.update(SNAKECASE_COLUMN_NAME_TO_DB_KEY)
    reverse_original_columns = {value: key for key, value in original_columns.items()}
    reverse_original_columns = {
        (
            SNAKECASE_COLUMN_NAME_TO_DB_KEY[key]
            if key in SNAKECASE_COLUMN_NAME_TO_DB_KEY
            else key
        ): value
        for key, value in reverse_original_columns.items()
    }

    LOGGER.info(f"reverse_original_columns : {reverse_original_columns}")
    # drop duplicate columns if they exist (e.g., PA demo data)
    # Identify duplicate columns
    data = data.loc[:, ~data.columns.duplicated()]

    data.index += 2
    # check for missing well ids
    missing_rows = data[WELL_ID_COL_NAME].apply(lambda x: pd.isna(x) or pd.isnull(x))
    missing_well_ids = data[missing_rows][WELL_ID_COL_NAME].values
    if len(missing_well_ids) > 0:
        raise HTTPException(
            status_code=fastapi.status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                "There are missing entries in the well ids column. "
                f"Please check rows {data.index[missing_rows].values}."
            ),
        )

    # ensure that all the well_ids are unique
    duplicate_well_ids = data[data[WELL_ID_COL_NAME].duplicated()][
        WELL_ID_COL_NAME
    ].values
    if len(duplicate_well_ids) > 0:
        raise HTTPException(
            status_code=fastapi.status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                f"The following well ids have duplicate entries {duplicate_well_ids}. "
                "All well ids must be unique. Please remove duplicates."
            ),
        )

    # get data for where the input data has problematic entries
    problematic_well_info = {}

    # coerce to strings
    data = coerce_columns_to_string(data, problematic_well_info)

    # modify the Boolean data
    data = replace_boolean_columns(data)

    # validate the numeric columns
    validate_numeric_columns(data, problematic_well_info)

    # validate the string columns
    validate_string_columns(data, problematic_well_info)

    # validate the Boolean columns
    validate_boolean_columns(data, problematic_well_info)

    # validate required columns
    check_required_columns(data, problematic_well_info)

    # validate the well type
    validate_well_type(data, problematic_well_info)

    handle_problematic_info(problematic_well_info, reverse_original_columns, data)

    return data
