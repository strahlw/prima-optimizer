<script setup lang="ts">
    import { ref, type PropType, onMounted, computed } from 'vue';
    import type { MinimalDetailsScenario } from '@/types/scenario';
    import CandidateWellsChart from '@/components/scenario/charts/CandidateWellsChart.vue';
    import BudgetChart from '@/components/scenario/charts/BudgetChart.vue';
    import { useCollapse } from '@/composables/collapse';
    import ImpactFactorsChart from '@/components/scenario/charts/ImpactFactorsChart.vue';
    import EfficiencyFactorsChart from '@/components/scenario/charts/EfficiencyFactorsChart.vue';
    import EfficiencyScoreRangeChart from '@/components/scenario/charts/EfficiencyScoreRangeChart.vue';
    import PriorityScoreRangeChart from '@/components/scenario/charts/PriorityScoreRangeChart.vue';
    import NumberOfProjectsChart from '@/components/scenario/charts/NumberOfProjectsChart.vue';
    import { createScenarioService } from '@/services/scenarioService';
    import type { KpiData } from '@/types/kpi';

    const loading = ref<boolean>(false);
    const collapsed = ref<boolean>(false);
    const { enter, leave } = useCollapse();
    const data = ref<KpiData | null>(null);

    const props = defineProps({
        scenario: {
            required: false,
            type: Object as PropType<MinimalDetailsScenario>
        },
        sideBySide: {
            required: false,
            type: Boolean,
            default: false
        },
        scenarioScreenLoading: {
            required: false,
            type: Boolean,
            default: false
        }
    });

    function toggleCollapse() {
        collapsed.value = !collapsed.value;
    }

    const computedGridClass = computed<string>(function (): string {
        let gridClass = 'lg:grid-cols-2 ';
        gridClass +=
            props.scenario?.isRankOnly || props.scenario?.isRecommendationOnly ? 'xl:grid-cols-3' : 'xl:grid-cols-4';
        return gridClass;
    });

    onMounted(async () => {
        loading.value = true;

        if (!props.scenario) {
            loading.value = false;
            return;
        }

        try {
            const scenarioService = createScenarioService();
            const result = await scenarioService.fetchKpiSummary(props.scenario.id);

            if (result) {
                data.value = result as KpiData;
            }
            loading.value = false;
        } catch (error) {
            console.error(error);
        } finally {
            loading.value = false;
        }
    });
</script>

<template>
    <div class="flex-auto h-full overflow-hidden" id="kpi-summary">
        <div v-if="scenario" class="overflow-visible scenario-detail-view mb-4 p-4 rounded-lg max-w-full bg-white">
            <div
                class="flex flex-col py-0 h-auto relative"
                :class="!scenarioScreenLoading ? 'cursor-pointer' : ''"
                @click="scenarioScreenLoading ? '' : toggleCollapse()"
            >
                <div
                    v-if="scenarioScreenLoading"
                    class="absolute inset-0 flex items-center justify-center bg-white bg-opacity-75 rounded"
                >
                    <i class="pi pi-spin pi-spinner text-lg text-gray-500"></i>
                </div>
                <div class="flex flex-row text-center items-center">
                    <p class="font-bold text-2xl w-full">{{ scenario?.data.name }}</p>
                    <div class="justify-self-end items-center flex flex-row">
                        <i
                            class="justify-self-end mr-2"
                            :class="{
                                'pi pi-chevron-up': collapsed,
                                'pi pi-chevron-down': !collapsed,
                                'text-xs': sideBySide
                            }"
                        ></i>
                    </div>
                </div>
                <div class="flex flex-col gap-10 text-xl my-2">
                    <div class="justify-self-start text-sm" :class="{ 'text-xs': sideBySide }">
                        <div>
                            <span>Uploaded By: </span>
                            <br v-if="sideBySide" />
                            <span class="italic">{{ scenario?.user?.firstName }} {{ scenario?.user?.lastName }}</span>
                        </div>

                        <div>
                            <span>Dataset: </span>
                            <br v-if="sideBySide" />
                            <span class="italic">{{ scenario?.dataset?.name }}</span>
                        </div>

                        <div>
                            <span v-if="scenario?.parent?.data">
                                <br />
                                <span
                                    >Child of:
                                    <router-link
                                        :to="{ path: `/scenarios/${scenario.parent?.id}`, hash: '#projects' }"
                                        target="_blank"
                                        class="router-link"
                                        >{{ scenario.parent?.data.name }}</router-link
                                    ></span
                                >
                            </span>
                        </div>

                        <div>
                            <span v-if="scenario.copyParent?.data">
                                <br />
                                <span
                                    >Modified based on:
                                    <router-link
                                        :to="{
                                            path: `/scenarios/${scenario.copyParent?.id}`,
                                            hash: '#projects'
                                        }"
                                        target="_blank"
                                        class="router-link"
                                        >{{ scenario.copyParent?.data.name }}</router-link
                                    ></span
                                >
                            </span>
                        </div>
                    </div>
                </div>
            </div>

            <div class="py-4">
                <transition name="accordion" @enter="enter" @leave="leave">
                    <div v-show="!collapsed" class="overflow-x-auto">
                        <div class="grid grid-cols-1 gap-4 w-full" :class="sideBySide ? '' : computedGridClass">
                            <CandidateWellsChart :data="data" />
                            <BudgetChart :data="data" :isRankOnly="scenario.isRankOnly" />
                            <ImpactFactorsChart :data="data" :notApplicable="scenario.isRecommendationOnly" />
                            <EfficiencyFactorsChart :data="data" :notApplicable="scenario.isRankOnly" />

                            <div :class="sideBySide ? '' : 'lg:col-span-2 xl:col-span-4'">
                                <div
                                    class="grid grid-cols-1 text-center gap-16 items-center justify-center w-full"
                                    :class="sideBySide ? '' : 'lg:grid-cols-2 xl:grid-cols-3'"
                                >
                                    <PriorityScoreRangeChart :data="data" />

                                    <EfficiencyScoreRangeChart :data="data" />

                                    <NumberOfProjectsChart :data="data" />
                                </div>
                            </div>
                        </div>
                    </div>
                </transition>
            </div>
        </div>
    </div>
</template>
