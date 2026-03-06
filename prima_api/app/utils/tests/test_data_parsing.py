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
# pylint: disable=missing-function-docstring

# Installed libs
import pandas as pd

# User-defined libs
from utils.data_parsing import (
    check_column_boolean,
    check_column_numeric,
    check_column_string,
    check_required_columns,
    replace_boolean_fields,
    validate_well_type,
)


def test_replace_boolean_fields():

    # Boolean field test - check none
    values = [
        "Yes",
        "yes",
        "Y",
        "y",
        "No",
        "no",
        "N",
        "n",
        "true",
        "TRUE",
        "True",
        "false",
        "False",
        "FALSE",
        1,
        0,
        1,
        "dummy",
        None,
        "dummy2",
    ]

    data = pd.DataFrame(values, columns=["Test"])
    replaced_fields = replace_boolean_fields(data, "Test")
    data_to_db = replaced_fields.to_dict(orient="records")
    values = [item[key] for item in data_to_db for key in item]
    assert all(
        (
            values[i] == [1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 1, 0, 1, "dummy"][i]
            for i in range(len(replaced_fields.values) - 2)
        )
    )
    assert values[-2] is None
    assert values[-1] == "dummy2"


def test_check_column_numeric_tests():
    # check column numeric tests
    values = [None, 1, 0, 1]
    well_ids = [1, 2, 3, 4]
    problematic_well_info = {}
    data = pd.DataFrame({"Test": values, "well_id": well_ids})
    check_column_numeric(data, "Test", problematic_well_info)
    assert len(problematic_well_info) == 0

    # check column numeric tests
    data.iloc[0, 0] = "string"
    check_column_numeric(data, "Test", problematic_well_info)
    assert len(problematic_well_info) == 1
    assert problematic_well_info == {1: ["Test"]}


def test_check_column_string_tests():
    # check column string tests
    values = ["", "1", "0", "1"]
    well_ids = [1, 2, 3, 4]
    problematic_well_info = {}
    data = pd.DataFrame({"Test": values, "well_id": well_ids})
    check_column_string(data, "Test", problematic_well_info)
    assert len(problematic_well_info) == 0

    # check column string tests
    values = ["", "", "", None]
    well_ids = [1, 2, 3, 4]
    problematic_well_info = {}
    data = pd.DataFrame({"Test": values, "well_id": well_ids})
    check_column_string(data, "Test", problematic_well_info)
    assert len(problematic_well_info) == 0

    # check column string tests
    values = ["string", 1, "string2", 1]
    well_ids = [1, 2, 3, 4]
    problematic_well_info = {}
    data = pd.DataFrame({"Test": values, "well_id": well_ids})
    check_column_string(data, "Test", problematic_well_info)
    assert len(problematic_well_info) == 2
    assert problematic_well_info == {2: ["Test"], 4: ["Test"]}


def test_check_column_boolean():
    # check column Boolean tests
    values = ["No", "Yes", "Yes", "No"]
    well_ids = [1, 2, 3, 4]
    problematic_well_info = {}
    data = pd.DataFrame({"Test": values, "well_id": well_ids})
    check_column_boolean(data, "Test", problematic_well_info)
    assert len(problematic_well_info) == 0

    # check column Boolean tests
    values = [None, "Yes", "Yes", "No"]
    well_ids = [1, 2, 3, 4]
    problematic_well_info = {}
    data = pd.DataFrame({"Test": values, "well_id": well_ids})
    check_column_boolean(data, "Test", problematic_well_info)
    assert len(problematic_well_info) == 0

    # check column Boolean tests
    values = ["No", "Yes1", "Yes", "No"]
    well_ids = [1, 2, 3, 4]
    problematic_well_info = {}
    data = pd.DataFrame({"Test": values, "well_id": well_ids})
    check_column_boolean(data, "Test", problematic_well_info)
    assert problematic_well_info == {2: ["Test"]}


def test_validate_well_type():
    # check column well_type tests
    values = ["Oil", "Gas", "Both", "Oil"]
    data = pd.DataFrame(values, columns=["well_type"])
    well_ids = [1, 2, 3, 4]
    problematic_well_info = {}
    data = pd.DataFrame({"well_type": values, "well_id": well_ids})
    validate_well_type(data, problematic_well_info)
    assert problematic_well_info == {3: ["well_type"]}

    # check column well_type well_types
    values = ["Oil", "Gas", "Both", "Oil", None]
    data = pd.DataFrame(values, columns=["well_type"])
    well_ids = [1, 2, 3, 4, 5]
    problematic_well_info = {}
    data = pd.DataFrame({"well_type": values, "well_id": well_ids})
    validate_well_type(data, problematic_well_info)
    assert problematic_well_info == {3: ["well_type"], 5: ["well_type"]}

    # check column well_type well_types
    values = ["Oil", "Gas", "Both", "Oil5"]
    data = pd.DataFrame(values, columns=["well_type"])
    well_ids = [1, 2, 3, 4]
    problematic_well_info = {}
    data = pd.DataFrame({"well_type": values, "well_id": well_ids})
    validate_well_type(data, problematic_well_info)
    assert problematic_well_info == {3: ["well_type"], 4: ["well_type"]}

    values = ["Oil", "Gas", "Combined", "Oil"]
    data = pd.DataFrame(values, columns=["well_type"])
    well_ids = [1, 2, 3, 4]
    problematic_well_info = {}
    data = pd.DataFrame({"well_type": values, "well_id": well_ids})
    validate_well_type(data, problematic_well_info)
    assert len(problematic_well_info) == 0


def test_check_required_columns():
    # check required_columns tests
    # note this assumes that the type has been checked already
    values1 = ["Oil", "Gas", "Both", "Oil"]
    values2 = [1, 2, 3, 4]
    values3 = [0.0, 0.0, 0.0, 0.0]
    values4 = [0.0, 0.0, 0.0, 0.0]
    problematic_well_info = {}
    data = pd.DataFrame(
        {
            "well_type": values1,
            "well_id": values2,
            "latitude": values3,
            "longitude": values4,
        }
    )
    check_required_columns(data, problematic_well_info)
    assert len(problematic_well_info) == 0

    # check required_columns tests
    # note this assumes that the type has been checked already
    values1 = ["Oil", "Gas", "Both", None]
    values2 = [1, 2, 3, 4]
    values3 = [0.0, 0.0, 0.0, None]
    values4 = [0.0, 0.0, 0.0, 0.0]
    problematic_well_info = {}
    data = pd.DataFrame(
        {
            "well_type": values1,
            "well_id": values2,
            "latitude": values3,
            "longitude": values4,
        }
    )
    check_required_columns(data, problematic_well_info)
    assert len(problematic_well_info) == 1
    assert problematic_well_info == {4: ["latitude"]}
