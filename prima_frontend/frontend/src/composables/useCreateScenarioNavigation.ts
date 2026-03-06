import type { MenuItem } from 'primevue/menuitem';
import { computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { ScenarioFormStep, ScenarioFormTitle } from '@/constants/scenarioEnums';
import UseCasesForm from '@/views/scenario/UseCasesForm.vue';
import GeneralSpecificationsForm from '@/views/scenario/GeneralSpecificationsForm.vue';
import ImpactFactorsForm from '@/views/scenario/ImpactFactorsForm.vue';
import EfficiencyFactorsForm from '@/views/scenario/EfficiencyFactorsForm.vue';
import WellRankingPage from '@/views/scenario/WellRankingPage.vue';
import RunOptimizationReview from '@/views/scenario/RunOptimizationReview.vue';
import PAProjectRecommendations from '@/views/scenario/PAProjectRecommendations.vue';

export function useCreateScenarioNavigation() {
    const route = useRoute();
    const router = useRouter();

    const steps: Array<MenuItem> = [
        {
            title: ScenarioFormTitle.UseCases,
            label: 'PRIMA Use Cases',
            key: ScenarioFormStep.UseCases,
            icon: 'pi-sign-out',
            step: 1,
            component: UseCasesForm
        },
        {
            title: ScenarioFormTitle.GeneralSpecifications,
            label: ScenarioFormTitle.GeneralSpecifications,
            key: ScenarioFormStep.GeneralSpecifications,
            icon: 'pi-cog',
            step: 2,
            component: GeneralSpecificationsForm
        },
        {
            title: ScenarioFormTitle.ImpactFactors,
            label: ScenarioFormTitle.ImpactFactors,
            key: ScenarioFormStep.ImpactFactors,
            icon: 'pi-flag',
            step: 3,
            component: ImpactFactorsForm
        },
        {
            title: ScenarioFormTitle.EfficiencyFactors,
            label: ScenarioFormTitle.EfficiencyFactors,
            key: ScenarioFormStep.EfficiencyFactors,
            icon: 'pi-list-check',
            step: 4,
            component: EfficiencyFactorsForm
        },
        {
            title: ScenarioFormTitle.WellRanking,
            label: ScenarioFormTitle.WellRanking,
            key: ScenarioFormStep.WellRanking,
            icon: 'pi-chart-scatter',
            step: 5,
            component: WellRankingPage
        },
        {
            title: ScenarioFormTitle.PAProjectRecommendations,
            label: ScenarioFormTitle.PAProjectRecommendations,
            key: ScenarioFormStep.PAProjectRecommendations,
            icon: 'pi-star-fill',
            step: 6,
            component: RunOptimizationReview
        },
        {
            title: ScenarioFormTitle.PAProjectComaprisons,
            label: ScenarioFormTitle.PAProjectComaprisons,
            key: ScenarioFormStep.PAProjectComaprisons,
            icon: 'pi-list-check',
            step: 7,
            component: PAProjectRecommendations
        }
    ];

    const activeStep = computed<MenuItem>(() => {
        const foundStep = steps.find((step) => step.key === route.name);
        return foundStep || steps[0];
    });

    const previousStep = () => {
        if (activeStep.value.key !== steps[0].key) router.back();
    };

    return { steps, activeStep, previousStep, route };
}
