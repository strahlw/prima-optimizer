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

# Standard libs
import logging
import pathlib

# Installed libs
import numpy as np
import pyomo.environ as pe
import pytest

# User-defined libs
from primo.data_parser import EfficiencyMetrics, ImpactMetrics, WellDataColumnNames
from primo.data_parser.well_data import WellData
from primo.opt_model.model_options import OptModelInputs
from primo.opt_model.model_with_clustering import (  # pylint: disable=no-name-in-module
    IndexedClusterBlock,
    PluggingCampaignModel,
)
from primo.opt_model.result_parser import Campaign, Project
from primo.utils.config_utils import (
    OverrideAddInfo,
    OverrideRemoveLockInfo,
    OverrideSelections,
)
from primo.utils.override_utils import OverrideCampaign

LOGGER = logging.getLogger(__name__)


# pylint: disable=duplicate-code


# pylint: disable=missing-function-docstring
@pytest.fixture(name="get_column_names", scope="function")
def get_column_names_fixture():
    """
    Pytest fixture to set up the impact metric, assign
    column names, and read the test data.
    """

    # Define impact metrics by creating an instance of ImpactMetrics class
    im_metrics = ImpactMetrics()

    # Specify weights
    im_metrics.set_weight(
        primary_metrics={
            "well_history": 35,
            "sensitive_receptors": 20,
            "ann_production_volume": 20,
            "well_age": 15,
            "well_count": 10,
        },
        submetrics={
            "well_history": {
                "leak": 40,
                "compliance": 30,
                "violation": 20,
                "incident": 10,
            },
            "sensitive_receptors": {
                "schools": 50,
                "hospitals": 50,
            },
            "ann_production_volume": {
                "ann_gas_production": 50,
                "ann_oil_production": 50,
            },
        },
    )

    eff_metrics = EfficiencyMetrics()

    # Set weights for the metrics
    eff_metrics.set_weight(
        primary_metrics={
            "num_wells": 10,
            "elevation_delta": 20,
            "age_range": 10,
            "depth_range": 20,
            "dist_range": 20,
            "dist_to_road": 15,
            "population_density": 0,
            "record_completeness": 0,
            "num_unique_owners": 5,
        }
    )

    # Construct an object to store column names
    col_names = WellDataColumnNames(
        well_id="API Well Number",
        latitude="x",
        longitude="y",
        operator_name="Operator Name",
        age="Age [Years]",
        depth="Depth [ft]",
        leak="Leak [Yes/No]",
        compliance="Compliance [Yes/No]",
        violation="Violation [Yes/No]",
        incident="Incident [Yes/No]",
        hospitals="Number of Nearby Hospitals",
        schools="Number of Nearby Schools",
        ann_gas_production="Gas [Mcf/Year]",
        ann_oil_production="Oil [bbl/Year]",
        # These are user-specific columns
        elevation_delta="Elevation Delta [m]",
        dist_to_road="Distance to Road [miles]",
    )

    current_file = pathlib.Path(__file__).resolve()
    # primo folder is 2 levels up the current folder
    data_file = str(current_file.parents[2].joinpath("demo", "Example_1_data.csv"))
    return eff_metrics, im_metrics, col_names, data_file


@pytest.mark.parametrize(
    "cluster_method, num_projects",
    [
        ("Louvain", [4, 5, 6, 7]),
        ("Agglomerative", [4, 5, 6]),
    ],
)
def test_opt_model_inputs(get_column_names, cluster_method, num_projects):
    """
    Test that the optimization model is constructed and solved correctly.
    """
    # pylint: disable=too-many-locals
    # pylint: disable=too-many-statements

    eff_metrics, im_metrics, col_names, filename = get_column_names

    # Create the well data object
    wd = WellData(
        data=filename,
        column_names=col_names,
        impact_metrics=im_metrics,
        efficiency_metrics=eff_metrics,
    )

    # Partition the wells as gas/oil
    gas_oil_wells = wd.get_gas_oil_wells
    wd_gas = gas_oil_wells["gas"]

    # Mobilization cost
    mobilization_cost = {1: 120000, 2: 210000, 3: 280000, 4: 350000}
    for n_wells in range(5, len(wd_gas) + 1):
        mobilization_cost[n_wells] = n_wells * 84000

    # Catch inputs missing error
    with pytest.raises(
        ValueError,
        match=(
            "One or more essential input arguments in \\[well_data, total_budget, "
            "mobilization_cost\\] are missing while instantiating the object. "
            "WellData object containing information on all wells, the total budget, "
            "and the mobilization cost are essential inputs for the optimization model. "
        ),
    ):
        opt_mdl_inputs = OptModelInputs()

    # Catch priority score missing error
    with pytest.raises(
        ValueError,
        match=(
            "Unable to find priority scores in the WellData object. Compute the scores "
            "using the compute_priority_scores method."
        ),
    ):
        opt_mdl_inputs = OptModelInputs(
            well_data=wd_gas,
            total_budget=3250000,  # 3.25 million USD
            mobilization_cost=mobilization_cost,
        )

    # Compute priority scores
    # Test the model and options
    wd_gas.compute_priority_scores()

    assert "Clusters" not in wd_gas

    # Formulate the optimization problem
    opt_mdl_inputs = OptModelInputs(
        well_data=wd_gas,
        total_budget=1500000,  # 1.5 million USD
        mobilization_cost=mobilization_cost,
        threshold_distance=10,
        cluster_method=cluster_method,
        objective_weight_impact=50,
        max_wells_in_project=5,
    )

    # Ensure that clustering is performed internally
    assert "Clusters" in wd_gas

    opt_mdl_inputs.build_optimization_model()
    opt_campaign = opt_mdl_inputs.solve_model(solver="highs", mip_gap=50e-2)
    opt_mdl = opt_mdl_inputs.optimization_model

    assert hasattr(opt_mdl_inputs, "config")
    assert "Clusters" in wd_gas  # Column is added after clustering
    assert hasattr(opt_mdl_inputs, "campaign_candidates")
    assert hasattr(opt_mdl_inputs, "owner_well_count")

    assert opt_mdl_inputs.get_max_cost_project is None
    assert opt_mdl_inputs.get_total_budget == 1.5

    scaled_mobilization_cost = {1: 0.12, 2: 0.21, 3: 0.28, 4: 0.35}
    for n_wells in range(5, len(wd_gas.data) + 1):
        scaled_mobilization_cost[n_wells] = n_wells * 0.084

    get_mobilization_cost = opt_mdl_inputs.get_mobilization_cost
    for well, cost in scaled_mobilization_cost.items():
        assert np.isclose(get_mobilization_cost[well], cost)

    assert isinstance(opt_mdl, PluggingCampaignModel)
    assert isinstance(opt_campaign, Campaign)
    project_keys = list(opt_campaign.projects.keys())
    example_key = project_keys[0]  # Pick the first available key
    assert isinstance(opt_campaign.projects[example_key], Project)

    # TODO: Confirm degeneracy
    assert len(opt_campaign.projects) in num_projects

    # Test the structure of the optimization model
    num_clusters = len(set(wd_gas["Clusters"]))
    assert hasattr(opt_mdl, "cluster")
    assert len(opt_mdl.cluster) == num_clusters
    assert isinstance(opt_mdl.cluster, IndexedClusterBlock)
    assert not hasattr(opt_mdl, "max_well_owner_constraint")
    assert hasattr(opt_mdl, "total_priority_score")

    # Check if the scaling factor for unused budget variable is correctly built
    # pylint: disable=protected-access
    _, _, budget_sufficient = opt_mdl._slack_variable_scaling()
    assert not budget_sufficient

    # Check if all the cluster sets are defined
    assert hasattr(opt_mdl.cluster[1], "set_wells")
    assert hasattr(opt_mdl.cluster[1].efficiency_model.num_unique_owners, "set_owners")

    # Check if all the required variables are defined
    assert not opt_mdl.cluster[1].select_cluster.is_indexed()
    assert opt_mdl.cluster[1].select_cluster.is_binary()
    assert opt_mdl.cluster[1].select_well.is_indexed()
    for j in opt_mdl.cluster[1].select_well:
        assert opt_mdl.cluster[1].select_well[j].domain == pe.Binary
    assert opt_mdl.cluster[1].num_wells_var.is_indexed()
    for j in opt_mdl.cluster[1].num_wells_var:
        assert opt_mdl.cluster[1].num_wells_var[j].domain == pe.Binary
    assert not opt_mdl.cluster[1].plugging_cost.is_indexed()
    assert opt_mdl.cluster[1].plugging_cost.domain == pe.NonNegativeReals
    assert opt_mdl.cluster[1].num_wells_chosen.domain == pe.NonNegativeReals
    assert (
        opt_mdl.cluster[1]
        .efficiency_model.num_unique_owners.select_owner["Owner 243"]
        .domain
        == pe.Binary
    )
    assert (
        opt_mdl.cluster[1].efficiency_model.num_unique_owners.num_owners_chosen.domain
        == pe.NonNegativeReals
    )
    # pylint: disable=no-member
    assert opt_mdl.unused_budget.domain == pe.NonNegativeReals

    # Check if the required expressions are defined
    assert hasattr(opt_mdl.cluster[1], "cluster_impact_score")

    # Check if the required constraints are defined
    assert hasattr(opt_mdl.cluster[1], "calculate_num_wells_chosen")
    assert hasattr(opt_mdl.cluster[1], "calculate_plugging_cost")
    assert hasattr(opt_mdl.cluster[1], "campaign_length")
    assert hasattr(opt_mdl.cluster[1], "num_well_uniqueness")
    assert not hasattr(opt_mdl.cluster[1], "ordering_num_wells_vars")
    assert hasattr(opt_mdl.cluster[1], "skip_distant_well_cuts")
    assert hasattr(
        opt_mdl.cluster[1].efficiency_model.num_unique_owners, "num_owners_constraint"
    )
    assert hasattr(
        opt_mdl.cluster[1].efficiency_model.num_unique_owners, "do_not_select_owner"
    )
    assert hasattr(
        opt_mdl.cluster[1].efficiency_model.num_unique_owners, "num_owners_constraint"
    )

    # check unique owners constraints
    assert str(
        opt_mdl.cluster[1].efficiency_model.num_unique_owners.calculate_score.expr
    ) == (
        "cluster[1].efficiency_model.num_unique_owners.score  <=  "
        "5*(cluster[1].select_cluster - "
        "(cluster[1].efficiency_model.num_unique_owners.num_owners_chosen "
        "- cluster[1].select_cluster)/4)"
    )

    # identify selected projects
    project_index = []
    for i in range(num_clusters):
        if (
            sum(
                opt_mdl.cluster[i].select_well[j].value
                for j in opt_mdl.cluster[i].set_wells
            )
            > 0
        ):
            project_index.append(i)
    # compute efficiency scores
    opt_campaign.efficiency_calculator.efficiency_model_scores = {}

    # compare efficiency scores from model and campaign class
    for project_id in project_index:
        eff_scores_model = opt_mdl.cluster[
            project_id
        ].efficiency_model.get_efficiency_scores()
        eff_scores_calculated = opt_campaign.projects[
            project_id
        ].get_efficiency_metric_scores()

        # assert individual efficiency scores for each metric
        for metric in eff_scores_model:
            assert np.isclose(eff_scores_model[metric], eff_scores_calculated[metric])

        for metric in eff_scores_calculated:
            assert np.isclose(eff_scores_model[metric], eff_scores_calculated[metric])


def test_opt_model_with_overlapping_clustering(get_column_names):
    """
    Test that the optimization model for smaller datasets is constructed and solved correctly.
    """
    # pylint: disable=too-many-locals
    # pylint: disable=too-many-statements

    eff_metrics, im_metrics, col_names, filename = get_column_names

    # Create the well data object
    wd = WellData(
        data=filename,
        column_names=col_names,
        impact_metrics=im_metrics,
        efficiency_metrics=eff_metrics,
    )

    # Partition the wells as gas/oil
    gas_oil_wells = wd.get_gas_oil_wells
    wd_gas = gas_oil_wells["gas"]

    # Mobilization cost
    mobilization_cost = {1: 120000, 2: 210000, 3: 280000, 4: 350000}
    for n_wells in range(5, len(wd_gas) + 1):
        mobilization_cost[n_wells] = n_wells * 84000

    # Catch inputs missing error
    with pytest.raises(
        ValueError,
        match=(
            "One or more essential input arguments in \\[well_data, total_budget, "
            "mobilization_cost\\] are missing while instantiating the object. "
            "WellData object containing information on all wells, the total budget, "
            "and the mobilization cost are essential inputs for the optimization model. "
        ),
    ):
        opt_mdl_inputs = OptModelInputs()

    # Catch priority score missing error
    with pytest.raises(
        ValueError,
        match=(
            "Unable to find priority scores in the WellData object. Compute the scores "
            "using the compute_priority_scores method."
        ),
    ):
        opt_mdl_inputs = OptModelInputs(
            well_data=wd_gas,
            total_budget=32500000,  # 32.5 million USD
            mobilization_cost=mobilization_cost,
        )

    # Compute priority scores
    # Test the model and options
    wd_gas.compute_priority_scores()
    wd_gas = wd_gas.get_high_priority_wells(num_wells=20)

    assert "Clusters" not in wd_gas

    # Formulate the optimization problem
    opt_mdl_inputs = OptModelInputs(
        well_data=wd_gas,
        total_budget=32500000,  # 32.5 million USD
        mobilization_cost=mobilization_cost,
        threshold_distance=2,
        cluster_method="Exhaustive",
        objective_weight_impact=50,
    )

    print(mobilization_cost)

    assert opt_mdl_inputs.check_sufficient_budget
    assert len(opt_mdl_inputs.campaign_candidates) == 20

    opt_mdl_inputs.build_optimization_model()
    opt_campaign = opt_mdl_inputs.solve_model(solver="highs", mip_gap=5e-2)
    opt_mdl = opt_mdl_inputs.optimization_model

    assert hasattr(opt_mdl_inputs, "config")
    assert hasattr(opt_mdl_inputs, "campaign_candidates")

    assert opt_mdl_inputs.get_total_budget == 32.5

    scaled_mobilization_cost = {1: 0.12, 2: 0.21, 3: 0.28, 4: 0.35}
    for n_wells in range(5, len(wd_gas.data) + 1):
        scaled_mobilization_cost[n_wells] = n_wells * 0.084

    get_mobilization_cost = opt_mdl_inputs.get_mobilization_cost
    for well, cost in scaled_mobilization_cost.items():
        assert np.isclose(get_mobilization_cost[well], cost)

    assert isinstance(opt_mdl, PluggingCampaignModel)
    assert isinstance(opt_campaign, Campaign)
    project_keys = list(opt_campaign.projects.keys())
    example_key = project_keys[0]  # Pick the first available key
    assert isinstance(opt_campaign.projects[example_key], Project)

    # TODO: Confirm degeneracy
    assert len(opt_campaign.projects) in [14]

    # Test the structure of the optimization model
    assert not hasattr(opt_mdl, "max_well_owner_constraint")
    assert hasattr(opt_mdl, "total_priority_score")
    assert hasattr(opt_mdl, "well_selection_constraint")
    assert hasattr(opt_mdl, "anchor_well_constraint")
    assert hasattr(opt_mdl, "well_selected")
    assert hasattr(opt_mdl, "set_wells")

    # Test override recalculation

    assert "Clusters" in wd_gas
    override_selections = OverrideSelections(
        remove_widget_return=OverrideRemoveLockInfo(cluster=[], well={860: [864]}),
        add_widget_return=OverrideAddInfo(
            existing_clusters={860: [864]}, new_clusters={67: [864]}
        ),
        lock_widget_return=OverrideRemoveLockInfo(cluster=[858], well={858: [858]}),
    )

    campaign = OverrideCampaign(
        override_selections=override_selections,
        opt_inputs=opt_mdl_inputs,
        opt_campaign=opt_campaign.clusters_dict,
        eff_metrics=eff_metrics,
    )

    assert not campaign.feasibility.assess_feasibility()
    assert 864 in campaign.new_campaign[67]
    assert 864 not in campaign.new_campaign[860]

    violation_info_dict = campaign.violation_info
    assert len(violation_info_dict) == 2
    assert violation_info_dict["Project Status:"] == "CONSTRAINT(S) VIOLATED"
    key_list = list(violation_info_dict.keys())
    violated_operators = violation_info_dict[key_list[1]].head(1)
    assert violated_operators["Project"].loc[violated_operators.index[0]] == 67
    assert violated_operators["Well 1"].loc[violated_operators.index[0]] == "50038"
    assert violated_operators["Well 2"].loc[violated_operators.index[0]] == "26239"
    assert np.isclose(
        violated_operators["Distance between Well 1 and 2 [Miles]"].loc[
            violated_operators.index[0]
        ],
        119.00012515262621,
    )


def test_opt_model_with_sufficient_budget_edge_case(get_column_names, caplog):
    """
    Test that the optimization model for smaller datasets is constructed and solved correctly.
    """
    # pylint: disable=too-many-locals
    # pylint: disable=too-many-statements

    eff_metrics, im_metrics, col_names, filename = get_column_names

    # Create the well data object
    wd = WellData(
        data=filename,
        column_names=col_names,
        impact_metrics=im_metrics,
        efficiency_metrics=eff_metrics,
    )

    # Partition the wells as gas/oil
    gas_oil_wells = wd.get_gas_oil_wells
    wd_gas = gas_oil_wells["gas"]

    # Mobilization cost
    mobilization_cost = {1: 120000, 2: 210000, 3: 280000, 4: 350000}
    for n_wells in range(5, len(wd_gas) + 1):
        mobilization_cost[n_wells] = n_wells * 84000

    # Test the model and options
    wd_gas.compute_priority_scores()
    wd_gas = wd_gas.get_high_priority_wells(num_wells=20)

    assert "Clusters" not in wd_gas

    # NOTE: Budget set to 2 million, which is between the bounds
    # False positive case
    # Formulate the optimization problem
    opt_mdl_inputs = OptModelInputs(
        well_data=wd_gas,
        total_budget=2000000,
        mobilization_cost=mobilization_cost,
        threshold_distance=2,
        cluster_method="Exhaustive",
        objective_weight_impact=50,
    )

    print(mobilization_cost)

    assert opt_mdl_inputs.check_sufficient_budget
    assert len(opt_mdl_inputs.campaign_candidates) == 20

    opt_mdl_inputs.build_optimization_model()
    opt_campaign = opt_mdl_inputs.solve_model(solver="highs", mip_gap=5e-2)
    opt_mdl = opt_mdl_inputs.optimization_model

    assert hasattr(opt_mdl_inputs, "config")
    assert hasattr(opt_mdl_inputs, "campaign_candidates")

    assert opt_mdl_inputs.get_total_budget == 2

    scaled_mobilization_cost = {1: 0.12, 2: 0.21, 3: 0.28, 4: 0.35}
    for n_wells in range(5, len(wd_gas.data) + 1):
        scaled_mobilization_cost[n_wells] = n_wells * 0.084

    get_mobilization_cost = opt_mdl_inputs.get_mobilization_cost
    for well, cost in scaled_mobilization_cost.items():
        assert np.isclose(get_mobilization_cost[well], cost)

    assert isinstance(opt_mdl, PluggingCampaignModel)
    assert isinstance(opt_campaign, Campaign)
    project_keys = list(opt_campaign.projects.keys())
    example_key = project_keys[0]  # Pick the first available key
    assert isinstance(opt_campaign.projects[example_key], Project)

    # TODO: Confirm degeneracy
    assert len(opt_campaign.projects) == 12

    # Test the structure of the optimization model
    assert not hasattr(opt_mdl, "max_well_owner_constraint")
    assert hasattr(opt_mdl, "total_priority_score")
    assert hasattr(opt_mdl, "well_selection_constraint")
    assert hasattr(opt_mdl, "anchor_well_constraint")
    assert hasattr(opt_mdl, "well_selected")
    assert hasattr(opt_mdl, "set_wells")
    assert "Clusters" in wd_gas

    # confirm logger warning message in output
    expected_msg = (
        "The sufficient budget check returned True but some wells in the dataset "
        "are not selected in projects."
    )
    assert any(expected_msg in message for message in caplog.messages)
