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
# pylint: disable=too-many-lines,too-few-public-methods
# Standard libs
from datetime import datetime
from enum import Enum
from typing import Dict, List, Literal, Optional, Union

# Installed libs
from pydantic import BaseModel, Field, FilePath, ValidationInfo, field_validator

# User-defined libs
from parameters import EFFICIENCY_FACTORS, IMPACT_FACTORS
from utils.raise_exception import raise_exception


def validate_max_value(
    value: int, min_value: int, max_string: str, min_string: str
) -> int:
    """
    Runs a quick validation to ensure that the 'value' provided as an upper bound is larger than
    a previously specified lower bound with 'min_value'

    Parameters
    ----------
    value : int
        The candidate 'upper bound'

    min_value : int
        A previously validated lower bound

    max_string : str
        The string identifier for the upper bound under consideration

    min_string : str
        The string identifier for the lower bound under consideration

    Returns
    -------
    A validated upper bound

    Raises
    ------
    ValueError
        If the upper bound provided is lower than the lower bound
    """
    if value < min_value:
        msg = (
            f"{max_string}: {value} is less than {min_string}: {min_value}."
            " Optimization is infeasible"
        )
        raise_exception(msg, ValueError)
    return value


class Status(str, Enum):
    """
    Set up job status to match the Status from the Celery backend to return
    from the API

    (https://docs.celeryq.dev/en/stable/reference/celery.result.html)
    """

    STARTED = "STARTED"
    REVOKED = "REVOKED"
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    RETRY = "RETRY"
    FAILURE = "FAILURE"
    SUCCESS = "SUCCESS"
    KILLED = "KILLED"


class PrimoResponse(BaseModel):
    """
    Object defining a response schema for the API

    Attributes
    ----------
    id : str
        The ID of the task under consideration

    status : Status
        Status for the task under consideration

    date : datetime.datetime
        The datetime when task was completed
    """

    id: str = Field(title="id", description="The ID of the task under consideration")
    status: Status = Field(
        title="status", description="Status for the task under consideration"
    )
    date: Optional[datetime] = Field(
        title="date", description="The datetime when task was completed", default=None
    )


class DataInputCheckResponse(PrimoResponse):
    """
    Object defining a response schema for the API

    Attributes
    ----------
    id : str
        The ID of the task under consideration

    status : Status
        Status for the task under consideration

    date : datetime.datetime
        The datetime when task was completed

    contains_ranking: bool
        True if the data contains ranking data, else False
    """

    contains_ranking: bool = Field(
        title="Contains Ranking",
        description="A flag for if the data contains ranking data or not",
        default=False,
    )


class OptimizerResults(PrimoResponse):
    """
    Object defining a response schema for get_status API calls

    Attributes
    ----------
    description : str
        Metadata providing additional information about the state of a job
    """

    description: Optional[str] = Field(
        title="description",
        description="Metadata providing additional information about job",
        default=None,
    )


class RankResults(PrimoResponse):
    """
    Object defining a response schema for rank_wells API calls

    Attributes
    ----------
    data : List[dict]
    """

    data: List[dict] = Field(
        title="data", description="The data with the ranked well objects"
    )


class ValidWellIdsResults(PrimoResponse):
    """
    Object defining a response schema for valid_well_ids API calls

    Attributes
    ----------
    data : List[int]
    """

    data: List[int] = Field(
        title="data", description="The data with the valid well ids"
    )


class DataSummaryResults(RankResults):
    """
    Object defining a response schema for data_summary API calls

    Attributes
    ----------
    data : List[dict]
    """


class KPISummaryResponse(PrimoResponse):
    """
    Object defining a response schema for the KPI summary API call

    Attributes
    ----------
    data : Dict[str, Dict[str, Union[str, float]]]
        The KPI Summary
    """

    data: dict = Field(title="data", description="KPI summary data")


class OverrideRecalculationCheckResponse(PrimoResponse):
    """
    Object defining a response schema for manual_override_recalculation_check
    API call

    Attributes
    ----------
    data : Dict[str, Dict[str, Dict[str, float]]]
        Information on constraints being violated during the override
        recalculation
    """

    data: dict = Field(title="data", description="Feasibility check for override")


class OverrideReoptimizationCheckResponse(OverrideRecalculationCheckResponse):
    """
    Object defining a response schema for the manual_reoptimization_check API call

    Attributes
    ----------
    data : Dict[str, Dict[str, Dict[str, float]]]
        Information on constraints being violated during the override
        re-optimization
    """


class Factor(BaseModel):
    """
    Object determines a "factor" and contains
    whether it is selected and its value

    Attributes
    ----------
    value : int
        The weight selected for the factor

    selected : bool
        Boolean to indicate whether factor is selected
    """

    value: int = Field(
        title="value",
        description="The weight selected for the factor",
        ge=0,
        le=100,
    )
    selected: bool = Field(
        title="selected", description="Boolean to indicate whether factor was selected"
    )

    def get_child_factors(self):
        """
        Returns child factors if any are set up

        Parameters
        ----------
        None

        Returns
        -------
        SetOfFactors
            A SetOfFactors object denoting the child
            factors for the object
        """

        if hasattr(self, "child_factors"):
            return self.child_factors.__dict__
        return {}


class SetOfFactors(BaseModel):
    """
    A container object for a set of factors under consideration
    """

    def __iter__(self):
        # Iterate over all fields in the object
        return iter(self.__dict__.items())

    def get_primary_factors(self) -> Dict[str, Factor]:
        """
        Returns all Factors in the set that are not characterized as child factors

        Parameters
        ----------
        None

        Returns
        -------
        Dict[str, Factor]
            A dictionary with factor names as string keys and Factor objects
            as their corresponding values
        """
        return {
            attr_name: attr_value
            for attr_name, attr_value in self.__dict__.items()
            if attr_name != "child_factors"
        }

    def get_child_factors(self):
        """
        Returns all Factors in the set that are characterized as child factors

        Parameters
        ----------
        None

        Returns
        -------
        SetOfFactors
            A SetOfFactors object denoting the child
            factors for the object
        """

        if hasattr(self, "child_factors"):
            return self.child_factors.__dict__
        return {}


class LossesChildren(SetOfFactors):
    """
    Object determines impact sub-factors associated
    with "losses": These are proxies used to determine if a well is leaking
    in the absence of real losses data

    Attributes
    ----------
    leak : Factor
        Has a leak been observed at a well

    violation : Factor
        Has the well been served with any violations

    compliance : Factor
        Has the well been in compliance with regulations

    incident : Factor
        Does the well have any documented incidents

    hydrocarbon_losses : Factor
        The quantity of hydrocarbon losses for a well

    """

    leak: Factor = Field(
        title="leak",
        description="Factor parameters to use detection of leaks as proxy for hydrocarbon losses",
    )

    violation: Factor = Field(
        title="violation",
        description="Factor parameters to use past violations as proxy for hydrocarbon losses",
    )
    compliance: Factor | None = None
    # = Field(
    #     title="compliance",
    #     description=("Factor parameters to use compliance reports"
    #  "as proxies for hydrocarbon losses"),
    # )
    incident: Factor | None = None
    # = Field(
    #     title="incident",
    #     description=("Factor parameters to use documented incidents"
    #  "as proxies for hydrocarbon losses"),
    # )
    hydrocarbon_losses: Factor | None = None
    # = Field(
    #     title="hydrocarbon_losses",
    #     description=("Factor parameter for actual hydrocarbon losses"),
    # )


class Losses(SetOfFactors, Factor):
    """
    Object determines weights/selections associated with
    losses as an impact factor

    Attributes
    ----------
    child_factors : LossesChildren
        Sub-factors associated with losses
    """

    child_factors: LossesChildren = Field(
        title="child_factors",
        description="Child factor parameters associated with losses proxies",
    )


class EcologicalReceptorsChildren(SetOfFactors):
    """
    Object determines impact sub-factors associated
    with "ecological receptors": These are factors related to
    proximity and impact on ecological receptors

    Attributes
    ----------
    endangered_species_on_site : Factor
        endangered_species as a priority factor

    """

    endangered_species_on_site: Factor = Field(
        title="endangered_species",
        description="Impact factor for well impact on endangered species",
    )


class EcologicalReceptors(SetOfFactors, Factor):
    """
    Object determines weights/selections associated with
    ecological receptors as an impact factor

    Attributes
    ----------
    child_factors : LossesChildren
        Sub-factors associated with losses
    """

    child_factors: EcologicalReceptorsChildren = Field(
        title="child_factors",
        description="Child factor parameters associated with ecological receptors",
    )


class EnvironmentChildren(SetOfFactors):
    """
    Object determines impact sub-factors associated
    with "sensitive receptors".

    Attributes
    ----------
    wetlands : Factor
        Nearby wetlands as a sub-factor for environment

    water_source_nearby : Factor
        Nearby water sources as a sub-factor for environment

    known_soil_or_water_impact : Factor
        Known soil or water impact as a sub-factor for environment

    fed_wetlands_near : Factor
        Impact metric for federal wetlands near wells

    fed_wetlands_far : Factor
        Impact metric for federal wetlands far from, but close to wells

    state_wetlands_near : Factor
        Impact metric for state wetlands near wells

    state_wetlands_far : Factor
        Impact metric for state wetlands far from, but close to wells
    """

    wetlands: Factor | None = None
    # = Field(
    #     title="wetlands",
    #     description="Factor parameters for nearby wetlands as an environmental impact factor",
    # )
    water_source_nearby: Factor = Field(
        title="water_source_nearby",
        description="Factor parameters for water source nearby as an environmental impact factor",
    )
    known_soil_or_water_impact: Factor = Field(
        title="known_soil_or_water_impact",
        description=(
            "Factor parameters for known soil or water impact"
            "as an environmental impact factor"
        ),
    )
    fed_wetlands_near: Factor | None = None
    #  = Field(
    #     title="fed_wetlands_near",
    #     description="Impact metric for federal wetlands near wells"
    # )
    fed_wetlands_far: Factor | None = None
    #  = Field(
    #     title="fed_wetlands_far",
    #     description="Impact metric for federal wetlands far from, but close to wells"
    # )
    state_wetlands_near: Factor | None = None
    #  = Field(
    #     title="state_wetlands_near",
    #     description="Impact metric for state wetlands near wells"
    # )
    state_wetlands_far: Factor | None = None
    #  = Field(
    #     title="state_wetlands_far",
    #     description= "Impact metric for state wetlands far from, but close to wells"
    # )


class Environment(SetOfFactors, Factor):
    """
    Object determines weights/selections associated with
    environment considerations as an impact factor

    Attributes
    ----------
    child_factors : EnvironmentChildren
        Sub-factors associated with losses
    """

    child_factors: EnvironmentChildren = Field(
        title="child_factors",
        description="Child factor parameters associated with environmental impact factors",
    )


class OtherLossesChildren(SetOfFactors):
    """
    Object determines impact sub-factors associated
    with "other losses".

    Attributes
    ----------
    brine_leak : Factor
        Impact metric for well brine leaks

    h2s_leak : Factor
        Impact metric for well h2s leaks
    """

    brine_leak: Factor | None = None
    # = Field(
    #     title="brine_leak",
    #     description="Impact metric for well brine leaks"
    # )
    h2s_leak: Factor | None = None
    # = Field(
    #     title="h2s_leak",
    #     description="Impact metric for well h2s leaks"
    # )


class OtherLosses(SetOfFactors, Factor):
    """
    Object determines weights/selections associated with
    other losses as an impact factor

    Attributes
    ----------
    child_factors : OtherLossesChildren
        Sub-factors associated with losses
    """

    child_factors: OtherLossesChildren = Field(
        title="child_factors",
        description="Child factor parameters associated with other losses impact factors",
    )


class SensitiveReceptorsChildren(SetOfFactors):
    """
    Object determines impact sub-factors associated
    with "sensitive receptors".

    Attributes
    ----------
    schools : Factor
        Nearby schools as a sub-factor for sensitive receptors

    hospitals : Factor
        Nearby hospitals as a sub-factor for sensitive receptors

    agriculture_area_nearby : Factor
        nearby agricultural areas as a sensitive receptor

    buildings_far : Factor
        buildings in proximity, but not as close as buildings_near

    buildings_near : Factor
        buildings in proximity closer than buildings_far
    """

    schools: Factor = Field(
        title="schools",
        description="Factor parameters for nearby schools as a sensitive receptor",
    )
    hospitals: Factor = Field(
        title="hospitals",
        description="Factor parameters for nearby hospitals as a sensitive receptor",
    )
    agriculture_area_nearby: Factor | None = None
    #  = Field(
    #     title="agriculture_area_nearby",
    #     description="Factor parameters for nearby agricultural areas as a sensitive receptor",
    # )
    buildings_far: Factor | None = None
    #  = Field(
    #     title="buildings_far",
    #     description="buildings in proximity, but not as close as buildings_near"
    # )
    buildings_near: Factor | None = None
    #  = Field(
    #     title="buildings_near",
    #     description="buildings in proximity closer than buildings_far"
    # )


class SensitiveReceptors(SetOfFactors, Factor):
    """
    Object determines weights/selections associated with
    sensitive receptors as an impact factor

    Attributes
    ----------
    child_factors : SensitiveReceptorsChildren
        Sub-factors associated with sensitive receptors
    """

    child_factors: SensitiveReceptorsChildren = Field(
        title="child_factors",
        description="Child factor parameters associated with sensitive receptors",
    )


class FiveYearProductionVolumesChildren(SetOfFactors):
    """
    Object determines impact sub-factors associated
    with production volumes.

    Attributes
    ----------
    five_year_gas_production : Factor
        Factor parameters for five-year gas production volume

    five_year_oil_production : Factor
        Factor parameters for five-year oil production volume


    """

    five_year_gas_production: Factor | None = None
    # = Field(
    #     title="five_year_gas_production",
    #     description="Factor parameters for five-year gas production volume"
    # )
    five_year_oil_production: Factor | None = None
    # = Field(
    #     title="five_year_oil_production",
    #     description="Factor parameters for five-year oil production volume"
    # )


class FiveYearProductionVolumes(SetOfFactors, Factor):
    """
    Object determines weights/selections associated with
    five-year production volume related impact factors

    Attributes
    ----------
    child_factors : FiveYearProductionVolumeChildren
        Sub-factors associated with five-year production volumes
    """

    child_factors: FiveYearProductionVolumesChildren = Field(
        title="child_factors",
        description="Child factor parameters associated with five-year production volumes",
    )


class LifelongProductionVolumesChildren(SetOfFactors):
    """
    Object determines impact sub-factors associated
    with production volumes.

    Attributes
    ----------
    five_year_gas_production : Factor
        Factor parameters for five-year gas production volume

    five_year_oil_production : Factor
        Factor parameters for five-year oil production volume


    """

    lifelong_gas_production: Factor | None = None
    # = Field(
    #     title="five_year_gas_production",
    #     description="Factor parameters for five-year gas production volume"
    # )
    lifelong_oil_production: Factor | None = None
    # = Field(
    #     title="five_year_oil_production",
    #     description="Factor parameters for five-year oil production volume"
    # )


class LifelongProductionVolumes(SetOfFactors, Factor):
    """
    Object determines weights/selections associated with
    five-year production volume related impact factors

    Attributes
    ----------
    child_factors : FiveYearProductionVolumeChildren
        Sub-factors associated with five-year production volumes
    """

    child_factors: LifelongProductionVolumesChildren = Field(
        title="child_factors",
        description="Child factor parameters associated with lifelong production volumes",
    )


class AnnualProductionVolumesChildren(SetOfFactors):
    """
    Object determines impact sub-factors associated
    with production volumes.

    Attributes
    ----------
    ann_gas_production : Factor
        Factor parameters for annual gas production volume

    ann_oil_production : Factor
        Factor parameters for annual oil production volume


    """

    ann_gas_production: Factor | None = None
    # = Field(
    #     title="ann_gas_production",
    #     description="Factor parameters for annual gas production volume"
    # )
    ann_oil_production: Factor | None = None
    # = Field(
    #     title="ann_oil_production",
    #     description="Factor parameters for annual oil production volume"
    # )


class AnnualProductionVolumes(SetOfFactors, Factor):
    """
    Object determines weights/selections associated with
    annual production volume related impact factors

    Attributes
    ----------
    child_factors : AnnualProductionVolumeChildren
        Sub-factors associated with annual production volumes
    """

    child_factors: AnnualProductionVolumesChildren = Field(
        title="child_factors",
        description="Child factor parameters associated with annual production volumes",
    )


class SiteConsiderationsChildren(SetOfFactors):
    """
    Object determines impact sub-factors associated
    with site considerations.

    Attributes
    ----------
    historical_preservation_site : Factor
        Factor parameters for historical preservation sites

    home_use_gas_well : Factor
        Factor parameters for home use gas wells

    post_plugging_land_use : Factor
        Factor parameters for post plugging land use

    proximity_to_geologic_faults : Factor
        Factor parameters for proximity to geologic faults

    surface_equipment_on_site : Factor
        Factor parameters for surface equipment on site


    """

    historical_preservation_site: Factor | None = None
    # = Field(
    #     title="historical_preservation_site",
    #     description="Factor parameters for historical preservation sites"
    # )
    home_use_gas_well: Factor | None = None
    # = Field(
    #     title="home_use_gas_well",
    #     description="Factor parameters for home use gas wells"
    # )
    post_plugging_land_use: Factor | None = None
    # = Field(
    #     title="post_plugging_land_use",
    #     description="Factor parameters for post plugging land use"
    # )
    # proximity_to_geologic_faults: Factor | None = None
    # # = Field(
    # #     title="proximity_to_geologic_faults",
    # #     description="Factor parameters for proximity to geologic faults"
    # # )
    surface_equipment_on_site: Factor | None = None
    # = Field(
    #     title="surface_equipment_on_site",
    #     description="Factor parameters for surface equipment on site"
    # )


class SiteConsiderations(SetOfFactors, Factor):
    """
    Object determines weights/selections associated with
    site considerations related impact factors

    Attributes
    ----------
    child_factors : SiteConsiderationsChildren
        Sub-factors associated with site considerations
    """

    child_factors: SiteConsiderationsChildren = Field(
        title="child_factors",
        description="Child factor parameters associated with site considerations",
    )


class ImpactFactors(SetOfFactors):
    """
    Object determines weights/selections associated with
    impact factor for scenario analysis

    Attributes
    ----------
    well_age : Factor
        Age of well as an impact factor

    h2s_leak : Factor
        H2s leak as an impact factor, child of OtherLosses
    losses : Losses
        Losses from well as an impact factor

    sensitive_receptors : SensitiveReceptors
        Sensitive receptors as an impact factor

    well_count : Factor
        Number of wells owned by an owner as an impact factor

    environment : Environment
        Environmental impact factors

    ecological_receptors : EcologicalReceptors
        Ecological receptor impact factors

    other_losses : OtherLosses
        Other losses (not hydrocarbons) impact factors

    lifelong_production_volume : LifelongProductionVolumes
        Impact factors for lifelong production

    five_year_production_volume : FiveYearProductionVolumes
        Impact factors for five-year production

    ann_production_volume : AnnualProductionVolumes
        Impact factors for annual production volumes

    site_considerations: SiteConsiderations
        Impact factors for site considerations

    cost_of_plugging : Factor
        Prioritize wells based on predicted cost to plug

    high_pressure_observed : Factor
        high pressure observed at a well

    idle_status_duration : Factor
        Well idle status duration

    in_tribal_land : Factor
        Impact factor for wells in tribal land

    likely_to_be_orphaned : Factor
        Impact factor for wells that are likely to be orphaned

    mechanical_integrity_test: Factor
        Impact factor for mechanical integrity test

    number_of_mcws_nearby : Factor
        Impact factor for number of mcws nearby

    otherwise_incentivized_well : Factor
        Impact factor for wells that are otherwise incentivized by states

    well_integrity : Factor
        Impact factor for well integrity
    """

    well_age: Factor = Field(
        title="well_age", description="Impact parameters associated with well age"
    )

    losses: Losses = Field(
        title="losses", description="Impact parameters associated with losses"
    )

    sensitive_receptors: SensitiveReceptors = Field(
        title="sensitive_receptors",
        description="Impact parameters associated with sensitive receptors",
    )
    owner_well_count: Factor = Field(
        title="owner_well_count",
        description="Impact parameters associated with number of wells owned by an owner",
    )
    # making this optional to support backwards compatibility
    lifetime_production_volumes: Factor | None = None
    environment: Environment = Field(
        title="environmental",
        description="Impact parameters associated with environment",
    )
    ecological_receptors: EcologicalReceptors | None = None
    # = Field(
    #     title="ecological_receptors",
    #     description="Impact factors associated with ecological receptors"
    # )
    other_losses: OtherLosses | None = None
    # = Field(
    #     title="other_losses",
    #     description="Losses impact factors other than hydrocarbons"
    # )
    lifelong_production_volume: LifelongProductionVolumes | None = None
    # = Field(
    #     title="five_year_production_volume",
    #     description="Impact factors for five-year production",
    # )
    five_year_production_volume: FiveYearProductionVolumes | None = None
    # = Field(
    #     title="five_year_production_volume",
    #     description="Impact factors for five-year production",
    # )
    ann_production_volume: AnnualProductionVolumes | None = None
    # = Field(
    #     title="ann_production_volume",
    #     description="Impact factors for annual production volumes",
    # )
    site_considerations: SiteConsiderations | None = None
    # = Field(
    #     title="site_considerations",
    #     description="Impact factors relating to site considerations",
    # )
    cost_of_plugging: Factor | None = None
    # = Field(
    #     title="cost_of_plugging",
    #     description="Prioritize wells based on predicted cost to plug",
    # )
    high_pressure_observed: Factor | None = None
    # = Field(
    #     title="high_pressure_observed",
    #     description="high pressure observed at a well",
    # )
    idle_status_duration: Factor | None = None
    # = Field(
    #     title="idle_status_duration",
    #     description="Well idle status duration",
    # )
    in_tribal_land: Factor | None = None
    # = Field(
    #     title="in_tribal_land",
    #     description="Impact factor for wells in tribal land",
    # )
    likely_to_be_orphaned: Factor | None = None
    # = Field(
    #     title="likely_to_be_orphaned",
    #     description="Impact factor for wells that are likely to be orphaned",
    # )
    number_of_mcws_nearby: Factor | None = None
    # = Field(
    #     title="number_of_mcws_nearby",
    #     description="Impact factor for number of mcws nearby",
    # )
    mechanical_integrity_test: Factor | None = None
    # = Field(
    #     title="mechanical_integrity_test",
    #     description="Impact factor for mechanical integrity test",
    # )

    otherwise_incentivized_well: Factor | None = None
    # = Field(
    #     title="otherwise_incentivized_well",
    #     description="Impact factor for wells that are otherwise incentivized by states",
    # )
    well_integrity: Factor | None = None
    # = Field(
    #     title="well_integrity",
    #     description="Impact factor for well integrity",
    # )
    placeholder_one: Factor | None = None
    # = Field(
    #     title="placeholder_1",
    #     description="Impact factor for placeholders",
    # )
    placeholder_two: Factor | None = None
    # = Field(
    #     title="placeholder_2",
    #     description="Impact factor for placeholders",
    # )
    placeholder_three: Factor | None = None
    # = Field(
    #     title="placeholder_3",
    #     description="Impact factor for placeholders",
    # )
    placeholder_four: Factor | None = None
    # = Field(
    #     title="placeholder_4",
    #     description="Impact factor for placeholders",
    # )
    placeholder_five: Factor | None = None
    # = Field(
    #     title="placeholder_5",
    #     description="Impact factor for placeholders",
    # )
    placeholder_six: Factor | None = None
    # = Field(
    #     title="placeholder_6",
    #     description="Impact factor for placeholders",
    # )
    placeholder_seven: Factor | None = None
    # = Field(
    #     title="placeholder_7",
    #     description="Impact factor for placeholders",
    # )
    placeholder_eight: Factor | None = None
    # = Field(
    #     title="placeholder_8",
    #     description="Impact factor for placeholders",
    # )
    placeholder_nine: Factor | None = None
    # = Field(
    #     title="placeholder_9",
    #     description="Impact factor for placeholders",
    # )
    placeholder_ten: Factor | None = None
    # = Field(
    #     title="placeholder_10",
    #     description="Impact factor for placeholders",
    # )
    placeholder_eleven: Factor | None = None
    # = Field(
    #     title="placeholder_11",
    #     description="Impact factor for placeholders",
    # )
    placeholder_twelve: Factor | None = None
    # = Field(
    #     title="placeholder_12",
    #     description="Impact factor for placeholders",
    # )
    placeholder_thirteen: Factor | None = None
    # = Field(
    #     title="placeholder_13",
    #     description="Impact factor for placeholders",
    # )
    placeholder_fourteen: Factor | None = None
    # = Field(
    #     title="placeholder_14",
    #     description="Impact factor for placeholders",
    # )
    placeholder_fifteen: Factor | None = None
    # = Field(
    #     title="placeholder_15",
    #     description="Impact factor for placeholders",
    # )
    placeholder_sixteen: Factor | None = None
    # = Field(
    #     title="placeholder_16",
    #     description="Impact factor for placeholders",
    # )
    placeholder_seventeen: Factor | None = None
    # = Field(
    #     title="placeholder_17",
    #     description="Impact factor for placeholders",
    # )
    placeholder_eighteen: Factor | None = None
    # = Field(
    #     title="placeholder_18",
    #     description="Impact factor for placeholders",
    # )
    placeholder_nineteen: Factor | None = None
    # = Field(
    #     title="placeholder_19",
    #     description="Impact factor for placeholders",
    # )
    placeholder_twenty: Factor | None = None
    # = Field(
    #     title="placeholder_20",
    #     description="Impact factor for placeholders",
    # )


class EfficiencyFactors(SetOfFactors):
    """
    Object determines weights/selections associated with
    efficiency factors for scenario analysis

    Attributes
    ----------
    avg_age : Factor
        Average age of wells in a project

    avg_depth : Factor
        Average depth of wells in a project

    age_range : Factor
        Range (max - min) of well age in a project

    distance_range : Factor
        Distance between farthest wells in a project

    num_wells : Factor
        Number of wells in a project

    depth_range : Factor
        Range (max - min) of depth in a project

    num_unique_owners : Factor
        Number of unique owners in a project

    avg_distance_to_nearest_road : Factor
        Average distance from nearest road for wells in project

    avg_elevation_change_from_nearest_road : Factor
        Average elevation change for well from nearest road point
    """

    # avg_age: Factor = Field(
    #     title="avg_age",
    #     description="Efficiency parameter associated with average age of wells in a project",
    # )
    # avg_depth: Factor = Field(
    #     title="avg_depth",
    #     description="Efficiency parameters associated with average depth of wells in a project",
    # )
    # num_unique_owners: Factor = Field(
    #     title="num_unique_owners",
    #     description=(
    #         "Efficiency parameters associated with number of "
    #         "unique well owners in a project"
    #     ),
    # )
    age_range: Factor = Field(
        title="age_range",
        description=(
            "Efficiency parameters associated with"
            " age range (oldest-youngest) in a project"
        ),
    )
    num_wells: Factor = Field(
        title="num_wells",
        description="Efficiency parameters associated with number of wells in a project",
    )
    depth_range: Factor = Field(
        title="depth_range",
        description=(
            "Efficiency parameters associated with depth range "
            "(deepest-shallowest) in a project"
        ),
    )
    distance_range: Factor = Field(
        title="distance_range",
        description=(
            "Efficiency parameters associated with"
            " distance range (farthest distance between two wells) in a project"
        ),
    )
    avg_distance_to_nearest_road: Factor = Field(
        title="avg_distance_to_nearest_road",
        description=(
            "Efficiency parameters associated with proximity of "
            "wells in a project to nearest road point"
        ),
    )
    avg_elevation_change_from_nearest_road: Factor = Field(
        title="avg_elevation_change_from_nearest_road",
        description=(
            "Efficiency parameters associated with elevation change "
            "to access wells from nearest road point"
        ),
    )
    population_density: Factor = Field(
        title="population_density",
        description=("Efficiency parameters associated with population density"),
    )


class GeneralSpecifications(BaseModel):
    """
    Object that defines program level requirements required to run scenario

    Attributes
    ----------
    name : str
        The name of the scenario

    budget : float
        The budget available

    well_type : List[str]
        The type of wells being considered

    dataset_id : int
        The id of the dataset being used

    organization_id : int
        The id of the organization for which scenario is being run

    additional_datasets : List[str]
        The id for additional datasets needed for running scenarios

    min_wells_in_project : int
        Minimum number of wells in a single project

    max_wells_in_project : int
        Maximum number of wells in a single project

    max_distance_between_project_wells : float
        The maximum allowable distance between two wells in a project in miles

    well_depth_limit : int
        The depth beyond which a well is considered deep

    max_wells_per_owner : int
        The maximum number of wells to be considered for plugging from a single owner

    min_lifetime_gas_production : int
        The minimum gas production (in MCF) to consider a well eligible for plugging

    max_lifetime_gas_production : int
        The maximum gas production (in MCF) to consider a well eligible for plugging

    min_lifetime_oil_production : int
        The minimum oil production (in Bbl) to consider a well eligible for plugging

    max_lifetime_oil_production : int
        The maximum oil production (in Bbl) to consider a well eligible for plugging

    shallow_gas_well_cost : int
        Cost of plugging a single shallow gas well

    deep_gas_well_cost : int
        Cost of plugging a single deep gas well

    shallow_oil_well_cost : int
        Cost of plugging a single shallow oil well

    deep_oil_well_cost : int
        Cost of plugging a single deep oil well

    cost_efficiency : float
        A factor that defines economies of scale when more than
        one well of a type are plugged

    basic_data_checks : bool
        Whether to carry out basic data checks

    handle_missing_depth : str
        How to handle wells with missing depth (specify a fixed value or just remove them)

    handle_missing_production : str
        How to handle wells with missing production (specify a fixed value or just remove them)

    handle_missing_type : str
        How to handle wells with missing well type info (specify a fixed value or just remove them)

    handle_missing_well_age : str
        How to handle wells with missing well age info (specify a fixed value or just remove them)

    specified_age : int
        Fixed age to assume for wells with missing age info.
        Only used if handle_missing_well_age is set to 'specify-value'

    specified_depth : int
        Fixed depth to assume for wells with missing depth info.
        Only used if handle_missing_depth is set to 'specify-value'

    specified_type : str
        Fixed type to assume for wells with missing type info.
        Only used if handle_missing_type is set to 'specify-value'

    specified_annual_gas_production : float
        Fixed annual_gas_production to assume for wells with missing type info.
        Only used if handle_missing_production is set to 'specify-value'

    specified_annual_oil_production : float
        Fixed annual_oil_production to assume for wells with missing type info.
        Only used if handle_missing_production is set to 'specify-value'

    specified_lifetime_gas_production : float
        Fixed lifetime_gas_production to assume for wells with missing type info.
        Only used if handle_missing_production is set to 'specify-value'

    specified_lifetime_oil_production : float
        Fixed lifetime_oil_production to assume for wells with missing type info.
        Only used if handle_missing_production is set to 'specify-value'
    solver_time : int
        The solution time allowed for optimization model (in seconds)

    absolute_gap : float
        The absolute solver gap allowed for termination

    relative_gap : float
        The relative solver gap allowed for termination

    model : str
        The type of optimization model to use

    use_lazy_constraints : Bool
        Whether use of lazy constraints is allowed

    """

    name: str = Field(title="name", description="The NAME of the scenario")
    budget: Optional[float] = Field(
        title="budget",
        description="The total budget available for plugging",
        ge=-1,
        default=-1,
    )
    well_type: List[Literal["Oil", "Gas"]] = Field(
        title="well_type",
        description="The well type to be considered for building projects",
    )
    dataset_id: int = Field(title="dataset_id", description="The dataset id to be used")
    organization_id: int = Field(
        title="organization_id", description="The organization id to be used"
    )
    additional_datasets: Optional[List[str]] = Field(
        title="additional_datasets",
        description="Additional data to be used",
        default=[],
    )

    min_wells_in_project: Optional[int] = Field(
        title="min_wells_in_project",
        description="Minimum number of wells required in a project",
        default=2,
        ge=1,
        le=100,
    )
    max_wells_in_project: Optional[int] = Field(
        title="max_wells_in_project",
        description="Maximum number of wells allowed in a project",
        default=30,
        ge=2,
    )

    # pylint: disable=inconsistent-return-statements
    @field_validator("max_wells_in_project", mode="after")
    @classmethod
    def validate_wells_in_project(cls, value: int, info: ValidationInfo) -> int:
        """
        Field validator for max_wells_in_project
        """
        if value is None:
            return

        if info.data["min_wells_in_project"] is None:
            return value

        return validate_max_value(
            value,
            info.data["min_wells_in_project"],
            "max_wells_in_project",
            "min_wells_in_project",
        )

    max_distance_between_project_wells: Optional[float] = Field(
        title="max_distance_between_project_wells",
        description="Maximum allowable distance (in miles) between two wells in the same project",
        default=10,
        ge=0,
        le=500,
    )

    well_depth_limit: Optional[int] = Field(
        title="well_depth_limit",
        description=(
            "The cutoff depth (in feet) for a well to be considered shallow. "
            "Wells larger in depth are considered 'deep'"
        ),
        default=4000,
        ge=0,
        le=50000,
    )

    max_wells_per_owner: Optional[int] = Field(
        title="max_wells_per_owner",
        description=(
            "The maximum number of wells from a single owner "
            "to be included in plugging projects"
        ),
        default=10000000,
        ge=0,
        le=10000000,
    )

    min_lifetime_gas_production: Optional[int] = Field(
        title="min_lifetime_gas_production",
        description=(
            "The minimum gas production over lifetime (in MCF) to consider a well"
            " eligible for plugging"
        ),
        default=None,
        ge=0,
        le=1000000,
    )

    max_lifetime_gas_production: Optional[int] = Field(
        title="max_lifetime_gas_production",
        description=(
            "The maximum gas production over lifetime (in MCF) to consider a well"
            " eligible for plugging"
        ),
        default=None,
        ge=0,
        le=1000000,
    )

    # pylint: disable=inconsistent-return-statements
    @field_validator("max_lifetime_gas_production", mode="after")
    @classmethod
    def validate_lifetime_gas_prod(cls, value: int, info: ValidationInfo) -> int:
        """
        Field validator for max_lifetime_gas_production
        """
        if value is None:
            return

        if info.data["min_lifetime_gas_production"] is None:
            return value

        return validate_max_value(
            value,
            info.data["min_lifetime_gas_production"],
            "max_lifetime_gas_production",
            "min_lifetime_gas_production",
        )

    min_lifetime_oil_production: Optional[int] = Field(
        title="min_lifetime_oil_production",
        description=(
            "The minimum gas production over lifetime (in Bbl) to consider a well"
            " eligible for plugging"
        ),
        default=None,
        ge=0,
        le=100000000,
    )

    max_lifetime_oil_production: Optional[int] = Field(
        title="max_lifetime_oil_production",
        description=(
            "The maximum oil production over lifetime (in Bbl) to consider a well"
            " eligible for plugging"
        ),
        default=None,
        ge=0,
        le=1000000000,
    )

    # pylint: disable=inconsistent-return-statements
    @field_validator("max_lifetime_oil_production", mode="after")
    @classmethod
    def validate_lifetime_oil_prod(cls, value: int, info: ValidationInfo) -> int:
        """
        Field validator for max_lifetime_oil_production
        """
        if value is None:
            return

        if info.data["min_lifetime_oil_production"] is None:
            return value
        return validate_max_value(
            value,
            info.data["min_lifetime_oil_production"],
            "max_lifetime_oil_production",
            "min_lifetime_oil_production",
        )

    shallow_gas_well_cost: Optional[int] = Field(
        title="single_shallow_gas_well_cost",
        description="Cost of plugging a single shallow gas well in $",
        ge=0,
        default=60000,
    )
    deep_gas_well_cost: Optional[int] = Field(
        title="single_deep_gas_well_cost",
        description="Cost of plugging a single deep gas well in $",
        ge=0,
        default=60000,
    )
    shallow_oil_well_cost: Optional[int] = Field(
        title="single_shallow_oil_well_cost",
        description="Cost of plugging a single shallow oil well in $",
        ge=0,
        default=60000,
    )
    deep_oil_well_cost: Optional[int] = Field(
        title="single_deep_oil_well_cost",
        description="Cost of plugging a single deep oil well in $",
        ge=0,
        default=60000,
    )
    cost_efficiency: Optional[float] = Field(
        title="beta",
        description=(
            "Parameter that defines economies of scale " "when plugging multiple wells"
        ),
        ge=0,
        lt=1,
        default=0.9,
    )
    basic_data_checks: Optional[bool] = Field(
        title="basic_data_checks",
        description="Whether to carry out basic data checks",
        default=True,
    )

    handle_missing_depth: Literal["specify-value", "remove-wells"] = Field(
        title="handle_missing_depth",
        description="How to handle wells with missing depth info",
    )

    handle_missing_production: Literal["specify-value", "remove-wells"] = Field(
        title="handle_missing_production",
        description="How to handle wells with missing depth info",
    )

    handle_missing_type: Literal["specify-value", "remove-wells"] = Field(
        title="handle_missing_type",
        description="How to handle wells with missing well type info",
    )

    handle_missing_well_age: Literal["specify-value", "remove-wells"] = Field(
        title="handle_missing_well_age",
        description="How to handle wells with missing well age info",
    )

    specified_age: Optional[int] = Field(
        title="specified_age",
        description="The fixed age to assume for wells with missing age info",
        ge=0,
        le=300,
        default=0,
    )

    specified_depth: Optional[int] = Field(
        title="specified_depth",
        description="The fixed depth to assume for wells with missing depth info",
        ge=0,
        le=20000,
        default=4000,
    )

    specified_type: Optional[Literal["oil", "gas"]] = Field(
        title="specified_type",
        description="The fixed well type to assume for wells with missing type info",
        default="oil",
    )

    specified_annual_gas_production: Optional[float] = Field(
        title="specified_annual_gas_production",
        description=(
            "The fixed annual gas production to assume for wells with "
            "missing gas production info"
        ),
        ge=0,
        default=0,
    )

    specified_annual_oil_production: Optional[float] = Field(
        title="specified_annual_oil_production",
        description=(
            "The fixed annual oil production to assume for wells with "
            "missing oil production info"
        ),
        ge=0,
        default=0,
    )

    specified_lifetime_gas_production: Optional[float] = Field(
        title="specified_lifetime_gas_production",
        description=(
            "The fixed lifetime gas production to assume "
            "for wells with missing gas production info"
        ),
        ge=0,
        default=0,
    )

    specified_lifetime_oil_production: Optional[float] = Field(
        title="specified_lifetime_oil_production",
        description=(
            "The fixed lifetime oil production to assume "
            "for wells with missing oil production info"
        ),
        ge=0,
        default=0,
    )
    solver_time: Optional[int] = Field(
        title="solver_time",
        description="The solution time (in seconds) allowed for optimization model",
        default=3600,
        ge=0,
    )

    absolute_gap: Optional[float] = Field(
        title="absolute_gap",
        description="The absolute gap allowed for optimization solver for termination",
        ge=0,
        le=1000000,
        default=1,
    )

    relative_gap: Optional[float] = Field(
        title="relative_gap",
        description="The relative gap allowed for termination",
        ge=0,
        le=1,
        default=0.05,
    )

    model: Optional[Literal["impact", "impact-and-efficiency"]] = Field(
        title="model",
        description="The optimization model type to be used",
        default="impact-and-efficiency",
    )

    use_lazy_constraints: Optional[bool] = Field(
        title="use_lazy_constraints",
        description="Whether to use Lazy Constraints with optimization model",
        default=False,
    )

    # pylint: disable=unsubscriptable-object
    @field_validator(
        "budget",
        "min_wells_in_project",
        "max_wells_in_project",
        "max_distance_between_project_wells",
        "well_depth_limit",
        "max_wells_per_owner",
        "min_lifetime_gas_production",
        "max_lifetime_gas_production",
        "min_lifetime_oil_production",
        "max_lifetime_oil_production",
        "shallow_gas_well_cost",
        "deep_gas_well_cost",
        "shallow_oil_well_cost",
        "deep_oil_well_cost",
        "cost_efficiency",
        "basic_data_checks",
        "specified_type",
        "specified_annual_gas_production",
        "specified_annual_oil_production",
        "specified_lifetime_gas_production",
        "specified_lifetime_oil_production",
        "specified_age",
        "specified_depth",
        "solver_time",
        "absolute_gap",
        "relative_gap",
        "model",
        "use_lazy_constraints",
        mode="before",
    )
    @classmethod
    def replace_null_with_default(cls, value, ctx):
        """
        Validator to replace null entries with the
        default value
        """
        filter_methods = [
            "min_lifetime_gas_production",
            "max_lifetime_gas_production",
            "min_lifetime_oil_production",
            "max_lifetime_oil_production",
        ]

        if value is None and ctx.field_name not in filter_methods:
            return cls.__fields__[ctx.field_name].default
        return value


class UseCases(BaseModel):
    """
    Object defining a the Use Cases

    Attributes
    ----------
    cases: the types of use cases for scenarios
    """

    cases: List[
        Literal[
            "Well Ranking", "P&A Project Recommendations", "P&A Project Comparisons"
        ]
    ] = Field(
        title="PRIMO Use Cases",
        description="PRIMO Use Cases",
    )


class RankWellsParameters(SetOfFactors):
    """
    Object defines the parameters required for running a rank wells operation

    Attributes
    ----------
    impact_factors : ImpactFactors
        The scenario parameter selections for impact factors

    efficiency_factors : EfficiencyFactors
        The scenario parameter selections for efficiency factors

    general_specifications : GeneralSpecifications
        The scenario parameter selections associated with overall program requirements

    """

    impact_factors: Optional[ImpactFactors] = Field(
        title="impact_factors",
        description="Scenario specifications for impact factors",
        default=ImpactFactors.model_validate(IMPACT_FACTORS),
    )
    efficiency_factors: Optional[EfficiencyFactors] = Field(
        title="efficiency_factors",
        description="Scenario specifications for efficiency factors",
        default=EfficiencyFactors.model_validate(EFFICIENCY_FACTORS),
    )
    general_specifications: GeneralSpecifications = Field(
        title="general_specifications",
        description="Scenario specifications for overall program requirements",
    )
    use_cases: Optional[UseCases] = Field(
        title="Use Cases",
        description="PRIMO Use Cases",
        default=UseCases.model_validate(
            {"cases": ["Well Ranking", "P&A Project Recommendations"]}
        ),
    )
    # pylint: disable=unsubscriptable-object
    @classmethod
    def replace_null_with_default(cls, value, ctx):
        """
        Validator to replace null entries with the
        default value
        """
        if value is None:
            return cls.__fields__[ctx.field_name].default
        return value


class ScenarioParameters(RankWellsParameters):
    """
    Object defines the parameters required for running a scenario

    Attributes
    ----------
    scenario_id : str
        The name of the scenario
    """

    scenario_id: int = Field(title="scenario_id", description="id for the scenario")


class ManualOverrideRequest(RankWellsParameters):
    """
    Object defines the request from the front end for executing a manual override

    Attributes
    ----------
    scenario_id : str
        The name of the scenario

    parent_project_ids : List[int]
        A list of project_ids corresponding to the parent scenario

    projects_remove : List[int]
        A list of project ids to manually remove

    wells_remove : dict[int: List[int]]
        A dictionary of project id : [well_ids] that provides all information
            for wells to manually remove

    projects_lock : List[int]
        A list of project ids to manually lock

    wells_lock : dict[int: List[int]]
        A dictionary of project id : [well_ids] that provides all information
            for wells to manually lock

    wells_reassign_from : dict[int: List[int]]
        A dictionary of project id : [well_ids] that provides all information
            for wells that are manually reassigned from projects

    wells_reassign_to : dict[int: List[int]]
        A dictionary of project id : [well_ids] that provides all information
            for wells that are manually reassigned to projects
    """

    scenario_id: int = Field(title="scenario_id", description="id for the scenario")
    parent_project_ids: List[int] = Field(
        title="parent_projects",
        description="Project ids for the all the projects of the parent scenario",
    )
    child_scenario_id: int = Field(
        title="child_scenario", description="manual override child scenario id"
    )
    projects_remove: List[int] = Field(
        title="projects", description="projects to manually remove"
    )
    wells_remove: Dict[int, List[int]] = Field(
        title="wells dictionary",
        description="wells to manually remove and their associated projects",
    )
    projects_lock: List[int] = Field(
        title="projects", description="projects to manually lock"
    )
    wells_lock: Dict[int, List[int]] = Field(
        title="wells dictionary",
        description="wells to manually lock and their associated projects",
    )
    wells_reassign_from: Dict[Union[int, str], List[int]] = Field(
        title="wells dictionary",
        description="wells to manually add and their associated current projects",
    )
    wells_reassign_to: Dict[int, List[int]] = Field(
        title="wells dictionary",
        description="wells to manually add and their associated future projects",
    )


class ValidateDataRequest(BaseModel):
    """
    Object defines the request from the front end for validating data

    Attributes
    ----------
    file_path: str
        File path for the data file

    dataset_id : int
        Id for the dataset
    """

    file_path: FilePath = Field(title="file_path", description="path to data file")
    dataset_id: int = Field(
        title="dataset_id",
        description="dataset id corresponding to the data at the file path",
    )


class KPISummaryRequest(ScenarioParameters):
    """
    Object defines the request for summarizing a scenario

    Attributes
    ----------
    project_ids: List[int]
        List of ids corresponding to project ids in the database
    """

    project_ids: List[int] = Field(
        title="project ids",
        description="Project ids for the all the projects of the scenario",
    )


class OverrideReoptimizationCheckRequest(ManualOverrideRequest):
    """
    Object defines the request for constraints violation information of the
    override re-optimization

    Attributes
    ----------
    re_optimized_project_ids: List[int]
        List of ids corresponding to project ids in the database
    """

    re_optimized_project_ids: List[int] = Field(
        title="project ids",
        description="Project ids for the all the projects of the scenario",
    )


class DataAvailCheckResults(PrimoResponse):
    """
    Object defining a response schema for checking available data
    API calls

    Attributes
    ----------
    impact_factors : Dict[str,Union[dict,None]]
        The dictionary containing the data necessary to determine
        whether the user can use each of the available impact
        factors

    efficiency_factors : Dict[str,Union[dict,None]]
        The dictionary containing the data necessary to determine
        whether the user can use each of the available efficiency
        factors
    """

    impact_factors: Dict[str, dict] = Field(
        title="Impact Factors",
        description="The data with the available metrics that can be selected",
    )

    efficiency_factors: Dict[str, dict] = Field(
        title="efficiency factors",
        description="The data with the available metrics that can be selected",
    )
