Optimization Model for Efficient P&A Campaigns
================================================

Overview
--------

Given a set of marginal wells, an overall budget, and a radius that constitutes an efficient project, the optimization model returns candidates for high efficiency P&A projects.


.. _mathematical_program_formulation:

Impact-only Optimization Model
==============================

The following sets are defined for the Impact-only optimization model.

.. _sets_table:
.. list-table:: **Sets**
   :widths: 25 75
   :header-rows: 1

   * - Symbol
     - Description
   * - :math:`\mathcal{W}`
     - Set of all wells under consideration.
   * - :math:`\mathcal{C}`
     - Set of all clusters.
   * - :math:`\mathcal{WP_c}, \forall c \in \mathcal{C}`
     - Set of all well pairs that belong to cluster :math:`\mathit{c}`.
   * - :math:`\mathcal{W}_c \subseteq \mathcal{W},\, \forall c \in \mathcal{C}`
     - Set of wells that belong to cluster :math:`\mathit{c}`.
   * - :math:`\mathcal{W}^\text{dac} \subseteq \mathcal{W}`
     - Set of wells in disadvantaged communities.

The following parameters are defined for the Impact-only optimization model.

.. list-table:: **Parameters**
   :widths: 25 75
   :header-rows: 1

   * - Symbol
     - Description
   * - :math:`\text{B}`
     - Total budget available for the plugging campaign.
   * - :math:`\text{P}_{cw}`
     - Impact score assigned to each well :math:`\mathit{w}` in cluster :math:`\mathit{c}`.
   * - :math:`\text{M}_n`
     - Cost of plugging a project assuming the project has :math:`\mathit{n}` wells.
   * - :math:`\text{NW}_\text{max}`
     - Maximum number of wells to be chosen in a project.
   * - :math:`\text{NW}_\text{min}`
     - Minimum number of wells to be chosen in a project.
   * - :math:`\text{DAC}_\text{min}`
     - Minimum percentage of wells chosen to be from disadvantaged communities across all projects

The following variables are defined for the Impact-only optimization model.

.. list-table:: **Binary Variables**
   :widths: 25 75
   :header-rows: 1

   * - Symbol
     - Description
   * - :math:`\mathit{SW_{cw}}`
     - 1, if well :math:`\mathit{w}` is chosen in cluster :math:`\mathit{c}`.
   * - :math:`\mathit{SC_c}`
     - 1, if wells in cluster :math:`\mathit{c}` are chosen; 0, otherwise.
   * - :math:`\mathit{NW_cn}`
     - Binary variables to track the number of wells :math:`\mathit{n}` in cluster :math:`\mathit{c}`.


.. list-table:: **Continuous Variables**
   :widths: 25 75
   :header-rows: 1

   * - Symbol
     - Description
   * - :math:`\mathit{PC_c}`
     - Total cost of plugging all wells in a project in cluster :math:`\mathit{c}`.
   * - :math:`\mathit{TW_c}`
     - Total number of wells chosen in a project in cluster :math:`\mathit{c}`.
   * - :math:`\mathit{\eta_c}^\text{impact}`
     - Impact score of the project in cluster :math:`\mathit{c}`.
   * - :math:`\mathit{\eta_c}^\text{efficiency}`
     - Efficiency score of the project in cluster :math:`\mathit{c}`.
   * - :math:`\mathit{\eta_c}^\text{e}`
     - Efficiency score of the project in cluster :math:`\mathit{c}` for the metric e in set :math:`\mathcal{E}`.
   * - :math:`\mathit{TW_c}^\text{dac}`
     - Total number of wells chosen in disadvantaged communities from each cluster :math:`\mathit{c}`.


The objective function maximizes impact derived through the P&A projects. The impact is computed
through a weighted sum of all the priorities under consideration weighted with their relative importance. 
The optimization model is as follows.



**Objective**

.. math::

   \max \sum_{c \in \mathcal{C}} \mathit{\eta_c}^\text{impact}

**Explanation**: The objective of the model is to maximize the impact by summing the priority scores of all wells selected in a project across all clusters.

.. math::

   \sum_{w \in \mathcal{W}_c} SW_{cw} = TW_c, \quad \forall \, c \in \mathcal{C}

**Explanation**: This constraint computes the number of wells chosen in cluster :math:`\mathit{c}`.

.. math::

   {TW_c} = \sum_{n = 1}^{|\mathcal{W}_c|} n \cdot {NW_{cn}}, \quad \forall \, c \in \mathcal{C}

**Explanation**: This constraint updates variable :math:`\mathit{TW}_{c}` to be equal to the number of wells chosen in cluster :math:`\mathit{c}`.

.. math::

   {SC_c} = \sum_{n = 1}^{|\mathcal{W}_c|} {NW_{cn}}, \quad \forall \, c \in \mathcal{C}

**Explanation**: This constraint ensures at most one :math:`\mathit{NW}_{cn}` is selected.

.. math::

   \sum_{n = 1}^{|\mathcal{W}_c|} \text{M}_n \cdot {NW_{cn}} = {PC_c}, \quad \forall \, c \in \mathcal{C}

**Explanation**: This constraint computes the cost of the project.

.. math::

   \sum_{c \in \mathcal{C}} {PC_c} \le \text{B}

**Explanation**: This constraint is the total budget constraint.

.. math::

   \eta^\text{impact} = \sum_{c \in \mathcal{C}} \sum_{w \in \mathcal{W}} \text{P}_{cw} \cdot {SW_{cw}}

**Explanation**: This constraint computes the total impact score of all projects, which is then maximized in the objective function.

.. math::

   {SC_c} \cdot \text{NW}_{\min} \leq {\mathit{TW}_c}, \quad \forall \, c \in \mathcal{C}

**Explanation**: This optional constraint sets the lower bound on the number of wells selected in a project if the cluster :math:`\mathit{c}` is selected.

.. math::

   {SC_c} \cdot \text{NW}_{\max} \geq {\mathit{TW}_c}, \quad \forall \, c \in \mathcal{C}

**Explanation**: This optional constraint sets the upper bound on the number of wells selected in a project if the cluster :math:`\mathit{c}` is selected.

.. math::

   \sum_{w \in \mathcal{W}^\text{dac}} SW_{cw} \ge {TW_c^\text{dac}}, \quad \forall \, c \in \mathcal{C}

**Explanation**: This optional constraint ensures a specific number of wells in cluster :math:`\mathit{c}` are selected from disadvantaged communities. This constraint is only added if the user selects the option for a minimum number of wells to be selected from DAC regions.

.. math::

   \sum_{c \in \mathcal{C}}{{TW_c^\text{dac}}} \geq \frac{\text{DAC}_\text{min}}{100} \cdot \sum_{c \in \mathcal{C}} {{TW_c}}

**Explanation**: This optional constraint ensures that a percentage of the wells selected across all projects are in disadvantaged communities.

Note that the efficiency score for each project is calculated based on the optimization solution obtained after solving the optimization problem.
For details, see the :ref:`project-efficiency-score` section under Methods for more details.

Impact & Efficiency Optimization Model
======================================

PRIMO allows users to not only opt for high-impact projects but also high-efficiency projects. In this model, the objective of the optimization model is updated as follows:

.. math::

   \sum_{c \in \mathcal{C}} \left( \zeta^\text{impact} \cdot \mathit{\eta_c}^\text{impact} + \zeta^\text{efficiency} \cdot \mathit{\eta_c}^\text{efficiency} \right)

The weight assigned to impact and efficiency is user-defined in the codebase.

The following efficiency metrics are supported in PRIMO.

.. table:: 
    :class: longtable

    ===========================  ======================================================================
    **Name of the Metric**       **Description**
    ===========================  ======================================================================
    **Age Range**                The difference between the maximum and minimum ages of wells within
                                 each project cluster. Projects with wells of similar ages are more 
                                 efficient for plugging.
    ---------------------------  ----------------------------------------------------------------------
    **Depth Range**              The difference between the maximum and minimum depths of wells
                                 within the project. Projects with wells of similar depths are more 
                                 efficient for plugging.
    ---------------------------  ----------------------------------------------------------------------
    **Distance Range**           The maximum distance between a pair of wells
                                 within the project. Projects with wells in close proximity are more 
                                 efficient for plugging.
    ---------------------------  ----------------------------------------------------------------------
    **Number of Wells**          The total number of wells associated with each project. A larger
                                 number of wells in a project can reduce the average cost to plug a
                                 well due to economies of scale.
    ---------------------------  ----------------------------------------------------------------------
    **Number of Unique Owners**  The total number of unique well owenrs whose wells are selected with 
                                 each project. Fewer number of owners in a project can reduce effort
                                 from a project management point of view which enhances efficiency.
    ---------------------------  ----------------------------------------------------------------------
    **Elevation Delta**          The maximum absolute elevation delta across all wells within
                                 the project group. The elevation delta is the difference in
                                 surface elevation between the well and the nearest road point.
                                 Low elevation deltas means projects with more accessible wells,
                                 which enhances plugging efficiency.
    ---------------------------  ----------------------------------------------------------------------
    **Distance to Road**         The maximum absolute distance from well locations to their
                                 nearest road point. This metric quantifies well accessibility,
                                 as constructing service roads to well sites can be a significant
                                 part of the plugging cost. Having wells close to roads can reduce
                                 plugging cost which enhances plugging efficiency.
    ---------------------------  ----------------------------------------------------------------------
    **Population Density**       The maximum population density of all wells in a project. Wells in
                                 lower populated areas can lead to a increase in efficiency due
                                 to easy access.
    ---------------------------  ----------------------------------------------------------------------
    **Record Completeness**      The number of data columns with missing values for a well selected in 
                                 a project. Wells with complete records/data can help avoid a lot of 
                                 uncertainty in a project enhancing efficiency.
    ===========================  ======================================================================


We have 2 formulations to include efficiency in the optimization model: The max scaling formulation and zone formulation.

The following sets are defined in addition to the sets in the Impact-only optimization model. These sets are only defined if the weight of efficiency in the objective is non-zero.

.. _eff_sets_table:
.. list-table:: **Sets**
   :widths: 25 75
   :header-rows: 1

   * - Symbol
     - Description
   * - :math:`\mathcal{E}`
     - Set of all efficiency metrics.
   * - :math:`\mathcal{E}^\text{wb} \subseteq \mathcal{E}`
     - Set of well-based efficiency metrics. These include population density, record completeness, elevation delta, distance to nearest road.
   * - :math:`\mathcal{E}^\text{wp} \subseteq \mathcal{E}`
     - Set of well-pair efficiency metrics. These include age range, depth range, distance range.
   * - :math:`\mathcal{O}_c`
     - Set of unique owners in cluster :math:`\mathit{c}`. 

The following parameters are defined in addition to the parameters in the impact-only optimization model. These parameters are only defined if the weight of efficiency in the objective is non-zero.

.. table:: **Parameters**
   :name: tab-par-def
   :widths: auto

   ============================================ =============================================================================  
   Parameter                                    Definition  
   ============================================ =============================================================================  
   :math:`\zeta^{\text{impact}}`                Weight of impact in the objective function  
   :math:`\zeta^{\text{efficiency}}`            Weight of efficiency in the objective function  
   :math:`\zeta^{\text{e}}`                     Weight of efficiency metric e  
   :math:`\text{e}_{w_1w_2}`                        The value of efficiency metric e of well :math:`\mathit{w_1}` and well :math:`\mathit{w_2}` for all e :math:`\subseteq \mathcal{E}^\text{wp}` 
   :math:`\text{e}_{w}`                         The value of efficiency metric e of well :math:`\mathit{w}` for all e :math:`\subseteq \mathcal{E}^\text{wb}`  
   :math:`\text{e}_{\text{max}}`                The maximum value of efficiency metric e of any well :math:`\mathit{w}` in a project for all e :math:`\subseteq \mathcal{E}` 
   :math:`\text{own}_\text{max}`                Maximum number of unique owners in a project
   ============================================ =============================================================================

The following variables were defined in addition to the variables in the impact only model. These variables are only defined if the weight of efficiency in the objective is non-zero and the weight of the corresponding efficiency metric is non-zero.

.. table:: **Variables**
   :name: tab-var-def
   :widths: auto

   ============================================ =============================================================================
   Variable                                     Definition
   ============================================ =============================================================================
   :math:`\mathit{\eta_c}^\text{efficiency}`    Efficiency score of cluster :math:`\mathit{c}`
   :math:`\mathit{\eta_c}^\text{e}`             Efficiency score for the efficiency metric, e, in cluster :math:`\mathit{c}`
   :math:`\mathit{\eta_c}^\text{nw}`            Efficiency score for the efficiency metric number of wells in cluster :math:`\mathit{c}`
   :math:`\mathit{\eta_c}^\text{own}`           Efficiency score for the efficiency metric number of unique owners in cluster :math:`\mathit{c}`
   :math:`\mathit{SO_{oc}}`                     Binary Variable to track if an owner, :math:`\mathit{o}`, has a well selected in a project in cluster :math:`\mathit{c}`
   :math:`\mathit{NO_c}`                        Variable to keep track of total number of unique owners with at least 1 well in cluster :math:`\mathit{c}` selected in a project 
   ============================================ =============================================================================


Max Scaling Formulation
=======================

In this formulation, the efficiency metrics are computed in the following constraints:

.. math::

   \eta_c^\text{nw} = \zeta^\text{nw} \cdot \left( \frac{\sum_{w \in \mathcal{W}_c} {SW}_{cw}}{\text{NW}_{\text{max}}} \right), \quad \forall c \in \mathcal{C}

.. math::

   \eta_c^\text{e} = \zeta^\text{e} \cdot \left( {SC}_c - \frac{\max_{(w_1, w_2) \in \mathcal{WP_c}} \{ \text{e}_{w_1w_2} \cdot {SW}_{cw_1} \cdot {SW}_{cw_2} \}}{\text{e}_{\text{max}}} \right), \quad \forall c \in \mathcal{C} \quad \forall \text{e} \in \mathcal{E}^\text{wp}

.. math::

   \eta_c^\text{e} = \zeta^\text{e} \cdot \left( {SC}_c - \frac{\max_{w \in \mathcal{W}_c} \{ \text{e}_{w} \cdot {SW}_{cw} \}} {\text{e}_{\text{max}}} \right), \quad \forall c \in \mathcal{C} \quad \forall \text{e} \in \mathcal{E}^\text{wb}

.. math::

   SW_{cw} \leq SO_{[owner(\mathit{w})]c}, \quad \forall c \in \mathcal{C}, 
   
where the function owner(:math:`\mathit{w}`) returns the well owner for well :math:`\mathit{w}`

.. math::

   NO_c = \sum_{o \in \mathcal{O}_c}{} {SO_{oc}}, \quad \forall c \in \mathcal{C}

.. math::

   \eta_c^\text{own} \leq SC_c - \frac{NO_c - SC_c}{\text{own}_{\text{max}} - 1}, \quad \forall c \in \mathcal{C}

.. math::

   \mathit{\eta_c}^\text{efficiency} = \sum_{\text{e} \in \mathcal{E}} \eta_c^\text{e}, \quad \forall c \in \mathcal{C}

The constraints shown above compute the efficiency score for each metric in set :math:`\mathcal{E}` and computes the total efficiency score of all projects, which is then maximized in the objective function of the optimization model.

Linearization of Efficiency Metrics Constraints
-----------------------------------------------

The constraints to compute the efficiency score for each metric can be linearized. The following example considers the age range metric.

.. math::

   \eta_c^\text{e} = \zeta^\text{e} \cdot \left( {SC}_c - \frac{\max_{(w_1, w_2) \in \mathcal{WP_c}} \{ \text{e}_{w_1w_2} \cdot {SW}_{cw_1} \cdot {SW}_{cw_2} \}}{\text{e}_{\text{max}}} \right), \quad \forall c \in \mathcal{C} \quad \forall \text{e} \in \mathcal{E}^\text{wp}

The linearized version of the above constraint is:

.. math::

   \eta_c^\text{e} \le \zeta^\text{e} \cdot \left( {SC}_c - \frac{\max_{(w_1, w_2) \in \mathcal{WP_c}} \{ \text{e}_{w_1w_2} \cdot {SW}_{cw_1} \cdot {SW}_{cw_2} \}}{\text{e}_{\text{max}}} \right), \quad \forall c \in \mathcal{C} \quad \forall \text{e} \in \mathcal{E}^\text{wp}

.. math::

   {SC}_c - \frac{\eta_c^\text{e}}{\zeta^\text{e}} \ge \frac{\max_{(w_1, w_2) \in \mathcal{WP_c}} \{ \text{e}_{w_1w_2} \cdot {SW}_{cw_1} \cdot {SW}_{cw_2} \}}{\text{e}_{\text{max}}}, \quad \forall c \in \mathcal{C} \quad \forall \text{e} \in \mathcal{E}^\text{wp}

.. math::

   {SC}_c - \frac{\eta_c^\text{e}}{\zeta^\text{e}} \ge \max_{(w_1, w_2) \in \mathcal{WP_c}} \biggl\{ \frac{\text{e}_{w_1w_2}}{\text{e}_{\text{max}}} \cdot {SW}_{cw_1} \cdot {SW}_{cw_2} \biggr\}, \quad \forall c \in \mathcal{C} \quad \forall \text{e} \in \mathcal{E}^\text{wp}

.. math::

   {SC}_c - \frac{\eta_c^\text{e}}{\zeta^\text{e}} \ge \max_{(w_1, w_2) \in \mathcal{WP_c}} \biggl\{ \frac{\text{e}_{w_1w_2}}{\text{e}_{\text{max}}} \cdot ({SW}_{cw_1} + {SW}_{cw_2} - {SC}_c) \biggr\}, \quad \forall c \in \mathcal{C} \quad \forall \text{e} \in \mathcal{E}^\text{wp}

.. math::

   {SC}_c - \frac{\eta_c^\text{e}}{\zeta^\text{e}} \ge \frac{\text{e}_{w_1w_2}}{\text{e}_{\text{max}}} \cdot ({SW}_{cw_1} + {SW}_{cw_2} - {SC}_c), \quad \forall (w_1, w_2) \in \mathcal{WP_c}, \quad \forall c \in \mathcal{C} \quad \forall \text{e} \in \mathcal{E}^\text{wp}

The linearization technique used above can be extended to all efficiency metrics using similar methods.

.. Zone Formulation
.. ================

.. Given one pairwise matrix representing the distance range, the goal is to convert this metric into zones based on specific value ranges. The following steps outline the process for the distance matrix, with similar logic applicable to the age and depth range matrices.

.. We define zones for the pairwise distances. Let :math:`\text{dist}_{ij}` represent the pairwise distance between points :math:`i` and :math:`j` in the distance matrix. The zone values are defined based on the distance range as follows:

.. .. math::

..    Z_{ij}^{\text{dist}} =
..    \begin{cases} 
..    1 & \text{if } 0 \leq \text{dist}_{ij} \leq 2 \text{ miles} \\
..    0.75 & \text{if } 2 < \text{dist}_{ij} \leq 3 \text{ miles} \\
..    0.50 & \text{if } 3 < \text{dist}_{ij} \leq 6 \text{ miles} \\
..    0.25 & \text{if } 6 < \text{dist}_{ij} \leq 8 \text{ miles} \\
..    0  & \text{otherwise}
..    \end{cases}

.. Similar rules can be applied to the pairwise age range matrix :math:`\text{age}_{ij}` and the pairwise depth range matrix :math:`\text{depth}_{ij}`. Define the zone values for each matrix based on the relevant range criteria for age and depth.

.. Formulating Efficiency Constraints
.. ----------------------------------

.. Let :math:`Y^\text{dist}_{cz} \in \{0, 1\}` be a variable that indicates whether well pairs in cluster :math:`c` in distance zone :math:`\mathit{z}` are allowed to be chosen. If :math:`Y^\text{dist}_{cz} = 1`, then well pairs within zone :math:`\mathit{z}` can be selected; otherwise, they are not considered.

.. .. math::

..    \eta^\text{dist} = \zeta^\text{dist} \cdot \left(1 - 0.25 \cdot Y^\text{dist}_{c2} - 0.25 \cdot Y^\text{dist}_{c3} - 0.25 \cdot Y^\text{dist}_{c4} - 0.25 \cdot Y^\text{dist}_{c5}\right), \quad \forall c \in \mathcal{C}

.. The relationship between the zone variables is given by:

.. .. math::

..    Y^\text{dist}_{c5} \le Y^\text{dist}_{c4} \le Y^\text{dist}_{c3} \le Y^\text{dist}_{c2} \le {SC}_c, \quad \forall c \in \mathcal{C}

.. Let :math:`\mathcal{WP_c}^z = \{(w_1, w_2) \in \text{comb}(\mathcal{S}_c) \mid (w_1, w_2) \in \text{zone} \mathit{z}\}` denote the set of well pairs in cluster :math:`\mathit{c}` that are in zone :math:`\mathit{z}`. The corresponding constraint is:

.. .. math::

..    {SW}_{cw_1} + {SW}_{cw_2} \le {SC}_c + Y^\text{dist}_{cz}, \quad \forall \; (w_1, w_2) \in \mathcal{WP_c}^z, \; z = \{2, \dots, 5\}, \quad \forall c \in \mathcal{C}

.. Zones Formulation for Extended Efficiency Metrics
.. -------------------------------------------------

.. The zone formulation can be extended to other efficiency metrics, such as population density, elevation delta, distance to road, and elevation delta. The following example illustrates the elevation delta metric, which can be implemented in a similar way to the other metrics.

.. The efficiency metric for elevation delta is defined as:

.. .. math::

..    \eta^\text{elev} = \zeta^\text{elev} \cdot \left(1 - 0.25 \cdot Y^\text{elev}_{c2} - 0.25 \cdot Y^\text{elev}_{c3} - 0.25 \cdot Y^\text{elev}_{c4} - 0.25 \cdot Y^\text{elev}_{c5}\right), \quad \forall c \in \mathcal{C}

.. The relationship between the zone variables for elevation delta is given by:

.. .. math::

..    Y^\text{elev}_{c5} \le Y^\text{elev}_{c4} \le Y^\text{dist}_{c3} \le Y^\text{elev}_{c2} \le {SC}_c, \quad \forall c \in \mathcal{C}

.. Let :math:`\mathcal{W}_z` denote the set of wells in zone :math:`\mathit{z}`. The corresponding constraint for elevation delta is:

.. .. math::

..    {SW}_{cw} \le Y^\text{elev}_{cz}, \quad \forall \; w \in \mathcal{W}_z, \quad \forall c \in \mathcal{C}

.. Total Efficiency Score
.. -----------------------

.. The total efficiency score for all projects can be computed by summing the individual efficiency metrics. This can be expressed as:

.. .. math::

..    \mathit{\eta_c}^\text{efficiency} = \eta_c^\text{well} + \eta_c^\text{age} + \eta_c^\text{depth} + \eta_c^\text{distance} + \eta_c^\text{dens} + \eta_c^\text{record} + \eta_c^\text{road} + \eta_c^\text{elev}, \quad \forall c \in \mathcal{C}
