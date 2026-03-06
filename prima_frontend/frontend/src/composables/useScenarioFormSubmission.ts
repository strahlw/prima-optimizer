// composables/useScenarioFormSubmission.ts
import { computed, type ComputedRef } from 'vue';
import type { MenuItem } from 'primevue/menuitem';
import { useRouter } from 'vue-router';
import { ScenarioFormStep, ScenarioFormTitle } from '@/constants/scenarioEnums';
import { stringToCamelCase } from '@/utils/toCamelCase';
import { useScenarioFormStore } from '@/stores/form/scenarioForm';
import { createFormService } from '@/services/formService';

export function useScenarioFormSubmission(steps: Array<MenuItem>, activeStep: ComputedRef<MenuItem>) {
    const router = useRouter();
    const formService = createFormService();
    const scenarioFormStore = useScenarioFormStore();

    const currentStepInvalid = computed<boolean>(() => {
        if (
            activeStep.value.key !== ScenarioFormStep.PAProjectRecommendations &&
            activeStep.value.key !== ScenarioFormStep.GeneralSpecifications
        ) {
            return scenarioFormStore.v$[stringToCamelCase(activeStep.value.title)]?.$invalid;
        } else if (activeStep.value.key === ScenarioFormStep.GeneralSpecifications) {
            return scenarioFormStore.v$.generalSpecifications.$invalid;
        } else {
            return true;
        }
    });

    const isRankOnly = computed(
        () =>
            scenarioFormStore.form.useCases.cases.length === 1 &&
            scenarioFormStore.form.useCases.cases.includes(ScenarioFormTitle.WellRanking) &&
            activeStep.value.step > 1
    );

    const isOptimizationOnly = computed(
        () =>
            scenarioFormStore.form.useCases.cases.length === 1 &&
            scenarioFormStore.form.useCases.cases.includes(ScenarioFormTitle.PAProjectRecommendations) &&
            activeStep.value.step > 1
    );

    const acceptConfirmation = async () => {
        // TODO: Add message about email being sent out when optimization is run (if relevant); (?)
        await formService.submitScenarioForm();
        const recommendationsStep = steps.find((step) => step.key === ScenarioFormStep.PAProjectRecommendations);
        if (recommendationsStep) {
            router.push(`/create-scenario/${recommendationsStep.key}`);
        }
    };

    const handleNext = async () => {
        if (currentStepInvalid.value) return;

        switch (activeStep.value.key) {
            case ScenarioFormStep.GeneralSpecifications:
                if (isOptimizationOnly.value) {
                    const nextKey = steps.find((step) => step.key === ScenarioFormStep.EfficiencyFactors);
                    if (nextKey) {
                        router.push(`/create-scenario/${nextKey.key}`);
                        return;
                    }
                }
                break;
            case ScenarioFormStep.ImpactFactors:
                if (isRankOnly.value) {
                    const data = await formService.submitRankOnlyScenarioForm();
                    router.push({
                        name: 'scenarios',
                        params: {
                            scenarioId: data.id,
                            organizationId: data.organizationId
                        },
                        hash: '#ranking'
                    });
                    return;
                }
                break;
        }

        router.push(`/create-scenario/${steps[activeStep.value.step].key}`);
    };

    const disabledDueToChildFactors = computed<boolean>(() => {
        return (
            !scenarioFormStore.childrenSumTo100('losses') ||
            !scenarioFormStore.childrenSumTo100('sensitiveReceptors') ||
            !scenarioFormStore.childrenSumTo100('environment') ||
            !scenarioFormStore.childrenSumTo100('annProductionVolume') ||
            !scenarioFormStore.childrenSumTo100('fiveYearProductionVolume') ||
            !scenarioFormStore.childrenSumTo100('lifelongProductionVolume') ||
            !scenarioFormStore.childrenSumTo100('siteConsiderations') ||
            !scenarioFormStore.childrenSumTo100('ecologicalReceptors') ||
            !scenarioFormStore.childrenSumTo100('otherLosses')
        );
    });

    return {
        currentStepInvalid,
        isRankOnly,
        isOptimizationOnly,
        acceptConfirmation,
        handleNext,
        disabledDueToChildFactors
    };
}
