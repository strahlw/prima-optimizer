import { required, numeric, minValue, maxValue, minLength, decimal } from '@vuelidate/validators';
import type { ScenarioForm } from '@/types/scenarioForm/scenarioForm';
import type { EfficiencyFormLabel } from '@/types/scenarioForm/efficiencyFactor';
import type {
    ImpactFactorsLossesLabel,
    ImpactFactorsSensitiveReceptorsLabel,
    ImpactFactorsEnvironmentLabel,
    ImpactFactorsAnnProductionVolumeLabel,
    ImpactFactorsFiveYearProductionVolumeLabel,
    ImpactFactorsLifelongProductionVolumeLabel,
    ImpactFactorsSiteConsiderationsLabel,
    ImpactFactorsEcologicalReceptorsLabel,
    ImpactFactorsOtherLossesLabel,
    ImpactFactorsLabel
} from '@/types/scenarioForm/impactFactor';
import { customMaxValue, customMinValue } from '../utils/validationHelpers';

export const validationRules = {
    useCases: {
        cases: { required }
    },
    generalSpecifications: {
        basic: {
            organizationId: { required },
            datasetId: { required, numeric },
            additionalDatasets: {},
            name: { required },
            budget: { required, numeric, minValue: customMinValue(120000) },
            minWellsInProject: { numeric, minValue: customMinValue(1), maxValue: customMaxValue(100) },
            maxWellsInProject: { numeric },
            wellDepthLimit: { numeric, minValue: customMinValue(1), maxValue: customMaxValue(50000) },
            maxDistanceBetweenProjectWells: { numeric, minValue: customMinValue(0), maxValue: customMaxValue(500) },
            maxWellsPerOwner: { numeric, minValue: customMinValue(0), maxValue: customMaxValue(10000) },
            minLifetimeGasProduction: { numeric, minValue: customMinValue(0), maxValue: customMaxValue(1000000) },
            maxLifetimeGasProduction: { numeric, minValue: customMinValue(0), maxValue: customMaxValue(1000000000) },
            minLifetimeOilProduction: { numeric, minValue: customMinValue(0), maxValue: customMaxValue(1000000) },
            maxLifetimeOilProduction: { numeric, minValue: customMinValue(0), maxValue: customMaxValue(1000000000) },
            wellType: { required, minLength: minLength(1) }
        },
        plugging: {
            shallowGasWellCost: { required, numeric },
            deepGasWellCost: { required, numeric },
            shallowOilWellCost: { required, numeric },
            deepOilWellCost: { required, numeric },
            costEfficiency: { required, numeric, minValue: customMinValue(0.1), maxValue: customMaxValue(1) }
        },
        dataQuality: {
            basicDataChecks: { required },
            handleMissingWellAge: { required },
            specifiedAge: {
                numeric,
                minValue: customMinValue(0),
                maxValue: customMaxValue(300)
            },
            handleMissingDepth: { required },
            specifiedDepth: {
                numeric,
                minValue: customMinValue(0),
                maxValue: customMaxValue(20000)
            },
            handleMissingProduction: { required },
            specifiedAnnualOilProduction: {
                numeric
            },
            specifiedLifetimeOilProduction: {
                numeric
            },
            specifiedAnnualGasProduction: {
                numeric
            },
            specifiedLifetimeGasProduction: {
                numeric
            },
            handleMissingType: { required },
            specifiedType: {
                minLength: minLength(1)
            }
        },
        solver: {
            solverTime: { required, numeric },
            absoluteGap: { decimal, customMinValue: customMinValue(0), customMaxValue: customMaxValue(1000000) },
            relativeGap: { decimal, customMinValue: customMinValue(0), customMaxValue: customMaxValue(1) },
            model: { minLength: minLength(1) }
        }
    },
    impactFactors: {
        losses: {
            value: { numeric, minValue: minValue(0), maxValue: maxValue(100) },
            selected: { required },
            childFactors: {
                leak: { value: { numeric, minValue: minValue(0), maxValue: maxValue(100) } },
                violation: { value: { numeric, minValue: minValue(0), maxValue: maxValue(100) } },
                compliance: { value: { numeric, minValue: minValue(0), maxValue: maxValue(100) } },
                incident: { value: { numeric, minValue: minValue(0), maxValue: maxValue(100) } },
                hydrocarbonLosses: { value: { numeric, minValue: minValue(0), maxValue: maxValue(100) } }
            }
        },
        annProductionVolume: {
            value: { numeric, minValue: minValue(0), maxValue: maxValue(100) },
            selected: { required },
            childFactors: {
                annGasProduction: { value: { numeric, minValue: minValue(0), maxValue: maxValue(100) } },
                annOilProduction: { value: { numeric, minValue: minValue(0), maxValue: maxValue(100) } }
            }
        },
        fiveYearProductionVolume: {
            value: { numeric, minValue: minValue(0), maxValue: maxValue(100) },
            selected: { required },
            childFactors: {
                fiveYearGasProduction: { value: { numeric, minValue: minValue(0), maxValue: maxValue(100) } },
                fiveYearOilProduction: { value: { numeric, minValue: minValue(0), maxValue: maxValue(100) } }
            }
        },
        wellAge: { value: { numeric, minValue: minValue(0), maxValue: maxValue(100) }, selected: { required } },
        ownerWellCount: { value: { numeric, minValue: minValue(0), maxValue: maxValue(100) }, selected: { required } },
        lifelongProductionVolume: {
            value: { numeric, minValue: minValue(0), maxValue: maxValue(100) },
            selected: { required },
            childFactors: {
                lifelongGasProduction: { value: { numeric, minValue: minValue(0), maxValue: maxValue(100) } },
                lifelongProduction: { value: { numeric, minValue: minValue(0), maxValue: maxValue(100) } }
            }
        },
        sensitiveReceptors: {
            value: { numeric, minValue: minValue(0), maxValue: maxValue(100) },
            selected: { required },
            childFactors: {
                schools: { value: { numeric, minValue: minValue(0), maxValue: maxValue(100) } },
                hospitals: { value: { numeric, minValue: minValue(0), maxValue: maxValue(100) } },
                agricultureAreaNearby: { value: { numeric, minValue: minValue(0), maxValue: maxValue(100) } },
                buildingsNear: { value: { numeric, minValue: minValue(0), maxValue: maxValue(100) } },
                buildingsFar: { value: { numeric, minValue: minValue(0), maxValue: maxValue(100) } }
            }
        },
        siteConsiderations: {
            value: { numeric, minValue: minValue(0), maxValue: maxValue(100) },
            selected: { required },
            childFactors: {
                historicalPreservationSite: { value: { numeric, minValue: minValue(0), maxValue: maxValue(100) } },
                homeUseGasWell: { value: { numeric, minValue: minValue(0), maxValue: maxValue(100) } },
                postPluggingLandUse: { value: { numeric, minValue: minValue(0), maxValue: maxValue(100) } },
                surfaceEquipmentOnSite: { value: { numeric, minValue: minValue(0), maxValue: maxValue(100) } }
            }
        },
        ecologicalReceptors: {
            value: { numeric, minValue: minValue(0), maxValue: maxValue(100) },
            selected: { required },
            childFactors: {
                endangeredSpeciesOnSite: { value: { numeric, minValue: minValue(0), maxValue: maxValue(100) } }
            }
        },
        otherLosses: {
            value: { numeric, minValue: minValue(0), maxValue: maxValue(100) },
            selected: { required },
            childFactors: {
                brineLeak: { value: { numeric, minValue: minValue(0), maxValue: maxValue(100) } },
                h2sLeak: { value: { numeric, minValue: minValue(0), maxValue: maxValue(100) } }
            }
        },
        environment: {
            value: { numeric, minValue: minValue(0), maxValue: maxValue(100) },
            selected: { required },
            childFactors: {
                waterSourceNearby: { value: { numeric, minValue: minValue(0), maxValue: maxValue(100) } },
                knownSoilOrWaterImpact: { value: { numeric, minValue: minValue(0), maxValue: maxValue(100) } },
                fedWetlandsNear: { value: { numeric, minValue: minValue(0), maxValue: maxValue(100) } },
                fedWetlandsFar: { value: { numeric, minValue: minValue(0), maxValue: maxValue(100) } },
                stateWetlandsNear: { value: { numeric, minValue: minValue(0), maxValue: maxValue(100) } },
                stateWetlandsFar: { value: { numeric, minValue: minValue(0), maxValue: maxValue(100) } }
            }
        },
        likelyToBeOrphaned: {
            value: { numeric, minValue: minValue(0), maxValue: maxValue(100) },
            selected: { required }
        },
        inTribalLand: { value: { numeric, minValue: minValue(0), maxValue: maxValue(100) }, selected: { required } },
        costOfPlugging: { value: { numeric, minValue: minValue(0), maxValue: maxValue(100) }, selected: { required } },
        highPressureObserved: {
            value: { numeric, minValue: minValue(0), maxValue: maxValue(100) },
            selected: { required }
        },
        idleStatusDuration: {
            value: { numeric, minValue: minValue(0), maxValue: maxValue(100) },
            selected: { required }
        },
        numberOfMcwsNearby: {
            value: { numeric, minValue: minValue(0), maxValue: maxValue(100) },
            selected: { required }
        },
        mechanicalIntegrityTest: {
            value: { numeric, minValue: minValue(0), maxValue: maxValue(100) },
            selected: { required }
        },
        otherwiseIncentivizedWell: {
            value: { numeric, minValue: minValue(0), maxValue: maxValue(100) },
            selected: { required }
        },
        wellIntegrity: { value: { numeric, minValue: minValue(0), maxValue: maxValue(100) }, selected: { required } },
        placeholderTwo: { value: { numeric, minValue: minValue(0), maxValue: maxValue(100) }, selected: { required } },
        placeholderThree: {
            value: { numeric, minValue: minValue(0), maxValue: maxValue(100) },
            selected: { required }
        },
        placeholderFour: { value: { numeric, minValue: minValue(0), maxValue: maxValue(100) }, selected: { required } },
        placeholderFive: { value: { numeric, minValue: minValue(0), maxValue: maxValue(100) }, selected: { required } },
        placeholderSix: { value: { numeric, minValue: minValue(0), maxValue: maxValue(100) }, selected: { required } },
        placeholderSeven: {
            value: { numeric, minValue: minValue(0), maxValue: maxValue(100) },
            selected: { required }
        },
        placeholderEight: {
            value: { numeric, minValue: minValue(0), maxValue: maxValue(100) },
            selected: { required }
        },
        placeholderNine: { value: { numeric, minValue: minValue(0), maxValue: maxValue(100) }, selected: { required } },
        placeholderTen: { value: { numeric, minValue: minValue(0), maxValue: maxValue(100) }, selected: { required } },
        placeholderEleven: {
            value: { numeric, minValue: minValue(0), maxValue: maxValue(100) },
            selected: { required }
        },
        placeholderTwelve: {
            value: { numeric, minValue: minValue(0), maxValue: maxValue(100) },
            selected: { required }
        },
        placeholderThirteen: {
            value: { numeric, minValue: minValue(0), maxValue: maxValue(100) },
            selected: { required }
        },
        placeholderFourteen: {
            value: { numeric, minValue: minValue(0), maxValue: maxValue(100) },
            selected: { required }
        },
        placeholderFifteen: {
            value: { numeric, minValue: minValue(0), maxValue: maxValue(100) },
            selected: { required }
        },
        placeholderSixteen: {
            value: { numeric, minValue: minValue(0), maxValue: maxValue(100) },
            selected: { required }
        },
        placeholderSeventeen: {
            value: { numeric, minValue: minValue(0), maxValue: maxValue(100) },
            selected: { required }
        },
        placeholderEighteen: {
            value: { numeric, minValue: minValue(0), maxValue: maxValue(100) },
            selected: { required }
        },
        placeholderNineteen: {
            value: { numeric, minValue: minValue(0), maxValue: maxValue(100) },
            selected: { required }
        },
        placeholderTwenty: {
            value: { numeric, minValue: minValue(0), maxValue: maxValue(100) },
            selected: { required }
        }
    },
    efficiencyFactors: {
        numWells: { value: { numeric, minValue: minValue(0), maxValue: maxValue(100) }, selected: { required } },
        numUniqueOwners: { value: { numeric, minValue: minValue(0), maxValue: maxValue(100) }, selected: { required } },
        distanceToCentroid: {
            value: { numeric, minValue: minValue(0), maxValue: maxValue(100) },
            selected: { required }
        },
        avgDistanceToNearestRoad: {
            value: { numeric, minValue: minValue(0), maxValue: maxValue(100) },
            selected: { required }
        },
        avgElevationChangeFromNearestRoad: {
            value: { numeric, minValue: minValue(0), maxValue: maxValue(100) },
            selected: { required }
        },
        ageRange: { value: { numeric, minValue: minValue(0), maxValue: maxValue(100) }, selected: { required } },
        avgAge: { value: { numeric, minValue: minValue(0), maxValue: maxValue(100) }, selected: { required } },
        depthRange: { value: { numeric, minValue: minValue(0), maxValue: maxValue(100) }, selected: { required } },
        avgDepth: { value: { numeric, minValue: minValue(0), maxValue: maxValue(100) }, selected: { required } },
        distanceRange: { value: { numeric, minValue: minValue(0), maxValue: maxValue(100) }, selected: { required } },
        populationDensity: {
            value: { numeric, minValue: minValue(0), maxValue: maxValue(100) },
            selected: { required }
        }
    },
    wellRanking: {
        rank: {}
    },
    paProjectComparisons: {
        comparison: {}
    },
    $validationGroups: {
        useCases: ['useCases.cases'],
        basic: [
            'generalSpecifications.organizationId',
            'generalSpecifications.datasetId',
            'generalSpecifications.additionalDatasets',
            'generalSpecifications.name',
            'generalSpecifications.budget',
            'generalSpecifications.minWellsInProject',
            'generalSpecifications.maxWellsInProject',
            'generalSpecifications.wellDepthLimit',
            'generalSpecifications.maxDistanceBetweenProjectWells',
            'generalSpecifications.minLifetimeGasProduction',
            'generalSpecifications.maxLifetimeGasProduction',
            'generalSpecifications.minLifetimeOilProduction',
            'generalSpecifications.maxLifetimeOilProduction',
            'generalSpecifications.wellType',
            'generalSpecifications.maxWellsPerOwner'
        ],
        plugging: [
            'generalSpecifications.shallowGasWellCost',
            'generalSpecifications.deepGasWellCost',
            'generalSpecifications.shallowOilWellCost',
            'generalSpecifications.deepOilWellCost',
            'generalSpecifications.costEfficiency'
        ],
        dataQuality: [
            'generalSpecifications.basicDataChecks',
            'generalSpecifications.handleMissingWellAge',
            'generalSpecifications.specifiedAge',
            'generalSpecifications.handleMissingDepth',
            'generalSpecifications.specifiedDepth',
            'generalSpecifications.handleMissingProduction',
            'generalSpecifications.specifiedAnnualOilProduction',
            'generalSpecifications.specifiedLifetimeOilProduction',
            'generalSpecifications.specifiedAnnualGasProduction',
            'generalSpecifications.specifiedLifetimeGasProduction',
            'generalSpecifications.handleMissingType',
            'generalSpecifications.specifiedType'
        ],
        solver: [
            'generalSpecifications.solverTime',
            'generalSpecifications.absoluteGap',
            'generalSpecifications.relativeGap',
            'generalSpecifications.model'
        ],
        impactFactors: [
            'impactFactors.losses',
            'impactFactors.wellAge',
            'impactFactors.ownerWellCount',
            'impactFactors.annProductionVolume',
            'impactFactors.fiveYearProductionVolume',
            'impactFactors.siteConsiderations',
            'impactFactors.lifelongProductionVolume',
            'impactFactors.sensitiveReceptors',
            'impactFactors.ecologicalReceptors',
            'impactFactors.otherLosses',
            'impactFactors.likelyToBeOrphaned',
            'impactFactors.inTribalLand',
            'impactFactors.likelyToBeOrphaned',
            'impactFactors.inTribalLand',
            'impactFactors.costOfPlugging',
            'impactFactors.highPressureObserved',
            'impactFactors.idleStatusDuration',
            'impactFactors.numberOfMcwsNearby',
            'impactFactors.mechanicalIntegrityTest',
            'impactFactors.otherwiseIncentivizedWell',
            'impactFactors.wellIntegrity',
            'impactFactors.placeholderOne',
            'impactFactors.placeholderTwo',
            'impactFactors.placeholderThree',
            'impactFactors.placeholderFour',
            'impactFactors.placeholderFive',
            'impactFactors.placeholderSix',
            'impactFactors.placeholderSeven',
            'impactFactors.placeholderEight',
            'impactFactors.placeholderNine',
            'impactFactors.placeholderTen',
            'impactFactors.placeholderEleven',
            'impactFactors.placeholderTwelve',
            'impactFactors.placeholderThirteen',
            'impactFactors.placeholderFourteen',
            'impactFactors.placeholderFifteen',
            'impactFactors.placeholderSixteen',
            'impactFactors.placeholderSeventeen',
            'impactFactors.placeholderEighteen',
            'impactFactors.placeholderNineteen',
            'impactFactors.placeholderTwenty'
        ],
        efficiencyFactors: [
            'efficiencyFactors.numWells',
            'efficiencyFactors.numUniqueOwners',
            'efficiencyFactors.distanceToCentroid',
            'efficiencyFactors.avgDistanceToNearestRoad',
            'efficiencyFactors.avgElevationChangeFromNearestRoad',
            'efficiencyFactors.ageRange',
            'efficiencyFactors.avgAge',
            'efficiencyFactors.depthRange',
            'efficiencyFactors.avgDepth',
            'efficiencyFactors.distanceRange',
            'efficiencyFactors.populationDensity'
        ],
        wellRanking: ['wellRanking.rank'],
        paProjectComparisons: ['paProjectComparisons.comparison']
    }
};

export const initialScenarioForm: ScenarioForm = {
    id: null,
    useCases: {
        cases: []
    },
    generalSpecifications: {
        basic: {
            organizationId: null,
            datasetId: null,
            additionalDatasets: [],
            name: '',
            budget: 0,
            minWellsInProject: 2,
            maxWellsInProject: 30,
            wellDepthLimit: 4000,
            maxDistanceBetweenProjectWells: 10,
            minLifetimeGasProduction: null,
            maxLifetimeGasProduction: null,
            minLifetimeOilProduction: null,
            maxLifetimeOilProduction: null,
            wellType: [],
            maxWellsPerOwner: null
        },
        plugging: {
            shallowGasWellCost: null,
            deepGasWellCost: null,
            shallowOilWellCost: null,
            deepOilWellCost: null,
            costEfficiency: 0.9
        },
        dataQuality: {
            basicDataChecks: true,
            handleMissingWellAge: 'specify-value',
            specifiedAge: null,
            handleMissingDepth: 'specify-value',
            specifiedDepth: null,
            handleMissingProduction: 'specify-value',
            specifiedAnnualOilProduction: null,
            specifiedLifetimeOilProduction: null,
            specifiedAnnualGasProduction: null,
            specifiedLifetimeGasProduction: null,
            handleMissingType: 'specify-value',
            specifiedType: null
        },
        solver: {
            solverTime: 3600,
            absoluteGap: null,
            relativeGap: null,
            model: null
        }
    },
    impactFactors: {
        losses: {
            value: 0,
            selected: true,
            childFactors: {
                leak: {
                    value: 0,
                    selected: true,
                    toolTip: 'Prioritize wells that have a known leak (as a proxy for Hydrocarbon Losses)'
                },
                violation: {
                    value: 0,
                    selected: true,
                    toolTip: 'Prioritize wells that have violated regulations (as a proxy for Hydrocarbon Losses)'
                },
                compliance: {
                    value: 0,
                    selected: true,
                    toolTip:
                        'Prioritize wells that have documented compliance issues (as a proxy for Hydrocarbon Losses)'
                },
                incident: {
                    value: 0,
                    selected: true,
                    toolTip: 'Prioritize wells that have a documented incident (as a proxy for Hydrocarbon Losses)'
                },
                hydrocarbonLosses: {
                    value: 0,
                    selected: true,
                    toolTip: 'Prioritize wells that have greater hydrocarbon losses'
                }
            },
            toolTip: 'Prioritize wells with expected or known hydrocarbon losses'
        },
        annProductionVolume: {
            value: 0,
            selected: true,
            childFactors: {
                annGasProduction: {
                    value: 0,
                    selected: true,
                    toolTip: 'Prioritize wells that have lower annual gas production [Mcf/Year]'
                },
                annOilProduction: {
                    value: 0,
                    selected: true,
                    toolTip: 'Prioritize wells that have lower annual oil production [bbl/Year]'
                }
            },
            toolTip: 'Prioritize wells with lower annual production volumes'
        },
        fiveYearProductionVolume: {
            value: 0,
            selected: true,
            childFactors: {
                fiveYearGasProduction: {
                    value: 0,
                    selected: true,
                    toolTip: 'Prioritize wells that have lower 5-Year gas production [Mcf/Year] values'
                },
                fiveYearOilProduction: {
                    value: 0,
                    selected: true,
                    toolTip: 'Prioritize wells that have lower 5-Year oil production [bbl/Year] values'
                }
            },
            toolTip: 'Prioritize wells with lower 5-Year production volume values'
        },
        wellAge: { value: 0, selected: true, toolTip: 'Prioritize older wells' },
        ownerWellCount: {
            value: 0,
            selected: true,
            toolTip: 'Prioritize wells owned by individuals or companies with fewer wells'
        },
        lifelongProductionVolume: {
            value: 0,
            selected: true,
            childFactors: {
                lifelongGasProduction: {
                    value: 0,
                    selected: true,
                    toolTip: 'Prioritize wells that have lower lifetime gas production [Mcf/Year] values'
                },
                lifelongOilProduction: {
                    value: 0,
                    selected: true,
                    toolTip: 'Prioritize wells that have lower lifetime oil production [bbl/Year] values'
                }
            },
            toolTip: 'Prioritize wells with lower lifetime production volume values'
        },
        sensitiveReceptors: {
            value: 0,
            selected: true,
            childFactors: {
                schools: { value: 0, selected: true, toolTip: 'Prioritize wells near schools' },
                hospitals: { value: 0, selected: true, toolTip: 'Prioritize wells near hospitals' },
                agricultureAreaNearby: {
                    value: 0,
                    selected: true,
                    toolTip: 'Prioritize wells near agricultural areas'
                },
                buildingsNear: { value: 0, selected: true, toolTip: 'Prioritize wells close to buildings (near)' },
                buildingsFar: { value: 0, selected: true, toolTip: 'Prioritize wells close to buildings (far)' }
            },
            toolTip: 'Prioritize wells near sensitive receptors'
        },
        siteConsiderations: {
            value: 0,
            selected: true,
            childFactors: {
                historicalPreservationSite: {
                    value: 0,
                    selected: true,
                    toolTip: 'Prioritize wells near historical preservation sites'
                },
                homeUseGasWell: {
                    value: 0,
                    selected: true,
                    toolTip: 'Prioritize wells that are not home use gas wells'
                },
                postPluggingLandUse: {
                    value: 0,
                    selected: true,
                    toolTip: 'Prioritize wells where the land can be used post-plugging'
                },
                surfaceEquipmentOnSite: {
                    value: 0,
                    selected: true,
                    toolTip: 'Prioritize wells with surface equipment on site'
                }
            },
            toolTip: 'Prioritize wells depending on site considerations'
        },
        otherLosses: {
            value: 0,
            selected: true,
            childFactors: {
                brineLeak: {
                    value: 0,
                    selected: true,
                    toolTip: 'Prioritize wells that have brine leaks'
                },
                h2sLeak: {
                    value: 0,
                    selected: true,
                    toolTip: 'Prioritize wells leaking H2S'
                }
            },
            toolTip: 'Prioritize wells considering losses other than hydrocarbons'
        },
        ecologicalReceptors: {
            value: 0,
            selected: true,
            childFactors: {
                endangeredSpeciesOnSite: {
                    value: 0,
                    selected: true,
                    toolTip: 'Prioritize wells with endangered species on site'
                }
            },
            toolTip: 'Prioritize wells depending on ecological considerations'
        },
        environment: {
            value: 0,
            selected: true,
            childFactors: {
                waterSourceNearby: {
                    value: 0,
                    selected: true,
                    toolTip: 'Prioritize wells near freshwater sources'
                },
                knownSoilOrWaterImpact: {
                    value: 0,
                    selected: true,
                    toolTip: 'Prioritize wells with known impacts on nearby soil or water'
                },
                fedWetlandsNear: {
                    value: 0,
                    selected: true,
                    toolTip: 'Prioritize wells close to federal wetlands (near)'
                },
                fedWetlandsFar: {
                    value: 0,
                    selected: true,
                    toolTip: 'Prioritize wells close to federal wetlands (far)'
                },
                stateWetlandsNear: {
                    value: 0,
                    selected: true,
                    toolTip: 'Prioritize wells close to state wetlands (near)'
                },
                stateWetlandsFar: {
                    value: 0,
                    selected: true,
                    toolTip: 'Prioritize wells close to state wetlands (far)'
                }
            },
            toolTip: 'Prioritize wells that are close to environmentally sensitive receptors'
        },
        likelyToBeOrphaned: {
            value: 0,
            selected: true,
            toolTip: 'Prioritize wells that are likely to become orphan wells'
        },
        inTribalLand: {
            value: 0,
            selected: true,
            toolTip: 'Prioritize wells that are located in tribal lands'
        },
        costOfPlugging: {
            value: 0,
            selected: true,
            toolTip: 'Prioritize wells that less expensive to plug'
        },
        highPressureObserved: {
            value: 0,
            selected: true,
            toolTip: 'Prioritize wells where high pressures have been observed'
        },
        idleStatusDuration: {
            value: 0,
            selected: true,
            toolTip: 'Prioritize wells that have been idle for longer durations'
        },
        numberOfMcwsNearby: {
            value: 0,
            selected: true,
            toolTip: 'Prioritize wells with a greater number of other MCWs nearby'
        },
        mechanicalIntegrityTest: {
            value: 0,
            selected: true,
            toolTip: 'Prioritize wells that score a higher number on the mechanical integrity test'
        },
        otherwiseIncentivizedWell: {
            value: 0,
            selected: true,
            toolTip: 'Prioritize wells that are otherwise incentivized'
        },
        wellIntegrity: {
            value: 0,
            selected: true,
            toolTip: 'Prioritize wells that have well integrity issues'
        },
        placeholderOne: {
            value: 0,
            selected: true,
            toolTip: 'Prioritize wells with true values for the data in the "Placeholder 1 " column'
        },
        placeholderTwo: {
            value: 0,
            selected: true,
            toolTip: 'Prioritize wells with true values for the data in the "Placeholder 2 " column'
        },
        placeholderThree: {
            value: 0,
            selected: true,
            toolTip: 'Prioritize wells with true values for the data in the "Placeholder 3 " column'
        },
        placeholderFour: {
            value: 0,
            selected: true,
            toolTip: 'Prioritize wells with true values for the data in the "Placeholder 4 " column'
        },
        placeholderFive: {
            value: 0,
            selected: true,
            toolTip: 'Prioritize wells with true values for the data in the "Placeholder 5 " column'
        },
        placeholderSix: {
            value: 0,
            selected: true,
            toolTip: 'Prioritize wells with larger values for the data in the "Placeholder 6 " column'
        },
        placeholderSeven: {
            value: 0,
            selected: true,
            toolTip: 'Prioritize wells with larger values for the data in the "Placeholder 7 " column'
        },
        placeholderEight: {
            value: 0,
            selected: true,
            toolTip: 'Prioritize wells with larger values for the data in the "Placeholder 8 " column'
        },
        placeholderNine: {
            value: 0,
            selected: true,
            toolTip: 'Prioritize wells with larger values for the data in the "Placeholder 9 " column'
        },
        placeholderTen: {
            value: 0,
            selected: true,
            toolTip: 'Prioritize wells with larger values for the data in the "Placeholder 10"  column'
        },
        placeholderEleven: {
            value: 0,
            selected: true,
            toolTip: 'Prioritize wells with false values for the data in the "Placeholder 11"  column'
        },
        placeholderTwelve: {
            value: 0,
            selected: true,
            toolTip: 'Prioritize wells with false values for the data in the "Placeholder 12"  column'
        },
        placeholderThirteen: {
            value: 0,
            selected: true,
            toolTip: 'Prioritize wells with false values for the data in the "Placeholder 13"  column'
        },
        placeholderFourteen: {
            value: 0,
            selected: true,
            toolTip: 'Prioritize wells with false values for the data in the "Placeholder 14"  column'
        },
        placeholderFifteen: {
            value: 0,
            selected: true,
            toolTip: 'Prioritize wells with false values for the data in the "Placeholder 15"  column'
        },
        placeholderSixteen: {
            value: 0,
            selected: true,
            toolTip: 'Prioritize wells with smaller values for the data in the "Placeholder 16"  column'
        },
        placeholderSeventeen: {
            value: 0,
            selected: true,
            toolTip: 'Prioritize wells with smaller values for the data in the "Placeholder 17"  column'
        },
        placeholderEighteen: {
            value: 0,
            selected: true,
            toolTip: 'Prioritize wells with smaller values for the data in the "Placeholder 18"  column'
        },
        placeholderNineteen: {
            value: 0,
            selected: true,
            toolTip: 'Prioritize wells with smaller values for the data in the "Placeholder 19"  column'
        },
        placeholderTwenty: {
            value: 0,
            selected: true,
            toolTip: 'Prioritize wells with smaller values for the data in the "Placeholder 20"  column'
        }
    },
    efficiencyFactors: {
        numWells: {
            selected: true,
            value: 0,
            toolTip: 'Encourages PRIMO to prioritize P&A projects with a larger number of wells'
        },
        numUniqueOwners: {
            selected: false,
            value: 0,
            toolTip:
                'Encourages PRIMO to prioritize P&A projects with fewer variations in the number of well owners (ideal case: only one owner/operator for a project)'
        },
        distanceToCentroid: { selected: true, value: 0, toolTip: 'Tooltip for distanceToCentroid' },
        avgDistanceToNearestRoad: {
            selected: true,
            value: 0,
            toolTip: 'Encourages PRIMO to prioritize P&A projects with wells that are close to an existing road'
        },
        avgElevationChangeFromNearestRoad: {
            selected: true,
            value: 0,
            toolTip:
                'Encourages PRIMO to prioritize P&A projects with wells located on level terrain or areas with minimal elevation change'
        },
        ageRange: {
            selected: true,
            value: 0,
            toolTip:
                'Encourages PRIMO to prioritize P&A projects where the wells within the project are of a similar age'
        },
        avgAge: {
            selected: false,
            value: 0,
            toolTip:
                'Encourages PRIMO to prioritize P&A projects where the average age of wells within the project is smaller'
        },
        depthRange: {
            selected: true,
            value: 0,
            toolTip:
                'Encourages PRIMO to prioritize P&A projects where the wells within the project are of similar depths'
        },
        avgDepth: {
            selected: false,
            value: 0,
            toolTip:
                'Encourages PRIMO to prioritize P&A projects where the average depth of wells within the project is shallower'
        },
        distanceRange: {
            selected: true,
            value: 0,
            toolTip: 'Encourages PRIMO to prioritize P&A projects where the wells are in close proximity to each other'
        },
        populationDensity: {
            selected: true,
            value: 0,
            toolTip:
                'Encourages PRIMO to prioritize P&A projects where the wells are in areas of low population density'
        }
    },
    wellRanking: {
        rank: ''
    },
    paProjectComparisons: {
        comparison: ''
    },
    copyParentId: null,
    $validationGroups: { ...validationRules.$validationGroups }
};

/** Start impact factors form specific constants */
export const lossesLabel: ImpactFactorsLossesLabel = {
    name: 'Hydrocarbon Losses',
    field: 'losses',
    childFields: [
        { name: 'Leak', field: 'leak' },
        { name: 'Violation', field: 'violation' },
        { name: 'Compliance', field: 'compliance' },
        { name: 'Incident', field: 'incident' },
        { name: 'Hydrocarbon Losses', field: 'hydrocarbonLosses' }
    ]
};

export const annProductionVolumeLabel: ImpactFactorsAnnProductionVolumeLabel = {
    name: 'Annual Production Volume',
    field: 'annProductionVolume',
    childFields: [
        { name: 'Annual Gas Production Volume', field: 'annGasProduction' },
        { name: 'Annual Oil Production Volume', field: 'annOilProduction' }
    ]
};

export const fiveYearProductionVolumeLabel: ImpactFactorsFiveYearProductionVolumeLabel = {
    name: '5-Year Production Volume',
    field: 'fiveYearProductionVolume',
    childFields: [
        { name: '5-Year Gas Production Volume', field: 'fiveYearGasProduction' },
        { name: '5-Year Oil Production Volume', field: 'fiveYearOilProduction' }
    ]
};

export const lifelongProductionVolumeLabel: ImpactFactorsLifelongProductionVolumeLabel = {
    name: 'Lifetime Production Volume',
    field: 'lifelongProductionVolume',
    childFields: [
        { name: 'Lifetime Gas Production Volume', field: 'lifelongGasProduction' },
        { name: 'Lifetime Oil Production Volume', field: 'lifelongOilProduction' }
    ]
};

export const sensitiveReceptorsLabel: ImpactFactorsSensitiveReceptorsLabel = {
    field: 'sensitiveReceptors',
    name: 'Sensitive Receptors',
    childFields: [
        { name: 'Schools', field: 'schools' },
        { name: 'Hospitals', field: 'hospitals' },
        { name: 'Agriculture Area Nearby', field: 'agricultureAreaNearby' },
        { name: 'Buildings (Near)', field: 'buildingsNear' },
        { name: 'Buildings (Far)', field: 'buildingsFar' }
    ]
};

export const siteConsiderationsLabel: ImpactFactorsSiteConsiderationsLabel = {
    field: 'siteConsiderations',
    name: 'Site Considerations',
    childFields: [
        { name: 'Historical Preservation Site', field: 'historicalPreservationSite' },
        { name: 'Home Use Gas Well', field: 'homeUseGasWell' },
        { name: 'Post-Plugging Land Use', field: 'postPluggingLandUse' },
        { name: 'Surface Equipment On Site', field: 'surfaceEquipmentOnSite' }
    ]
};

export const ecologicalReceptorsLabel: ImpactFactorsEcologicalReceptorsLabel = {
    field: 'ecologicalReceptors',
    name: 'Ecological Receptors',
    childFields: [{ name: 'Endangered Species On Site', field: 'endangeredSpeciesOnSite' }]
};
export const otherLossesLabel: ImpactFactorsOtherLossesLabel = {
    field: 'otherLosses',
    name: 'Other Losses',
    childFields: [
        { name: 'Brine Leak', field: 'brineLeak' },
        { name: 'H2S Leak', field: 'h2sLeak' }
    ]
};

export const environmentLabel: ImpactFactorsEnvironmentLabel = {
    name: 'Environment',
    field: 'environment',
    childFields: [
        { name: 'Fresh Water Source Nearby', field: 'waterSourceNearby' },
        { name: 'Known Soil or Water Impact', field: 'knownSoilOrWaterImpact' },
        { name: 'Federal Wetlands (Near)', field: 'fedWetlandsNear' },
        { name: 'Federal Wetlands (Far)', field: 'fedWetlandsFar' },
        { name: 'State Wetlands (Near)', field: 'stateWetlandsNear' },
        { name: 'State Wetlands (Far)', field: 'stateWetlandsFar' }
    ]
};

export const impactFactorsLabels: ImpactFactorsLabel[] = [
    { name: 'Well Age', field: 'wellAge' },
    { name: 'Owner Well Count', field: 'ownerWellCount' },
    { name: 'Likely To Be Orphaned', field: 'likelyToBeOrphaned' },
    { name: 'In Tribal Land', field: 'inTribalLand' },
    { name: 'Cost Of Plugging', field: 'costOfPlugging' },
    { name: 'High Pressure Observed', field: 'highPressureObserved' },
    { name: 'Idle Status Duration', field: 'idleStatusDuration' },
    { name: 'Number Of MCWs Nearby', field: 'numberOfMcwsNearby' },
    { name: 'Mechanical Integrity Test', field: 'mechanicalIntegrityTest' },
    { name: 'Otherwise Incentivized Well', field: 'otherwiseIncentivizedWell' },
    { name: 'Well Integrity', field: 'wellIntegrity' },
    { name: 'Placeholder 1', field: 'placeholderOne' },
    { name: 'Placeholder 2', field: 'placeholderTwo' },
    { name: 'Placeholder 3', field: 'placeholderThree' },
    { name: 'Placeholder 4', field: 'placeholderFour' },
    { name: 'Placeholder 5', field: 'placeholderFive' },
    { name: 'Placeholder 6', field: 'placeholderSix' },
    { name: 'Placeholder 7', field: 'placeholderSeven' },
    { name: 'Placeholder 8', field: 'placeholderEight' },
    { name: 'Placeholder 9', field: 'placeholderNine' },
    { name: 'Placeholder 10', field: 'placeholderTen' },
    { name: 'Placeholder 11', field: 'placeholderEleven' },
    { name: 'Placeholder 12', field: 'placeholderTwelve' },
    { name: 'Placeholder 13', field: 'placeholderThirteen' },
    { name: 'Placeholder 14', field: 'placeholderFourteen' },
    { name: 'Placeholder 15', field: 'placeholderFifteen' },
    { name: 'Placeholder 16', field: 'placeholderSixteen' },
    { name: 'Placeholder 17', field: 'placeholderSeventeen' },
    { name: 'Placeholder 18', field: 'placeholderEighteen' },
    { name: 'Placeholder 19', field: 'placeholderNineteen' },
    { name: 'Placeholder 20', field: 'placeholderTwenty' }
];

export const orderedImpactFactorsLabels: (
    | ImpactFactorsLabel
    | ImpactFactorsEnvironmentLabel
    | ImpactFactorsLossesLabel
    | ImpactFactorsSensitiveReceptorsLabel
    | ImpactFactorsAnnProductionVolumeLabel
    | ImpactFactorsFiveYearProductionVolumeLabel
    | ImpactFactorsLifelongProductionVolumeLabel
    | ImpactFactorsSiteConsiderationsLabel
    | ImpactFactorsEcologicalReceptorsLabel
    | ImpactFactorsOtherLossesLabel
)[] = [
    { name: 'Well Age', field: 'wellAge' },
    { name: 'Owner Well Count', field: 'ownerWellCount' },
    lifelongProductionVolumeLabel,
    annProductionVolumeLabel,
    fiveYearProductionVolumeLabel,
    sensitiveReceptorsLabel,
    ecologicalReceptorsLabel,
    environmentLabel,
    siteConsiderationsLabel,
    { name: 'Likely To Be Orphaned', field: 'likelyToBeOrphaned' },
    { name: 'In Tribal Land', field: 'inTribalLand' },
    { name: 'Cost Of Plugging', field: 'costOfPlugging' },
    { name: 'High Pressure Observed', field: 'highPressureObserved' },
    { name: 'Idle Status Duration', field: 'idleStatusDuration' },
    { name: 'Number Of MCWs Nearby', field: 'numberOfMcwsNearby' },
    { name: 'Mechanical Integrity Test', field: 'mechanicalIntegrityTest' },
    { name: 'Otherwise Incentivized Well', field: 'otherwiseIncentivizedWell' },
    { name: 'Well Integrity', field: 'wellIntegrity' },
    { name: 'Placeholder 1', field: 'placeholderOne' },
    { name: 'Placeholder 2', field: 'placeholderTwo' },
    { name: 'Placeholder 3', field: 'placeholderThree' },
    { name: 'Placeholder 4', field: 'placeholderFour' },
    { name: 'Placeholder 5', field: 'placeholderFive' },
    { name: 'Placeholder 6', field: 'placeholderSix' },
    { name: 'Placeholder 7', field: 'placeholderSeven' },
    { name: 'Placeholder 8', field: 'placeholderEight' },
    { name: 'Placeholder 9', field: 'placeholderNine' },
    { name: 'Placeholder 10', field: 'placeholderTen' },
    { name: 'Placeholder 11', field: 'placeholderEleven' },
    { name: 'Placeholder 12', field: 'placeholderTwelve' },
    { name: 'Placeholder 13', field: 'placeholderThirteen' },
    { name: 'Placeholder 14', field: 'placeholderFourteen' },
    { name: 'Placeholder 15', field: 'placeholderFifteen' },
    { name: 'Placeholder 16', field: 'placeholderSixteen' },
    { name: 'Placeholder 17', field: 'placeholderSeventeen' },
    { name: 'Placeholder 18', field: 'placeholderEighteen' },
    { name: 'Placeholder 19', field: 'placeholderNineteen' },
    { name: 'Placeholder 20', field: 'placeholderTwenty' },
    lossesLabel,
    otherLossesLabel
];

export const impactFactorsSubHeading =
    'Select the weights/factors that determine the impact for your plugging projects. The total of all slider importance must equal 100.';

/** End impact factors form specific constants */

/** Start efficiency factors form specific constants */
export const efficiencyFactorsLabels: EfficiencyFormLabel[] = [
    { name: 'Number Of Wells In Project', field: 'numWells' },
    { name: 'Number Of Unique Owners', field: 'numUniqueOwners' },
    { name: 'Average Distance To Nearest Road', field: 'avgDistanceToNearestRoad' },
    { name: 'Average Elevation Change From Nearest Road To Well', field: 'avgElevationChangeFromNearestRoad' },
    { name: 'Age Range', field: 'ageRange' },
    { name: 'Average Age', field: 'avgAge' },
    { name: 'Depth Range', field: 'depthRange' },
    { name: 'Average Depth', field: 'avgDepth' },
    { name: 'Distance Range', field: 'distanceRange' },
    { name: 'Population Density', field: 'populationDensity' }
];

export const efficiencyFactorsSubHeading =
    'Select the weights/factors that determine the efficiency for your plugging projects. The total of all slider importance must equal 100.';

/** End efficiency factors form specific constants */
