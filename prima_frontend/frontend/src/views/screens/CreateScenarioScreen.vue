<script setup lang="ts">
    import { Dialog, Message } from 'primevue';
    import { ScenarioFormTitle } from '@/constants/scenarioEnums';
    import ScenarioFormProgressBar from '../scenario/ScenarioFormProgressBar.vue';
    import ScenarioFormNavigation from '@/components/forms/ScenarioFormNavigation.vue';
    import { ref, watch, computed, onUnmounted, onMounted } from 'vue';
    import { useRoute, useRouter } from 'vue-router';
    import { useCreateScenarioNavigation } from '@/composables/useCreateScenarioNavigation';
    import { useScenarioFormSubmission } from '@/composables/useScenarioFormSubmission';

    import { createRankingService } from '@/services/rankingService';
    import { createScenarioService } from '@/services/scenarioService';
    import { createDatasetService } from '@/services/datasetService';
    import { useScenarioFormStore } from '@/stores/form/scenarioForm';
    import { useOrganizationStore } from '@/stores/organizationStore';
    import { autoloadScenarioData } from '@/utils/autoloadScenarioData';

    const confirmVisible = ref<boolean>(false);
    const loading = ref<boolean>(false);
    const formValid = ref<boolean>(false);
    const rankOnlyDatasets = ref<boolean>(false);
    const route = useRoute();
    const router = useRouter();

    const scenarioFormStore = useScenarioFormStore();
    const orgStore = useOrganizationStore();
    const rankingService = createRankingService();
    const scenarioService = createScenarioService();
    const datasetService = createDatasetService();
    const { updateStep, resetForm, resetUseCases } = scenarioFormStore;
    const { steps, activeStep, previousStep } = useCreateScenarioNavigation();
    const {
        currentStepInvalid,
        isRankOnly,
        isOptimizationOnly,
        acceptConfirmation,
        handleNext,
        disabledDueToChildFactors
    } = useScenarioFormSubmission(steps, activeStep);

    watch(
        () => route.name,
        () => {
            if (typeof activeStep.value.label === 'string') {
                updateStep(activeStep.value.label);
            }
        }
    );

    const resetScenarioForm = () => {
        resetForm();
        router.push(`/create-scenario/${steps[0].key}`);
    };

    const handleFormValidityChanged = (isValid: boolean) => {
        formValid.value = isValid;
    };

    const handleConfirmation = async () => {
        confirmVisible.value = false;
        acceptConfirmation();
    };

    const fetchDatasets = async (orgId: number | null = null) => {
        if (orgId) {
            loading.value = true;
            const mustContainRanking = scenarioFormStore.optimizationOnly;
            const response = await datasetService.getDatasets(orgId, mustContainRanking);
            if (response) {
                orgStore.setOrganizationDatasets(response.wellData);
                orgStore.setOrganizationAdditionalDatasets(response.additionalData);
                loading.value = false;
            }
        }
    };

    watch(
        () => scenarioFormStore.form.generalSpecifications.basic.organizationId,
        async (newOrgId: number | null, oldOrgId: number | null) => {
            try {
                if (newOrgId !== oldOrgId && newOrgId) {
                    await fetchDatasets(newOrgId);
                }
            } catch (error) {
                loading.value = false;
                console.error(error);
            }
        }
    );

    watch(
        () => scenarioFormStore.form.useCases,
        async () => {
            if (scenarioFormStore.form.generalSpecifications.basic.organizationId) {
                const oldValue = rankOnlyDatasets.value;
                try {
                    if (scenarioFormStore.optimizationOnly && !rankOnlyDatasets.value) {
                        rankOnlyDatasets.value = true;
                        await fetchDatasets(scenarioFormStore.form.generalSpecifications.basic.organizationId);
                    } else if (!scenarioFormStore.optimizationOnly && rankOnlyDatasets.value) {
                        rankOnlyDatasets.value = false;
                        await fetchDatasets(scenarioFormStore.form.generalSpecifications.basic.organizationId);
                    }
                } catch (error) {
                    console.error(error);
                    rankOnlyDatasets.value = oldValue;
                }
            }
        },
        { immediate: true, deep: true }
    );

    const confirmOptimizationDisabled = computed<boolean>(() => {
        return (
            scenarioFormStore.v$.$invalid ||
            (!scenarioFormStore.sumsTo100(ScenarioFormTitle.ImpactFactors) && !isOptimizationOnly.value) ||
            !scenarioFormStore.sumsTo100(ScenarioFormTitle.EfficiencyFactors) ||
            disabledDueToChildFactors.value
        );
    });

    onUnmounted(() => {
        resetUseCases();
        rankingService.resetRankingData();
    });

    onMounted(async () => {
        if (route.query.copy) {
            loading.value = true;
            const copyParam = Array.isArray(route.query.copy) ? route.query.copy[0] : route.query.copy;
            const copyId = Number(copyParam);
            if (!isNaN(copyId)) {
                try {
                    const response = await scenarioService.fetchScenarioParams(copyId);
                    if (response.data) {
                        scenarioFormStore.loadParamsFromPreviousScenario(response.data, copyId);
                    }
                } catch (error) {
                    console.error('Error fetching scenario data:', error);
                }
            }
            loading.value = false;
            return;
        }

        // Local utility to autoload data for troubleshooting / development
        if (import.meta.env.VITE_APP_ENV === 'local' && !scenarioFormStore.form.generalSpecifications.basic.name) {
            autoloadScenarioData(scenarioFormStore);
            return;
        }
    });
</script>
<template>
    <span>
        <div v-if="loading" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center">
            <ProgressSpinner
                style="width: 50px; height: 50px"
                strokeWidth="4"
                animationDuration=".5s"
                aria-label="Loading"
            />
        </div>

        <Dialog v-model:visible="confirmVisible" modal header="Confirm Optimization" :style="{ width: '30rem' }">
            <span v-if="confirmOptimizationDisabled">
                <Message severity="error" :closable="false" icon="pi pi-times-circle"
                    >The form is not filled out correctly or is missing required fields, please review the steps before
                    running the optimization.</Message
                ></span
            >
            <span v-else>
                <Message severity="warn" :closable="false" icon="pi pi-exclaimation-triangle"
                    >Are you sure you want to run this optimization?</Message
                >
            </span>

            <template #footer>
                <PButton
                    label="Cancel"
                    class="p-button-secondary p-button-outlined"
                    @click="confirmVisible = false"
                ></PButton>
                <PButton label="Run" @click="handleConfirmation" :disabled="confirmOptimizationDisabled"> </PButton>
            </template>
        </Dialog>

        <div class="grid grid-cols-4 w-full mx-auto gap-1">
            <ScenarioFormProgressBar
                :steps="steps"
                :activeStep="activeStep.key || ''"
                class="col-span-1"
                :rankOnly="isRankOnly"
                :optimizationOnly="isOptimizationOnly"
            />
            <PCard
                :pt="{
                    root: { class: 'mt-10 w-full col-span-3 max-w-screen-lg h-fit overflow-scroll md:overflow-auto' },
                    body: { class: 'px-10' }
                }"
            >
                <template #header>
                    <div class="flex justify-center w-full">
                        <h1 class="flex-wrap overflow-hidden w-full text-center pt-6">
                            {{ activeStep.label }}
                        </h1>
                    </div>
                </template>
                <template #content>
                    <router-view
                        @create-new-scenario="resetScenarioForm"
                        @formValidityChanged="handleFormValidityChanged"
                        :scenarioId="scenarioFormStore.form.id"
                    ></router-view>

                    <ScenarioFormNavigation
                        :route="route"
                        :isRankOnly="isRankOnly"
                        :isOptimizationOnly="isOptimizationOnly"
                        :disabledDueToChildFactors="disabledDueToChildFactors"
                        :activeStep="activeStep"
                        :currentStepInvalid="currentStepInvalid"
                        :scenarioFormInvalid="scenarioFormStore.v$.$invalid"
                        :impactFactorsSumto100="scenarioFormStore.sumsTo100(ScenarioFormTitle.ImpactFactors)"
                        :efficiencyFactorsSumto100="scenarioFormStore.sumsTo100(ScenarioFormTitle.EfficiencyFactors)"
                        @previousStep="previousStep"
                        @handleNext="handleNext"
                        @showConfirmation="confirmVisible = true"
                    />
                </template>
            </PCard>
        </div>
    </span>
</template>
