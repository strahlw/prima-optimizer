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
Implements validity checks on input parameters for running scenarios
and ranking wells
"""
# Standard libs
import logging
from typing import Optional

# Installed libs
from primo.data_parser import EfficiencyMetrics, ImpactMetrics
from primo.data_parser.input_config import ScenarioType

LOGGER = logging.getLogger(__name__)


def is_valid_impact(im_metrics: ImpactMetrics) -> bool:
    """
    Validates the impact_metrics

    Parameters
    ----------
    im_metrics : ImpactMetrics
        Impact Metrics from scenario

    Returns
    -------
    True if the metrics is valid, False otherwise
    """

    try:
        im_metrics.check_validity()
    except ValueError:
        LOGGER.info(f"Invalid impact metrics received: {im_metrics}")
        return False

    return True


def is_valid_efficiency(eff_metrics: EfficiencyMetrics) -> bool:
    """
    Validates the efficiency_metrics

    Parameters
    ----------
    eff_metrics : EfficiencyMetrics
        Efficiency Metrics from scenario

    Returns
    -------
    True if the metrics is valid, False otherwise
    """
    try:
        eff_metrics.check_validity()
    except ValueError:
        LOGGER.info(f"Invalid efficiency metrics received: {eff_metrics}")
        return False

    return True


def is_valid_scenario_dependent(
    scenario_type: ScenarioType,
    im_metrics: Optional[ImpactMetrics] = None,
    eff_metrics: Optional[EfficiencyMetrics] = None,
) -> bool:
    """
    Validates impact and efficiency metrics based on scenario type

    Parameters
    ----------
    im_metrics : ImpactMetrics
        Impact Metrics from scenario

    eff_metrics : EfficiencyMetrics
        Efficiency Metrics from scenario

    Returns
    -------
    True if the appropriate metrics are valid, False otherwise
    """

    valid_impact = True
    if scenario_type.well_ranking:
        valid_impact = is_valid_impact(im_metrics)

    valid_efficiency = True
    if scenario_type.project_recommendation:
        valid_efficiency = is_valid_efficiency(eff_metrics)

    return valid_impact and valid_efficiency
