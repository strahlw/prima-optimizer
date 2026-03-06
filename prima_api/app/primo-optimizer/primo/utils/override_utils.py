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
import copy
import logging
import operator
from dataclasses import dataclass
from itertools import combinations, product
from typing import Dict, List

# Installed libs
import pandas as pd
from haversine import Unit, haversine_vector

# User-defined libs
from primo.opt_model.result_parser import Campaign
from primo.utils.clustering_utils import distance_matrix

LOGGER = logging.getLogger(__name__)


class AssessFeasibility:
    """
    Class for assessing whether the P&A projects adhere to the constraints
    defined in the optimization problem.

    Parameters
    ----------
    opt_inputs : OptModelInputs
        The optimization model inputs.

    opt_campaign : Dict
        A dictionary where keys are cluster numbers and values
        are list of wells for each cluster in the P&A projects.


    Attributes
    ----------
    campaign_cost_dict : Dict
        A dictionary that will hold the cost calculations for the projects within the campaign,
        mapped to their respective project identifiers.
    """

    def __init__(self, opt_inputs, opt_campaign: Dict):

        self.opt_inputs = opt_inputs
        self.new_campaign = opt_campaign
        self.campaign_cost_dict = {}

        # prevent duplication in plug_list
        self.plug_list = list(
            {well for well_list in self.new_campaign.values() for well in well_list}
        )
        self.wd = self.opt_inputs.config.well_data._construct_sub_data(self.plug_list)

        for cluster, groups in self.new_campaign.items():
            n_wells = len(groups)
            campaign_cost = self.opt_inputs.get_mobilization_cost[n_wells]
            self.campaign_cost_dict[cluster] = campaign_cost

    def assess_budget(self) -> float:
        """
        Assesses whether the budget constraint is violated and returns the
        amount by which the budget is violated. A 0 or negative value indicates
        that we are still under budget
        """
        total_cost = 0

        total_cost = sum(
            project_cost for _, project_cost in self.campaign_cost_dict.items()
        )

        return round((total_cost - self.opt_inputs.get_total_budget) * 1e6)

    def assess_owner_well_count(self) -> Dict:
        # pylint: disable=protected-access
        """
        Assess whether the owner well count constraint is violated or not.
        Returns list of owners and wells selected for each for whom the owner
        well count constraint is violated
        """
        opt_inputs = self.opt_inputs.config
        max_wells_per_owner = opt_inputs.max_wells_per_owner
        if max_wells_per_owner is None:
            # When the user does not have owner information
            # or does not wish to prioritize
            # this constraint becomes meaningless
            return {}
        violated_operators = {}
        for well_operator, groups in self.wd.data.groupby(
            self.wd._col_names.operator_name
        ):
            n_wells = len(groups)
            if n_wells > self.opt_inputs.config.max_wells_per_owner:
                violated_operators.setdefault("Owner", []).append(well_operator)
                violated_operators.setdefault("Number of wells", []).append(n_wells)
                violated_operators.setdefault("Wells", []).append(
                    groups[self.wd._col_names.well_id].to_list()
                )

        return violated_operators

    def assess_distances(self) -> Dict:
        # pylint: disable=protected-access
        """
        Assess whether the maximum distance between two wells constraint is violated or not
        """
        distance_threshold = self.opt_inputs.config.threshold_distance
        distance_violation = {}
        # Assign weight for distance as 1 to ensure the distance matrix returns physical
        # distance between two well pairs
        metric_array = distance_matrix(self.wd, {"distance": 1})

        for cluster, well_list in self.new_campaign.items():
            for w1, w2 in combinations(well_list, 2):
                well_distance = metric_array.loc[w1, w2]
                if well_distance > distance_threshold:
                    distance_violation.setdefault("Project", []).append(cluster)
                    distance_violation.setdefault("Well 1", []).append(
                        self.wd.data.loc[w1][self.wd._col_names.well_id]
                    )
                    distance_violation.setdefault("Well 2", []).append(
                        self.wd.data.loc[w2][self.wd._col_names.well_id]
                    )
                    distance_violation.setdefault(
                        "Distance between Well 1 and 2 [Miles]", []
                    ).append(well_distance)

        return distance_violation

    def _assess_project_size_violation(self, threshold, comparator) -> Dict:
        """
        Generic function to assess whether a project violates the project size constraint.
        """
        num_wells_in_project_violation = {}

        for cluster, well_list in self.new_campaign.items():
            if comparator(len(well_list), threshold):
                num_wells_in_project_violation.setdefault("Project", []).append(cluster)
                num_wells_in_project_violation.setdefault("Length", []).append(
                    len(well_list)
                )

        return num_wells_in_project_violation

    def assess_max_num_well_in_project(self) -> Dict:
        """
        Assess whether the max number of wells in a project constraint is violated or not
        """
        max_wells_in_project_threshold = self.opt_inputs.config.max_wells_in_project
        if max_wells_in_project_threshold is None:
            return {}

        return self._assess_project_size_violation(
            max_wells_in_project_threshold, operator.gt
        )

    def assess_min_num_well_in_project(self) -> Dict:
        """
        Assess whether the min number of wells in a project constraint is violated or not
        """
        min_wells_in_project_threshold = self.opt_inputs.config.min_wells_in_project
        if min_wells_in_project_threshold is None:
            return {}

        return self._assess_project_size_violation(
            min_wells_in_project_threshold, operator.lt
        )

    def assess_feasibility(self) -> bool:
        """
        Assesses whether current set of selections is feasible
        """
        if self.assess_budget() > 0:
            return False

        if self.assess_owner_well_count():
            return False

        if self.assess_distances():
            return False

        if self.assess_max_num_well_in_project():
            return False

        if self.assess_min_num_well_in_project():
            return False

        return True

    def violation_info(self):
        """
        Return information on constraints that the new campaign
        have violated.
        """
        violation_info_dict = {}
        if self.assess_feasibility() is False:
            violation_info_dict = {"Project Status:": "CONSTRAINT(S) VIOLATED"}
            violate_cost = self.assess_budget()
            violate_operator = self.assess_owner_well_count()
            violate_distance = self.assess_distances()
            violate_max_num_well_in_project = self.assess_max_num_well_in_project()
            violate_min_num_well_in_project = self.assess_min_num_well_in_project()

            if violate_cost > 0:
                msg = (
                    "After the modification, the total budget is over "
                    f"the limit by ${int(violate_cost)}. Please consider modifying "
                    "wells you have selected or "
                    "re-running the optimization problem."
                )

                violation_info_dict[msg] = """"""

            if violate_operator:
                msg = (
                    "After the modification, the following owners have "
                    f"more than {self.opt_inputs.config.max_wells_per_owner} well(s) "
                    "being selected. Please consider modifying wells you have "
                    "selected or re-running "
                    "the optimization problem."
                )

                violate_operator_df = pd.DataFrame.from_dict(violate_operator)
                violation_info_dict[msg] = violate_operator_df

            if violate_distance:
                msg = (
                    "After the modification, the following projects have "
                    "wells are far away from each others. Please consider modifying "
                    "wells you have selected or "
                    "re-running the optimization problem."
                )

                violate_distance_df = pd.DataFrame.from_dict(violate_distance)
                violation_info_dict[msg] = violate_distance_df

            if violate_max_num_well_in_project:
                msg = (
                    "After the modification, the following projects have "
                    f"more than {self.opt_inputs.config.max_wells_in_project} well(s) "
                    "being selected. Please consider modifying wells you have "
                    "selected or re-running "
                    "the optimization problem."
                )

                violate_max_wells_df = pd.DataFrame.from_dict(
                    violate_max_num_well_in_project
                )
                violation_info_dict[msg] = violate_max_wells_df

            if violate_min_num_well_in_project:
                msg = (
                    "After the modification, the following projects have "
                    f"less than {self.opt_inputs.config.min_wells_in_project} well(s) "
                    "being selected. Please consider modifying wells you have "
                    "selected or re-running "
                    "the optimization problem."
                )

                violate_min_wells_df = pd.DataFrame.from_dict(
                    violate_min_num_well_in_project
                )
                violation_info_dict[msg] = violate_min_wells_df

        else:
            violation_info_dict = {"Project Status:": "FEASIBLE"}

        return violation_info_dict


# pylint: disable=too-many-instance-attributes
class OverrideCampaign:
    """
    Class for constructing new campaigns based on the override results
    and returning infeasibility information.

    Parameters
    ----------
    override_selections : OverrideSelections
        Object containing the override selections

    opt_inputs : OptModelInputs
        Object containing the necessary inputs for the optimization model

    opt_campaign : dict
        A dictionary for the original suggested P&A project
        where keys are cluster numbers and values
        are list of wells for each cluster.

    eff_metrics : EfficiencyMetrics
        The efficiency metrics
    """

    def __init__(
        self,
        override_selections,
        opt_inputs,
        opt_campaign: Dict,
        eff_metrics,
    ):
        opt_campaign_copy = copy.deepcopy(opt_campaign)
        self.new_campaign = opt_campaign_copy
        self.remove = override_selections.remove_widget_return
        self.add = override_selections.add_widget_return
        self.lock = override_selections.lock_widget_return
        self.opt_inputs = opt_inputs
        self.eff_metrics = eff_metrics

        # change well cluster
        self._modify_campaign()

        self.feasibility = AssessFeasibility(self.opt_inputs, self.new_campaign)
        self.violation_info = self.feasibility.violation_info()

    def _modify_campaign(self):
        """
        Modify the original suggested P&A project
        """
        # remove clusters
        for cluster in self.remove.cluster:
            del self.new_campaign[cluster]

        # remove wells
        for cluster, well_list in self.remove.well.items():
            if cluster not in self.remove.cluster:
                for well in well_list:
                    self.new_campaign[cluster].remove(well)

        # add well with new cluster
        for cluster, well_list in self.add.new_clusters.items():
            self.new_campaign.setdefault(cluster, []).extend(well_list)

    def override_campaign(self):
        """
        Construct the new Campaign object based on the override selection
        """
        plugging_cost = self.feasibility.campaign_cost_dict
        wd = self.opt_inputs.config.well_data
        return Campaign(wd, self.new_campaign, plugging_cost, self.opt_inputs)

    def recalculate(self):
        """
        Recalculate the efficiency scores and impact scores of the new campaign
        based on the override selection
        """
        override_campaign = self.override_campaign()
        return override_campaign

    def recalculate_scores(self):
        """
        A function to return the impact score and efficiency score of
        the new campaign based on the override selection
        """
        override_campaign = self.recalculate()
        return {
            project_id: [project.impact_score, project.efficiency_score]
            for project_id, project in override_campaign.projects.items()
        }

    def re_optimize_data(self):
        """
        Generate dictionaries for clusters and wells to be fixed, along with
        a list of clusters that contain wells reassigned from other clusters,
        based on the override selection
        """
        re_optimize_cluster_dict = {}
        re_optimize_well_dict = {}

        # Assign 0 to wells being removed
        for cluster, well_list in self.remove.well.items():
            re_optimize_well_dict[cluster] = {well: 0 for well in well_list}

        # Assign 1 to wells being added
        for cluster, well_list in self.add.new_clusters.items():
            if cluster not in re_optimize_well_dict:
                re_optimize_well_dict[cluster] = {}
            for well in well_list:
                re_optimize_well_dict[cluster][well] = 1

        # Assign 1 to clusters being locked
        for cluster in self.lock.cluster:
            re_optimize_cluster_dict[cluster] = 1

        # Assign 1 to wells being locked
        for cluster, well_list in self.lock.well.items():
            if cluster not in re_optimize_well_dict:
                re_optimize_well_dict[cluster] = {}
            for well in well_list:
                re_optimize_well_dict[cluster][well] = 1

        # Generate a list of clusters which contain wells that are reassigned
        # from another cluster to this new cluster
        reassign = {
            key: list(
                set(self.add.new_clusters[key])
                - set(self.add.existing_clusters.get(key, []))
            )
            for key in self.add.new_clusters
            if set(self.add.new_clusters[key])
            - set(self.add.existing_clusters.get(key, []))
        }

        # Determine if an override was applied to ensure that re-optimization
        # returns the original results when no manual selections are made
        if (
            not self.remove.cluster
            and not self.remove.well
            and not self.add.existing_clusters
            and not self.lock.cluster
            and not self.lock.well
        ):
            override_status = False
        else:
            override_status = True

        return ReOptimizationData(
            re_optimize_cluster_dict, re_optimize_well_dict, reassign, override_status
        )


@dataclass
class ReOptimizationData:
    """
    Class for storing dictionaries for clusters and wells to be fixed,
    a list of clusters that contain wells reassigned from other clusters,
    and whether any override selection is made

    Parameters
    ----------
    re_optimize_cluster_dict : Dict[int, int]
        A dictionary mapping clusters (key) to binary values
        (0 or 1) indicating the cluster is fixed. Contains information on cluster
        selected to be locked

    re_optimize_well_dict : Dict[int, Dict[int, int]]
        A dictionary mapping clusters (key) to a list of dictionaries,
        where each dictionary contains wells (key) and their associated binary values
        (0 or 1) indicating the well is fixed within the respective cluster.

    reassign: Dict[int, List[int]]
        A dictionary contains ID of clusters (key) that contain wells reassigned from
        other clusters and the wells being reassigned (value).

    override_status: bool
        A boolean flag indicating whether an override selection has been made
    """

    re_optimize_cluster_dict: Dict[int, int]
    re_optimize_well_dict: Dict[int, Dict[int, int]]
    reassign: Dict[int, List[int]]
    override_status: bool


# pylint: disable=protected-access
def distance_reassigned_well(wells_in_cluster, wells_reassigned, wd):
    """
    Calculate the pairwise distances between existing wells in a cluster and
    wells being reassigned to that cluster from other clusters

    Parameters
    ----------
    wells_in_cluster : List
        A list of well currently belonging to the cluster

    wells_reassigned : List
        A list of well being reassigned to the cluster

    wd: WellData
        The WellData object.

    Raises
    ------
    pairwise_distance_dict: Dict
        A dictionary mapping well pairs (existing well, reassigned well) to their
        corresponding distance
    """
    wells_in_cluster_wd = wd._construct_sub_data(wells_in_cluster)
    wells_reassigned_wd = wd._construct_sub_data(wells_reassigned)

    cn = wd.column_names
    wells_in_cluster_coordinates = list(
        zip(
            wells_in_cluster_wd.data[cn.latitude],
            wells_in_cluster_wd.data[cn.longitude],
        )
    )
    wells_reassigned_coordinates = list(
        zip(
            wells_reassigned_wd.data[cn.latitude],
            wells_reassigned_wd.data[cn.longitude],
        )
    )

    pairwise_distance = haversine_vector(
        wells_in_cluster_coordinates,
        wells_reassigned_coordinates,
        unit=Unit.MILES,
        comb=True,
    )

    pairwise_distance_df = pd.DataFrame(
        pairwise_distance.transpose(),
        columns=wells_reassigned_wd.data.index,
        index=wells_in_cluster_wd.data.index,
    )

    well_pairs = list(product(list(wells_in_cluster), list(wells_reassigned)))

    pairwise_distance_matrix = pairwise_distance_df.stack()[well_pairs]

    pairwise_distance_dict = {
        (w1, w2): pairwise_distance_matrix[w1, w2]
        for w1, w2 in product(list(wells_in_cluster), list(wells_reassigned))
    }

    return pairwise_distance_dict
