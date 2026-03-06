import { ref, reactive, computed, watch } from 'vue';
import { defineStore } from 'pinia';
import useVuelidate from '@vuelidate/core';
import { createFormService } from '@/services/formService';
import { deepCopy } from '../../utils/deepCopy';
import { ScenarioFormTitle } from '@/constants/scenarioEnums';
import { validationRules, initialScenarioForm } from '../../constants/scenarioForm';
import { stringToCamelCase } from '../../utils/toCamelCase';
import { requiredIf, required, numeric } from '@vuelidate/validators';
import { greaterThanOrNull, lessThanOrNull, uniqueNameWithinOrg } from '../../utils/validationHelpers';
import { customMaxValue, customMinValue } from '@/utils/validationHelpers';
import type { ScenarioData } from '@/types/scenario';
import type { ImpactFactors } from '@/types/scenarioForm/impactFactor';
import type { EfficiencyFactors } from '@/types/scenarioForm/efficiencyFactor';
import type { GeneralSpecifications, GeneralSpecificationsInputs } from '@/types/scenarioForm/generalSpecification';
import { FormValueManager } from '@/services/formValueManagerService';
import { AFFECTED_FIELDS } from '@/constants/fieldConfig';

export const useScenarioFormStore = defineStore('scenarioForm', () => {
    const formService = createFormService();

    const form = reactive(deepCopy(initialScenarioForm));
    const formValueManager = ref<FormValueManager | null>(null);
    const userModifiedFields = ref<Set<string>>(new Set());
    const hasInitialized = ref(false);
    const lastSubmittedForm = ref(deepCopy(initialScenarioForm));
    const availableImpactFactors = ref<ImpactFactors | null>(null);
    const availableEfficiencyFactors = ref<EfficiencyFactors | null>(null);

    const isRankOnly = () =>
        form.useCases.cases.length === 1 && form.useCases.cases[0] === ScenarioFormTitle.WellRanking;
    const isOptimizationOnly = () =>
        form.useCases.cases.length === 1 && form.useCases.cases[0] === ScenarioFormTitle.PAProjectRecommendations;

    const reactiveRules = computed(() => ({
        ...validationRules,
        generalSpecifications: {
            basic: {
                ...validationRules.generalSpecifications.basic,
                minWellsInProject: {
                    ...validationRules.generalSpecifications.basic.minWellsInProject,
                    greaterThanOrNull: lessThanOrNull(
                        () => form.generalSpecifications.basic.maxWellsInProject,
                        'Maximum # of project wells'
                    )
                },
                maxWellsInProject: {
                    ...validationRules.generalSpecifications.basic.maxWellsInProject,
                    greaterThanOrNull: greaterThanOrNull(
                        () => form.generalSpecifications.basic.minWellsInProject,
                        'Minimum # of project wells'
                    )
                },
                minLifetimeGasProduction: {
                    ...validationRules.generalSpecifications.basic.minLifetimeGasProduction,
                    greaterThanOrNull: lessThanOrNull(
                        () => form.generalSpecifications.basic.maxLifetimeGasProduction,
                        'Maximum lifetime gas production'
                    )
                },
                maxLifetimeGasProduction: {
                    ...validationRules.generalSpecifications.basic.maxLifetimeGasProduction,
                    greaterThanOrNull: greaterThanOrNull(
                        () => form.generalSpecifications.basic.minLifetimeGasProduction,
                        'Minimum lifetime gas production'
                    )
                },
                minLifetimeOilProduction: {
                    ...validationRules.generalSpecifications.basic.minLifetimeOilProduction,
                    greaterThanOrNull: lessThanOrNull(
                        () => form.generalSpecifications.basic.maxLifetimeOilProduction,
                        'Maximum lifetime oil production'
                    )
                },
                maxLifetimeOilProduction: {
                    ...validationRules.generalSpecifications.basic.maxLifetimeOilProduction,
                    greaterThanOrNull: greaterThanOrNull(
                        () => form.generalSpecifications.basic.minLifetimeOilProduction,
                        'Minimum lifetime oil production'
                    )
                },
                name: {
                    required,
                    uniqueNameWithinOrg: uniqueNameWithinOrg(() => form.generalSpecifications.basic.organizationId)
                },
                budget: {
                    requiredIf: requiredIf(() => !isRankOnly()),
                    minValue: !isRankOnly() ? customMinValue(120000) : ''
                }
            },
            plugging: {
                shallowGasWellCost: { requiredIf: requiredIf(() => !isRankOnly()), numeric },
                deepGasWellCost: { requiredIf: requiredIf(() => !isRankOnly()), numeric },
                shallowOilWellCost: { requiredIf: requiredIf(() => !isRankOnly()), numeric },
                deepOilWellCost: { requiredIf: requiredIf(() => !isRankOnly()), numeric },
                costEfficiency: {
                    requiredIf: requiredIf(() => !isRankOnly()),
                    numeric,
                    minValue: customMinValue(0.1),
                    maxValue: customMaxValue(1)
                }
            },
            dataQuality: {
                ...validationRules.generalSpecifications.dataQuality,
                specifiedAge: {
                    ...validationRules.generalSpecifications.dataQuality.specifiedAge,
                    requiredIf: requiredIf(
                        () => form.generalSpecifications.dataQuality.handleMissingWellAge === 'specify-value'
                    )
                },
                specifiedDepth: {
                    ...validationRules.generalSpecifications.dataQuality.specifiedDepth,
                    requiredIf: requiredIf(
                        () => form.generalSpecifications.dataQuality.handleMissingDepth === 'specify-value'
                    )
                },
                specifiedAnnualOilProduction: {
                    ...validationRules.generalSpecifications.dataQuality.specifiedAnnualOilProduction,
                    requiredIf: requiredIf(
                        () => form.generalSpecifications.dataQuality.handleMissingProduction === 'specify-value'
                    )
                },
                specifiedLifetimeOilProduction: {
                    ...validationRules.generalSpecifications.dataQuality.specifiedLifetimeOilProduction,
                    requiredIf: requiredIf(
                        () => form.generalSpecifications.dataQuality.handleMissingProduction === 'specify-value'
                    )
                },
                specifiedAnnualGasProduction: {
                    ...validationRules.generalSpecifications.dataQuality.specifiedAnnualGasProduction,
                    requiredIf: requiredIf(
                        () => form.generalSpecifications.dataQuality.handleMissingProduction === 'specify-value'
                    )
                },
                specifiedLifetimeGasProduction: {
                    ...validationRules.generalSpecifications.dataQuality.specifiedLifetimeGasProduction,
                    requiredIf: requiredIf(
                        () => form.generalSpecifications.dataQuality.handleMissingProduction === 'specify-value'
                    )
                },
                specifiedType: {
                    ...validationRules.generalSpecifications.dataQuality.specifiedType,
                    requiredIf: requiredIf(
                        () => form.generalSpecifications.dataQuality.handleMissingType === 'specify-value'
                    )
                }
            },
            solver: {
                ...validationRules.generalSpecifications.solver,
                solverTime: { requiredIf: requiredIf(() => !isRankOnly()), numeric }
            }
        }
    }));

    const v$ = useVuelidate(reactiveRules, form);
    const currentStep = ref<string>('Primo Use Case(s)');

    const hasFormChanged = computed(() => {
        return (
            JSON.stringify(form.generalSpecifications) !== JSON.stringify(lastSubmittedForm.value.generalSpecifications)
        );
    });

    watch([currentStep, hasFormChanged], ([newStep, newChange], [priorStep, priorChange]) => {
        if (
            (newStep == ScenarioFormTitle.ImpactFactors || newStep == ScenarioFormTitle.EfficiencyFactors) &&
            (newChange || availableImpactFactors.value === null || availableEfficiencyFactors.value === null) &&
            newStep != priorStep
        ) {
            getAvailableFactors();
        }
    });

    const getAvailableFactors = async () => {
        try {
            const response = await formService.getAvailableFactors().then((result) => result);
            availableImpactFactors.value = response.impactFactors;
            availableEfficiencyFactors.value = response.efficiencyFactors;
            lastSubmittedForm.value = deepCopy(form);
        } catch (error) {
            console.error(error);
        }
    };

    const validation = useVuelidate(reactiveRules, form);

    const resetForm = () => {
        Object.assign(form, deepCopy(initialScenarioForm));
        validation.value.$reset();
    };

    const resetUseCases = () => {
        form.useCases.cases = [];
    };

    const isCurrentStepValid = computed(() => {
        // v$.value.$touch();
        return !v$.value[stringToCamelCase(currentStep.value)]?.$invalid.value;
    });

    const updateStep = (step: string) => {
        currentStep.value = step;
    };

    const currentStepErrors = computed(() => {
        return v$.value[stringToCamelCase(currentStep.value)]?.$errors.value || [];
    });

    const nestedImpactFactorActive = computed(() => {
        return (
            (form.impactFactors.sensitiveReceptors.selected && form.impactFactors.sensitiveReceptors.value > 0) ||
            (form.impactFactors.losses.selected && form.impactFactors.losses.value > 0) ||
            (form.impactFactors.environment.selected && form.impactFactors.environment.value > 0) ||
            (form.impactFactors.annProductionVolume.selected && form.impactFactors.annProductionVolume.value > 0) ||
            (form.impactFactors.fiveYearProductionVolume.selected &&
                form.impactFactors.fiveYearProductionVolume.value > 0) ||
            (form.impactFactors.lifelongProductionVolume.selected &&
                form.impactFactors.lifelongProductionVolume.value > 0) ||
            (form.impactFactors.siteConsiderations.selected && form.impactFactors.siteConsiderations.value > 0) ||
            (form.impactFactors.ecologicalReceptors.selected && form.impactFactors.ecologicalReceptors.value > 0) ||
            (form.impactFactors.otherLosses.selected && form.impactFactors.otherLosses.value > 0)
        );
    });

    const sumsTo100 = computed(() => (page: string) => {
        const activeStepPropName = stringToCamelCase(page);

        if (activeStepPropName === 'impactFactors' || activeStepPropName === 'efficiencyFactors') {
            let sum = 0;
            const formObject = activeStepPropName === 'impactFactors' ? form.impactFactors : form.efficiencyFactors;

            for (const key in formObject) {
                sum += formObject[key].value;
            }
            return sum === 100;
        } else {
            return true;
        }
    });

    const childrenSumTo100 = computed(() => (parent: string) => {
        if (currentStep.value !== ScenarioFormTitle.ImpactFactors) {
            return true;
        }

        if (
            parent !== 'sensitiveReceptors' &&
            parent !== 'losses' &&
            parent !== 'environment' &&
            parent !== 'annProductionVolume' &&
            parent !== 'fiveYearProductionVolume' &&
            parent !== 'lifelongProductionVolume' &&
            parent !== 'siteConsiderations' &&
            parent !== 'ecologicalReceptors' &&
            parent !== 'otherLosses'
        ) {
            return true;
        }

        const parentFactor = form.impactFactors[parent];

        if (
            !parentFactor.childFactors ||
            parentFactor.value === 0 ||
            parentFactor.selected === false ||
            Object.values(parentFactor.childFactors).length === 0
        ) {
            return true;
        }

        let sum = 0;
        Object.values(parentFactor.childFactors).forEach((child) => {
            sum += child.value;
        });

        return sum === 100;
    });

    const loadParamsFromPreviousScenario = (scenario: ScenarioData, copyScenarioId: number) => {
        clearUserModifications();

        formValueManager.value = new FormValueManager(true, scenario);

        if (scenario.generalSpecifications) {
            form.generalSpecifications = assignMatchingGeneralSpecificationsKeys(
                form.generalSpecifications,
                scenario.generalSpecifications
            );
            form.generalSpecifications.basic.name = '';
        }

        if (scenario.impactFactors) {
            form.impactFactors = deepMergeImpactFactorsPreservingKeys(form.impactFactors, scenario.impactFactors);
        }

        if (scenario.efficiencyFactors) {
            form.efficiencyFactors = deepMergeEfficiencyFactorsPreservingKeys(
                form.efficiencyFactors,
                scenario.efficiencyFactors
            );
        }

        form.copyParentId = copyScenarioId;
    };

    function assignMatchingGeneralSpecificationsKeys(
        target: GeneralSpecificationsInputs,
        source: GeneralSpecifications
    ): GeneralSpecificationsInputs {
        Object.keys(target).forEach((groupKey) => {
            const group = target[groupKey];
            if (typeof group === 'object' && group !== null) {
                Object.keys(group).forEach((fieldKey) => {
                    if (Object.prototype.hasOwnProperty.call(source, fieldKey)) {
                        (target as any)[groupKey][fieldKey] = (source as any)[fieldKey];
                    }
                });
            }
        });

        return target;
    }

    function deepMergeImpactFactorsPreservingKeys(target: ImpactFactors, source: ImpactFactors): ImpactFactors {
        return deepMergeAnyObject(target, source);
    }

    function deepMergeEfficiencyFactorsPreservingKeys(
        target: EfficiencyFactors,
        source: EfficiencyFactors
    ): EfficiencyFactors {
        return deepMergeAnyObject(target, source);
    }

    function deepMergeAnyObject(targetObj: any, sourceObj: any): any {
        for (const key in targetObj) {
            if (Object.prototype.hasOwnProperty.call(sourceObj, key)) {
                if (
                    typeof targetObj[key] === 'object' &&
                    targetObj[key] !== null &&
                    !Array.isArray(targetObj[key]) &&
                    typeof sourceObj[key] === 'object' &&
                    sourceObj[key] !== null &&
                    !Array.isArray(sourceObj[key])
                ) {
                    deepMergeAnyObject(targetObj[key], sourceObj[key]);
                } else {
                    targetObj[key] = sourceObj[key];
                }
            }
        }
        return targetObj;
    }

    function initializeGeneralSpecifications() {
        if (!formValueManager.value) {
            formValueManager.value = new FormValueManager();
        }

        const rankOnly = isRankOnly();

        (
            Object.keys(AFFECTED_FIELDS.generalSpecifications) as Array<
                keyof typeof AFFECTED_FIELDS.generalSpecifications
            >
        ).forEach((sectionKey) => {
            Object.keys(AFFECTED_FIELDS.generalSpecifications[sectionKey]).forEach((fieldKey) => {
                const fieldPath = `generalSpecifications.${sectionKey}.${fieldKey}`;

                // Only update if user hasn't manually modified this field
                if (!userModifiedFields.value.has(fieldPath)) {
                    const newValue = formValueManager.value!.getValueForField(
                        ['generalSpecifications', sectionKey],
                        fieldKey,
                        rankOnly
                    );

                    if (newValue !== undefined) {
                        (form.generalSpecifications as any)[sectionKey][fieldKey] = newValue;
                    }
                }
            });
        });

        hasInitialized.value = true;
    }

    const markFieldAsUserModified = (fieldPath: string) => {
        userModifiedFields.value.add(fieldPath);
    };

    const clearUserModifications = () => {
        userModifiedFields.value.clear();
        hasInitialized.value = false;
    };

    watch(
        () => form.useCases.cases,
        (newCases, oldCases) => {
            // Only initialize if this is the first time or if we're switching between rank-only and other modes
            const wasRankOnly = oldCases?.length === 1 && oldCases[0] === 'MCW Ranking';
            const isNowRankOnly = newCases?.length === 1 && newCases[0] === 'MCW Ranking';

            if (!hasInitialized.value || wasRankOnly !== isNowRankOnly) {
                initializeGeneralSpecifications();
            }
        },
        { deep: true }
    );

    const rankOnly = computed(() => isRankOnly());
    const optimizationOnly = computed(() => isOptimizationOnly());

    return {
        form,
        validation,
        resetForm,
        resetUseCases,
        v$,
        updateStep,
        isCurrentStepValid,
        currentStepErrors,
        sumsTo100,
        childrenSumTo100,
        nestedImpactFactorActive,
        loadParamsFromPreviousScenario,
        rankOnly,
        markFieldAsUserModified,
        optimizationOnly,
        initializeGeneralSpecifications,
        availableImpactFactors,
        availableEfficiencyFactors
    };
});
