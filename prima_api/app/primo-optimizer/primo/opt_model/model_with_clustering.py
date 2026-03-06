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
from typing import Dict, Optional

# Installed libs
import numpy as np
from pyomo.core.base.block import BlockData, declare_custom_block
from pyomo.environ import (
    Binary,
    ConcreteModel,
    Constraint,
    Expression,
    NonNegativeReals,
    Objective,
    Param,
    Set,
    Var,
    maximize,
)

# User-defined libs
# pylint: disable=no-name-in-module, import-error
from primo.opt_model.efficiency_block import EfficiencyBlock
from primo.opt_model.result_parser import Campaign
from primo.utils.override_utils import distance_reassigned_well

LOGGER = logging.getLogger(__name__)


def build_cluster_model(model_block, cluster, override_data=None):
    """
    Builds the model block (adds essential variables and constraints)
    for a given cluster `cluster`
    """
    # Parameters are located in the parent block
    params = model_block.parent_block().model_inputs
    wd = params.config.well_data
    well_index = params.campaign_candidates[cluster]

    # Essential model sets
    model_block.set_wells = Set(
        initialize=well_index,
        doc="Set of wells in cluster c",
    )
    model_block.set_well_pairs_remove = Set(
        initialize=[],
        doc="Well-pairs which cannot be a part of the project",
    )
    model_block.set_well_pairs_keep = Set(
        initialize=[],
        doc="Well-pairs which can be a part of the project",
    )

    # Essential variables
    model_block.select_cluster = Var(
        within=Binary,
        doc="1, if wells from the cluster are chosen for plugging, 0 Otherwise",
    )
    model_block.select_well = Var(
        model_block.set_wells,
        within=Binary,
        doc="1, if the well is selected for plugging, 0 otherwise",
    )
    model_block.num_wells_var = Var(
        range(1, len(model_block.set_wells) + 1),
        within=Binary,
        doc="Variables to track the total number of wells chosen",
    )

    def num_wells_efficiency_embedding(i, b):
        """
        Computes coefficients for efficiency score in the objective function

        Parameters
        ----------
        i : int
            The number of wells in a project
        b : float
            A parameter that adjusts the coefficient based on the number of wells

        Returns
        -------
        float
            The coefficient for efficiency score in the objective. Returns 1 if b is zero.
        """
        if abs(b) <= 1e-6:
            return 1
        return np.log10(b * i) + 1

    model_block.num_wells_adjustment = Param(
        range(1, len(model_block.set_wells) + 1),
        initialize=lambda i: num_wells_efficiency_embedding(
            i, params.config.embedding_b
        ),
    )

    model_block.plugging_cost = Var(
        within=NonNegativeReals,
        doc="Total cost for plugging wells in this cluster",
    )

    # Although the following two variables are of type Integer, they
    # can be declared as continuous. The optimal solution is guaranteed to have
    # integer values.
    model_block.num_wells_chosen = Var(
        within=NonNegativeReals,
        doc="Total number of wells chosen in the project",
    )

    model_block.min_well_violation = Var(
        within=NonNegativeReals,
        initialize=0,
        doc="Amount by which the number of wells falls short of the minimum required per project",
    )

    model_block.max_well_violation = Var(
        within=NonNegativeReals,
        initialize=0,
        doc="Amount by which the number of wells exceeds the maximum allowed per project",
    )

    model_block.is_distant_pair = Var(
        model_block.set_well_pairs_remove,
        within=Binary,
        doc="1 if both wells are selected and exceed distance threshold",
    )

    # Set the maximum cost for a project: default is None.
    model_block.plugging_cost.setub(params.get_max_cost_project)

    # Set the minimum and maximum number of wells allowed for a project
    # Defaults are none
    if params.config.min_wells_in_project is not None:
        model_block.min_project_size = Constraint(
            expr=model_block.select_cluster * params.config.min_wells_in_project
            <= model_block.num_wells_chosen + model_block.min_well_violation
        )
        if override_data is None or override_data.override_status is False:
            model_block.min_well_violation.fix(0)

    if params.config.max_wells_in_project is not None:
        model_block.max_project_size = Constraint(
            expr=model_block.num_wells_chosen
            <= params.config.max_wells_in_project + model_block.max_well_violation
        )
        if override_data is None or override_data.override_status is False:
            model_block.max_well_violation.fix(0)

    # Useful expressions
    # Scale the priority score so that the maximum priority score is 100
    # Keep the lowest priority score at whatever (scaled) nominal value it is
    priority_score = (
        wd["Priority Score [0-100]"] * 100 / wd["Priority Score [0-100]"].max()
    )
    wt_impact = params.config.objective_weight_impact / 100
    model_block.cluster_impact_score = Expression(
        expr=(
            wt_impact
            * sum(
                priority_score[w] * model_block.select_well[w]
                for w in model_block.set_wells
            )
        ),
        doc="Computes the total priority score for the cluster",
    )

    # Essential constraints
    model_block.calculate_num_wells_chosen = Constraint(
        expr=(
            sum(model_block.select_well[w] for w in model_block.set_wells)
            == model_block.num_wells_chosen
        ),
        doc="Calculate the total number of wells chosen",
    )
    # This is to test which formulation is faster. If there is no
    # benefit in terms of computational time, then delete this method.
    if params.config.num_wells_model_type == "incremental":
        num_wells_incremental_formulation(model_block)
        return

    # Using the multicommodity formulation
    mob_cost = params.get_mobilization_cost
    model_block.calculate_plugging_cost = Constraint(
        expr=(
            sum(
                mob_cost[i] * model_block.num_wells_var[i]
                for i in model_block.num_wells_var
            )
            == model_block.plugging_cost
        ),
        doc="Calculates the total plugging cost for the cluster",
    )
    model_block.campaign_length = Constraint(
        expr=(
            sum(i * model_block.num_wells_var[i] for i in model_block.num_wells_var)
            == model_block.num_wells_chosen
        ),
        doc="Determines the number of wells chosen",
    )
    model_block.num_well_uniqueness = Constraint(
        expr=(
            sum(model_block.num_wells_var[i] for i in model_block.num_wells_var)
            == model_block.select_cluster
        ),
        doc="Ensures at most one num_wells_var is selected",
    )


def num_wells_incremental_formulation(model_block):
    """
    Models the number of wells constraint using the incremental cost
    formulation.
    """
    mob_cost = model_block.parent_block().model_inputs.get_mobilization_cost
    model_block.calculate_plugging_cost = Constraint(
        expr=(
            mob_cost[1] * model_block.num_wells_var[1]
            + sum(
                (mob_cost[i] - mob_cost[i - 1]) * model_block.num_wells_var[i]
                for i in model_block.num_wells_var
                if i != 1
            )
            == model_block.plugging_cost
        ),
        doc="Calculates the total plugging cost for the cluster",
    )
    model_block.campaign_length = Constraint(
        expr=(
            sum(model_block.num_wells_var[i] for i in model_block.num_wells_var)
            == model_block.num_wells_chosen
        ),
        doc="Computes the number of wells chosen",
    )

    @model_block.Constraint(
        model_block.num_wells_var.index_set(),
        doc="Ordering num_wells_var variables",
    )
    def ordering_num_wells_vars(model_block, well_idx):
        if well_idx == 1:
            return model_block.num_wells_var[well_idx] == model_block.select_cluster

        return (
            model_block.num_wells_var[well_idx]
            <= model_block.num_wells_var[well_idx - 1]
        )


def make_cluster_model_rule(override_data):
    """
    Returns a rule function for building cluster model blocks with override data

    Parameters
    ----------
    override_data : ReOptimizationData
            A ReOptimizationData object containing the necessary information
            related to the re-optimization of override

    Returns
    -------
    function
        A Pyomo-compatible rule function
    """

    def cluster_model_rule(model_block, cluster):
        return build_cluster_model(model_block, cluster, override_data=override_data)

    return cluster_model_rule


@declare_custom_block("ClusterBlock")
class ClusterBlockData(BlockData):
    """
    A custom block class for storing variables and constraints
    belonging to a cluster.
    Essential variables and constraints will be added via "rule"
    argument. Here, define methods only for optional cluster-level
    constraints and expressions.
    """

    def deactivate(self):
        """
        Deactivates the constraints present in this block.
        The variables will not be passed to the solver, unless
        they are used in other active constraints.
        """
        super().deactivate()
        self.select_cluster.fix(0)
        self.plugging_cost.fix(0)
        self.num_wells_chosen.fix(0)

    def activate(self):
        super().activate()
        self.select_cluster.unfix()
        self.plugging_cost.unfix()
        self.num_wells_chosen.unfix()

    def fix(
        self,
        cluster: Optional[int] = None,
        wells: Optional[Dict[int, int]] = None,
    ):
        """
        Fixes the binary variables associated with the cluster
        and/or the wells with in the cluster. To fix all variables
        within the cluster, use the fix_all_vars() method.

        Parameters
        ----------
        cluster : 0 or 1, default = None
            `select_cluster` variable will be fixed to this value.
            If None, select_cluster will be fixed to its incumbent value.

        wells : dict, default = None
            key => index of the well, value => value of `select_well`
            binary variable.
        """

        if cluster in [0, 1]:
            self.select_cluster.fix(cluster)

        if wells is not None:
            for w in self.set_wells:
                if w in wells:
                    self.select_well[w].fix(wells[w])

    def unfix(self):
        """
        Unfixes all the variables within the cluster.
        """
        self.unfix_all_vars()

    def add_distant_well_cuts(self):
        """
        Delete well pairs which are farther than the threshold distance
        """

        @self.Constraint(
            self.set_well_pairs_remove,
            doc="Removes well pairs which are far apart",
        )
        def skip_distant_well_cuts(b, w1, w2):
            return (
                b.select_well[w1] + b.select_well[w2]
                <= b.select_cluster + b.is_distant_pair[w1, w2]
            )


# pylint: disable-next = too-many-ancestors, too-many-instance-attributes
class PluggingCampaignModel(ConcreteModel):
    """
    Builds the optimization model
    """

    def __init__(self, model_inputs, *args, override_data=None, **kwargs):
        # pylint: disable=too-many-branches
        """
        Builds the optimization model for identifying the set of projects that
        maximize the overall impact and/or efficiency of plugging.

        Parameters
        ----------
        model_inputs : OptModelInputs
            Object containing the necessary inputs for the optimization model

        override_data : ReOptimizationData
            A ReOptimizationData object containing the necessary information
            related to the re-optimization of override
        """
        super().__init__(*args, **kwargs)

        self.model_inputs = model_inputs
        self.set_clusters = Set(
            initialize=list(model_inputs.campaign_candidates.keys())
        )

        # Define only those parameters which are useful for sensitivity analysis
        self.total_budget = Param(
            initialize=model_inputs.get_total_budget,
            mutable=True,
            doc="Total budget available [Million USD]",
        )

        self.unused_budget_scaling = Param(
            initialize=0,
            mutable=True,
            within=NonNegativeReals,
            doc="Unused budget variable scaling factor in the objective function",
        )

        # Define variables and parameters related to override re-optimization
        self.unused_budget = Var(
            within=NonNegativeReals,
            doc="The unutilized amount of total budget",
        )

        self.excess_budget = Var(
            within=NonNegativeReals,
            doc="Amount by which plugging costs exceed the total available budget",
        )

        self.excess_owc = Var(
            list(self.model_inputs.owner_well_count.keys()),
            within=NonNegativeReals,
            doc="Number of wells exceeding the maximum allowed per well owner",
        )

        self.excess_budget_scaling = Param(
            initialize=0,
            mutable=True,
            within=NonNegativeReals,
            doc="Scaling factor for the excess budget",
        )

        self.override_slack_scaling = Param(
            initialize=0,
            mutable=True,
            within=NonNegativeReals,
            doc="Scaling factor for override slack variables",
        )

        # pylint: disable=undefined-variable
        self.cluster = ClusterBlock(
            self.set_clusters, rule=make_cluster_model_rule(override_data)
        )

        # Add total budget constraint
        self.total_budget_constraint = Constraint(
            expr=(
                self.total_budget
                - sum(self.cluster[c].plugging_cost for c in self.set_clusters)
                == self.unused_budget - self.excess_budget
            ),
            doc="Total cost of plugging must be within the total budget",
        )
        if model_inputs.config.objective_weight_impact < 100:
            if model_inputs.config.efficiency_formulation == "Max Scaling":
                model_inputs.compute_efficiency_scaling_factors()
            for c in self.set_clusters:
                self.cluster[c].efficiency_model = EfficiencyBlock()
                self.cluster[c].efficiency_model.build_efficiency_model(
                    formulation_type=model_inputs.config.efficiency_formulation
                )

        wd = model_inputs.config.well_data
        self.set_wells = Set(initialize=wd.data.index.tolist())

        self.well_selected = Var(
            self.set_wells,
            within=Binary,
            doc="If well is selected in any project",
        )

        @self.Constraint(self.set_wells)
        def well_selection_constraint(self, w):
            return self.well_selected[w] == sum(
                self.cluster[c].select_well[w]
                for c in self.set_clusters
                if w in self.cluster[c].set_wells
            )

        if model_inputs.config.cluster_method == "Exhaustive":

            @self.Constraint(self.set_clusters)
            def anchor_well_constraint(self, c):
                return self.cluster[c].select_cluster == self.cluster[c].select_well[c]
                # the index c works for select_well because in exhaustive clustering
                # the well index is the same as the cluster number

        # Add optional constraints:
        if model_inputs.config.threshold_distance is not None:
            for c in self.set_clusters:
                self.cluster[c].add_distant_well_cuts()

        if model_inputs.config.max_wells_per_owner is not None:
            self.add_owner_well_count()

        scaling_factor_budget, scaling_factor_override, budget_sufficient = (
            self._slack_variable_scaling()
        )
        if model_inputs.config.min_budget_usage is not None:
            if budget_sufficient:
                LOGGER.warning(
                    "Ignoring min_budget_usage as the total_budget is sufficient to plug all wells."
                )
            else:
                self.add_min_budget_usage()

        if model_inputs.config.penalize_unused_budget:
            self.unused_budget_scaling = scaling_factor_budget

        # Add variables and constraints related to override re-optimization only
        if override_data and override_data.override_status:
            self.fix_var(override_data)

            self.excess_budget_scaling = 100 * scaling_factor_budget
            self.override_slack_scaling = scaling_factor_override

            if model_inputs.config.threshold_distance is not None:
                self.excess_distant_pairs = Var(
                    within=NonNegativeReals,
                    doc="Number of well pairs exceeding the distance threshold",
                )
                self.add_distant_well_count(override_data)

        # Append the objective function
        self.append_objective(override_data)

    def add_owner_well_count(self):
        """
        Constrains the maximum number of wells belonging to a specific owner
        chosen for plugging.
        """
        max_owc = self.model_inputs.config.max_wells_per_owner
        owner_dict = self.model_inputs.owner_well_count

        @self.Constraint(
            owner_dict.keys(),
            doc="Limit number of wells belonging to each owner",
        )
        def max_well_owner_constraint(b, owner):
            return (
                sum(b.well_selected[w] for w in owner_dict[owner])
                <= max_owc + self.excess_owc[owner]
            )

    def add_distant_well_count(self, override_data):
        """
        Count the number of well pairs that exceed the distance threshold
        for clusters that had wells reassigned during override
        re-optimization.
        """

        self.set_clusters_reassign = Set(
            initialize=list(override_data.reassign.keys()),
            doc="Clusters that have wells reassigned",
        )

        self.num_distant_well_pairs = Var(
            self.set_clusters_reassign,
            within=NonNegativeReals,
            doc="Number of distant well pairs for each reassigned cluster",
        )

        reassign_dict = override_data.reassign

        @self.Constraint(self.set_clusters_reassign)
        def count_distant_wells(b, c):
            reassign_well_list = reassign_dict[c]
            params = b.model_inputs
            wd = params.config.well_data
            wells_in_cluster = params.campaign_candidates[c]

            pairwise_distance = distance_reassigned_well(
                wells_in_cluster, reassign_well_list, wd
            )

            # Filter well pairs that exceed the threshold
            well_pairs_excess = [
                (w1, w2)
                for (w1, w2), dist in pairwise_distance.items()
                if dist > b.model_inputs.config.threshold_distance
            ]

            # Attach filtered well pairs as the set_well_pairs_remove set of the block
            b.cluster[c].set_well_pairs_remove.set_value(well_pairs_excess)

            # Add constraint for skipping distant pairs
            b.cluster[c].add_distant_well_cuts()

            # Constraint: Count the number of distant pairs with both wells selected
            return b.num_distant_well_pairs[c] == sum(
                b.cluster[c].is_distant_pair[w1, w2]
                for (w1, w2) in b.cluster[c].set_well_pairs_remove
            )

        @self.Constraint()
        def total_excess_distant_wells(b):
            return self.excess_distant_pairs == sum(
                b.num_distant_well_pairs[c] for c in b.set_clusters_reassign
            )

    def fix_var(self, override_data):
        """
        identify clusters and/or the wells with in the cluster that will be fixed
        based on the override selection

        Parameters
        ----------
        override_data : ReOptimizationData
            A ReOptimizationData object containing the necessary information
            related to the re-optimization of override
        """

        # obtain the dictionary for clusters being fixed and wells being fixed
        cluster_fix_dict = override_data.re_optimize_cluster_dict
        well_fix_dict = override_data.re_optimize_well_dict

        # Combine keys (cluster) of cluster_fix_dict and well_fix_dict and remove
        # duplicates using a set
        unique_clusters = set(cluster_fix_dict.keys()).union(set(well_fix_dict.keys()))
        unique_clusters_list = list(unique_clusters)

        # Obtain information on whether a cluster is fixed and if any wells in the cluster
        # are fixed.
        # The fix() method applies the fixes to the cluster and wells independently.
        # Iterate over all clusters in the unique_clusters_list
        for c in unique_clusters_list:
            # Get the binary variable for the cluster selected to be fixed. If only
            # specific wells in the cluster are fixed, assign None to the cluster.
            if c in cluster_fix_dict:
                cluster_v = cluster_fix_dict[c]
            else:
                cluster_v = None

            # Get the binary variable for the wells selected to be fixed. For a fixed cluster,
            # if no specific wells are selected, assign None to the wells.
            if c in well_fix_dict:
                wells_v = well_fix_dict[c]
            else:
                wells_v = None

            self.cluster[c].fix(cluster_v, wells_v)

    def add_min_budget_usage(self):
        """
        Implements an upper bound on the unused budget to ensure that at
        least the specified percentage of the budget is utilized.
        """

        max_unused_budget = (
            1 - self.model_inputs.config.min_budget_usage / 100
        ) * self.total_budget

        # Define upper bound for the budget amount that is not utilized
        # pylint: disable=no-member
        self.unused_budget.setub(max_unused_budget)

    def append_objective(self, override_data):
        """
        Appends objective function to the model
        """
        total_impact_score = sum(
            self.cluster[c].cluster_impact_score for c in self.set_clusters
        )

        # Compute the total cluster efficiency score (if applicable)
        total_efficiency_score = sum(
            (
                self.cluster[c].efficiency_model.cluster_efficiency_score
                if hasattr(self.cluster[c], "efficiency_model")
                else 0
            )
            for c in self.set_clusters
        )

        # Compute the total penalty for constraints being violated when
        # performing the re-optimization of override
        self.excess_campaign_length = Expression(
            expr=sum(
                self.cluster[c].max_well_violation + self.cluster[c].min_well_violation
                for c in self.set_clusters
            )
        )

        # Set all re-optimization-related variables to zero when solving the
        # base optimization problem or when no override selections are provided.
        if not override_data or not override_data.override_status:
            self.excess_budget.fix(0)  # pylint: disable=no-member
            for owc_value in self.excess_owc.values():
                owc_value.fix(0)  # pylint: disable=no-member
            self.excess_campaign_length_constraint = Constraint(
                expr=(self.excess_campaign_length == 0),
                doc="Ensure the minimum and maximum number of wells in a project constraint "
                "is satisfied under the non-override scenario.",
            )
            self.total_constraint_penalty = 0
        else:
            self.budget_status = Var(
                within=Binary,
                doc="1 if there is excess budget; 0 if there is unused budget",
            )

            self.excess_budget_constraint = Constraint(
                expr=(self.excess_budget <= self.budget_status * self.total_budget),
                doc="Ensure excess_budget and unused_budget are not non-zero at the same time.",
            )

            self.unused_budget_constraint = Constraint(
                expr=(
                    self.unused_budget <= (1 - self.budget_status) * self.total_budget
                ),
                doc="Ensure excess_budget and unused_budget are not non-zero at the same time.",
            )
            self.total_constraint_penalty = Expression(
                expr=self.excess_budget * self.excess_budget_scaling
                + self.override_slack_scaling
                * (
                    sum(
                        self.excess_owc[owner]
                        for owner in self.model_inputs.owner_well_count.keys()
                    )
                    + (
                        self.excess_distant_pairs
                        if hasattr(self, "excess_distant_pairs")
                        else 0
                    )
                    + self.excess_campaign_length
                )
            )

        # Define the total priority score as the objective
        self.total_priority_score = Objective(
            expr=(
                total_impact_score
                + total_efficiency_score
                - self.unused_budget_scaling * self.unused_budget
                - self.total_constraint_penalty
            ),
            sense=maximize,
            doc=(
                "Total impact and efficiency score minus scaled slack "
                "variables for unutilized budget and penalties for constraint violations."
            ),
        )

    def _slack_variable_scaling(self):
        """
        Check whether the budget is sufficient to plug all wells and (1)
        calculate the scaling factor for the budget slack variable based on the
        corresponding scenario. (2) Calculate the scaling factor for the slack
        variables of constraints violated during re-optimization of override.
        """
        # estimate the maximum number of wells can be plugged with the budget.
        unit_cost = max(self.model_inputs.get_mobilization_cost.values()) / max(
            self.model_inputs.get_mobilization_cost
        )
        max_well_num = self.model_inputs.get_total_budget / unit_cost

        # calculate the scaling factor for the budget slack variable if the
        # budget is not sufficient to plug all wells
        if max_well_num < len(self.model_inputs.config.well_data):
            scaling_budget_slack = (
                max_well_num
                * max(self.model_inputs.config.well_data["Priority Score [0-100]"])
            ) / self.model_inputs.get_total_budget
            budget_sufficient = False

            # scale the penalty for violated constraints to be 100 times greater
            # than the possible maximum total priority score across all wells.
            scaling_override_slack = max_well_num * max(
                self.model_inputs.config.well_data["Priority Score [0-100]"]
            )

        # calculate the scaling factor for the budget slack variable if the
        # budget is sufficient to plug all wells
        else:
            scaling_budget_slack = (
                len(self.model_inputs.config.well_data)
                * max(self.model_inputs.config.well_data["Priority Score [0-100]"])
            ) / self.model_inputs.get_total_budget
            budget_sufficient = True

            # scale the penalty for violated constraints to be 100 times greater
            # than the possible maximum total priority score across all wells.
            scaling_override_slack = len(self.model_inputs.config.well_data) * max(
                self.model_inputs.config.well_data["Priority Score [0-100]"]
            )
            budget_sufficient = True

        return scaling_budget_slack, scaling_override_slack, budget_sufficient

    def get_optimal_campaign(self):
        """
        Extracts the optimal choice of wells from the solved model
        """
        optimal_campaign = {}
        plugging_cost = {}
        efficiency_scores_projects = {}

        for c in self.set_clusters:
            blk = self.cluster[c]
            if blk.select_cluster.value < 0.05:
                # Cluster c is not chosen, so continue
                continue

            # Wells in cluster c are chosen
            optimal_campaign[c] = []
            plugging_cost[c] = blk.plugging_cost.value
            for w in blk.set_wells:
                if blk.select_well[w].value > 0.95:
                    # Well w is chosen, so store it in the dict
                    optimal_campaign[c].append(w)

            if hasattr(blk, "efficiency_model"):
                efficiency_scores_projects[c] = (
                    blk.efficiency_model.get_efficiency_scores()
                )

        wd = self.model_inputs.config.well_data
        return Campaign(
            wd,
            optimal_campaign,
            plugging_cost,
            self.model_inputs,
            efficiency_scores_projects,
        )

    def get_solution_pool(self, solver):
        """
        Extracts solutions from the solution pool

        Parameters
        ----------
        solver : Pyomo solver object
        """
        pm = self  # This is the Pyomo model
        # pylint: disable=protected-access
        gm = solver._solver_model  # This is the Gurobipy model
        # Get Pyomo var to Gurobipy var map.
        # Gurobi vars can be accessed as pm_to_gm[<pyomo var>]
        pm_to_gm = solver._pyomo_var_to_solver_var_map

        # Number of solutions found
        num_solutions = gm.SolCount
        solution_pool = {}
        # Well data
        # wd = self.model_inputs.config.well_data

        for i in range(num_solutions):
            gm.Params.SolutionNumber = i

            optimal_campaign = {}
            plugging_cost = {}

            for c in pm.set_clusters:
                blk = pm.cluster[c]
                if pm_to_gm[blk.select_cluster].Xn < 0.05:
                    # Cluster c is not chosen, so continue
                    continue

                # Wells in cluster c are chosen
                optimal_campaign[c] = []
                plugging_cost[c] = pm_to_gm[blk.plugging_cost].Xn
                for w in blk.set_wells:
                    if pm_to_gm[blk.select_well[w]].Xn > 0.95:
                        # Well w is chosen, so store it in the dict
                        optimal_campaign[c].append(w)

            solution_pool[i + 1] = Campaign(
                wd=self.model_inputs.config.well_data,
                clusters_dict=optimal_campaign,
                plugging_cost=plugging_cost,
                opt_model_inputs=self.model_inputs,
            )

        return solution_pool
