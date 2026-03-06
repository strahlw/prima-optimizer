<script lang="ts" setup>
    import { computed } from 'vue';
    import type { RouteLocationNormalizedLoadedGeneric } from 'vue-router';
    import { ScenarioFormStep, ScenarioFormTitle } from '@/constants/scenarioEnums';
    import type { MenuItem } from 'primevue/menuitem';

    const emit = defineEmits<{
        (e: 'previousStep'): void;
        (e: 'handleNext'): void;
        (e: 'showConfirmation'): void;
    }>();

    const props = defineProps<{
        route: RouteLocationNormalizedLoadedGeneric;
        isRankOnly: boolean;
        isOptimizationOnly: boolean;
        currentStepInvalid: boolean;
        disabledDueToChildFactors: boolean;
        activeStep: MenuItem;
        scenarioFormInvalid: boolean;
        impactFactorsSumto100: boolean;
        efficiencyFactorsSumto100: boolean;
    }>();

    const routeName = computed(() => props.route.name as ScenarioFormStep);

    const wellRankingVisible = computed<boolean>(() => {
        return (
            routeName.value === ScenarioFormStep.EfficiencyFactors ||
            routeName.value === ScenarioFormStep.WellRanking ||
            (routeName.value === ScenarioFormStep.ImpactFactors && props.isRankOnly)
        );
    });

    const wellRankingDisabled = computed<boolean>(() => {
        return (
            props.scenarioFormInvalid ||
            !props.impactFactorsSumto100 ||
            (!props.isRankOnly && !props.efficiencyFactorsSumto100) ||
            props.disabledDueToChildFactors
        );
    });

    const recommendProjectsVisible = computed<boolean>(() => {
        return !(routeName.value === ScenarioFormStep.ImpactFactors && props.isRankOnly);
    });

    const recommendProjectsDisabled = computed<boolean>(() => {
        return (
            props.scenarioFormInvalid ||
            !props.efficiencyFactorsSumto100 ||
            props.disabledDueToChildFactors ||
            (!props.isOptimizationOnly && !props.impactFactorsSumto100)
        );
    });

    const nextVisible = computed<boolean>(() => {
        return (
            routeName.value !== ScenarioFormStep.EfficiencyFactors &&
            routeName.value !== ScenarioFormStep.WellRanking &&
            !(routeName.value === ScenarioFormStep.ImpactFactors && props.isRankOnly) &&
            !(routeName.value === ScenarioFormStep.PAProjectRecommendations && props.isOptimizationOnly)
        );
    });

    const currentStepSumsTo100 = computed<boolean>(() => {
        if (routeName.value === ScenarioFormStep.ImpactFactors) {
            return props.impactFactorsSumto100;
        }

        if (routeName.value === ScenarioFormStep.EfficiencyFactors) {
            return props.efficiencyFactorsSumto100;
        }

        return true;
    });

    const nextDisabled = computed<boolean>(() => {
        return (
            (routeName.value !== ScenarioFormStep.PAProjectRecommendations && props.currentStepInvalid) ||
            !currentStepSumsTo100.value ||
            props.disabledDueToChildFactors
        );
    });
</script>

<template>
    <div class="flex flex-row mt-10 w-full justify-self-center justify-center gap-10">
        <PButton
            v-if="route.name !== ScenarioFormStep.RunOptimizationReview && route.name !== ScenarioFormStep.UseCases"
            class="justify-center p-3 font-bold w-1/3"
            severity="secondary"
            @click="emit('previousStep')"
            ><div>Back</div></PButton
        >
        <template v-if="wellRankingVisible">
            <PButton
                v-if="route.name !== 'well-ranking' && !isOptimizationOnly"
                class="justify-center btn-secondary p-3 font-bold w-1/3"
                @click="emit('handleNext')"
                :disabled="wellRankingDisabled"
            >
                <div>Rank Orphaned Wells</div>
            </PButton>
            <PButton
                class="btn-secondary justify-center p-3 font-bold w-1/3"
                @click="emit('showConfirmation')"
                v-if="recommendProjectsVisible"
                :disabled="recommendProjectsDisabled"
            >
                <div>Recommend P&A Projects</div>
            </PButton>
        </template>

        <PButton
            v-if="nextVisible"
            class="btn-secondary justify-center p-3 font-bold w-1/3"
            @click="emit('handleNext')"
            :disabled="nextDisabled || route.name === ScenarioFormStep.PAProjectRecommendations"
            ><div>
                {{
                    route.name === ScenarioFormStep.PAProjectRecommendations
                        ? ScenarioFormTitle.PAProjectComaprisons
                        : 'Next'
                }}
            </div>
        </PButton>
    </div>
</template>
