<script setup lang="ts">
    import { ref, type PropType, onMounted, computed, watch } from 'vue';
    import { useRouter } from 'vue-router';

    import ExportingDataDialog from '@/components/ExportingDataDialog.vue';
    import RankingTable from './RankingTable.vue';
    import type { DataTablePageEvent, DataTableSortEvent } from 'primevue/datatable';

    import { useCollapse } from '@/composables/collapse';
    import { columns } from '@/constants/rankingConstants';
    import { createRankingService } from '@/services/rankingService';
    import { createDownloadService } from '@/services/downloadService';
    import { useRankingStore } from '@/stores/form/rankingStore';
    import type { MinimalDetailsScenario } from '@/types/scenario';
    import { setupDatatablePaginationHelper } from '@/utils/datatablePaginationHelper';

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
        },
        triggerDownload: {
            required: false,
            type: Number,
            default: 0
        }
    });

    const emit = defineEmits(['download-complete']);
    const { enter, leave } = useCollapse();
    const { first, loading, lazyParams, onPage, onSort } = setupDatatablePaginationHelper(loadLazyData);
    const router = useRouter();

    const rankingService = createRankingService();
    const downloadService = createDownloadService();
    const rankingStore = useRankingStore();
    const collapsed = ref<boolean>(false);
    const downloadProcessing = ref<boolean>(false);
    const pendingDownload = ref<boolean>(true);
    const totalRecords = ref<number>();
    const taskId = ref<string | null>(null);

    function navigateToWell(well: any) {
        const routeName = 'well-overview';
        const data = { wellId: well.wellId, datasetId: props.scenario?.dataset?.id };
        const routePath = router.resolve({ name: routeName, query: data }).href;
        window.open(routePath, '_blank');
    }

    const reducedColumns = computed(function () {
        const scenarioId = props.scenario?.id;
        if (typeof scenarioId === 'number' && rankingStore.getScenarioIdMappedRankingData[scenarioId]) {
            return columns.filter((col) =>
                Object.keys(rankingStore.getScenarioIdMappedRankingData[scenarioId][0]).includes(col.key)
            );
        }
        return [];
    });

    function toggleCollapse() {
        collapsed.value = !collapsed.value;
    }

    function loadLazyData(event?: DataTablePageEvent | DataTableSortEvent) {
        loading.value = true;
        lazyParams.value = {
            ...lazyParams.value,
            first: event?.first || first.value
        };

        setTimeout(
            () => {
                if (props.scenario?.id) {
                    rankingService
                        .getRankingData(lazyParams.value, rankingStore.getTaskIdMap[props.scenario?.id])
                        .then((res) => {
                            if (props.scenario?.id) {
                                rankingStore.setScenarioIdMappedRankingData({
                                    ...rankingStore.getScenarioIdMappedRankingData,
                                    [props.scenario?.id]: res.data
                                });
                                taskId.value = res.data[0]?.taskId || null;
                            }
                            totalRecords.value = res.total;
                            if (props.triggerDownload && pendingDownload.value) {
                                pendingDownload.value = false; // Reset pending download state
                                downloadWells();
                            }
                        })
                        .finally(() => {
                            loading.value = false;
                        });
                }

                loading.value = false;
            },
            Math.random() * 1000 + 250
        );
    }

    const downloadWells = async () => {
        downloadProcessing.value = true;

        try {
            if (taskId.value) {
                lazyParams.value = {
                    ...lazyParams.value,
                    wellType: []
                };
                await downloadService.downloadRankedWells(
                    taskId.value,
                    lazyParams.value,
                    reducedColumns.value,
                    props.scenario?.name || 'Ranking Download',
                    props.scenario?.id
                );

                emit('download-complete');
            }
        } catch (error) {
            console.error('Error downloading ranked wells:', error);
        } finally {
            setTimeout(() => {
                downloadProcessing.value = false;
                emit('download-complete');
            }, 500);
        }
    };

    watch(
        () => props.triggerDownload,
        () => {
            if (props.triggerDownload === 0) return; // No download requested
            pendingDownload.value = true; // Reset pending download state
            downloadWells();
        }
    );

    onMounted(() => {
        if (props.scenario?.id && !rankingStore.getTaskIdMap[props.scenario?.id]) {
            loading.value = true;
            rankingService
                .submitScenarioWellRanking(props.scenario?.id || null, false)
                .then(() => {
                    lazyParams.value = {
                        ...lazyParams.value,
                        sortField: 'wellRank'
                    };
                    loadLazyData();
                })
                .catch((error) => {
                    console.error('Error submitting well ranking:', error);
                });
        } else {
            lazyParams.value = {
                ...lazyParams.value,
                sortField: 'wellRank'
            };
            loadLazyData();
        }
    });
</script>

<template>
    <div class="flex-auto h-full overflow-hidden">
        <ExportingDataDialog :isOpen="downloadProcessing" message="Exporting well data..." />
        <div v-if="scenario" class="overflow-visible scenario-detail-view mb-4 p-4 rounded-lg max-w-full bg-white">
            <div
                class="flex flex-col py-0 h-auto relative"
                :class="!loading && !scenarioScreenLoading ? 'cursor-pointer' : ''"
                @click="loading || scenarioScreenLoading ? '' : toggleCollapse()"
            >
                <div
                    v-if="loading || scenarioScreenLoading"
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

            <div>
                <transition name="accordion" @enter="enter" @leave="leave">
                    <div v-if="!collapsed">
                        <div>
                            <div class="col-span-2">
                                <div class="mx-auto">
                                    <div v-if="rankingStore.getScenarioIdMappedRankingData[scenario.id]">
                                        <RankingTable
                                            :existing="true"
                                            :scenarioData="scenario.data"
                                            @page="onPage($event)"
                                            @sort="onSort($event)"
                                            @navigate="navigateToWell($event)"
                                            :ranking-data="rankingStore.getScenarioIdMappedRankingData[scenario.id]"
                                            :lazy-params="lazyParams"
                                            :total-records="totalRecords || 0"
                                            :loading="loading"
                                            :columns="reducedColumns"
                                            :is-recommendation-only="scenario.isRecommendationOnly"
                                        />
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </transition>
            </div>
        </div>
    </div>
</template>
