<script setup lang="ts">
    import { computed, onMounted, ref, watch } from 'vue';

    import WellData from '@/components/maps/WellData.vue';
    import RankingTable from '@/components/scenario/RankingTable.vue';
    import ExportingDataDialog from '@/components/ExportingDataDialog.vue';

    import { deepCopy } from '@/utils/deepCopy';
    import type { ScenarioForm } from '@/types/scenarioForm/scenarioForm';

    import { setupDatatablePaginationHelper } from '@/utils/datatablePaginationHelper';
    import { setupWellRankingPage } from '@/utils/componentSetupHelpers';
    const {
        formService,
        rankingService,
        downloadService,
        wellOverviewService,
        rankingStore,
        scenarioFormStore,
        wellOverviewStore,
        router
    } = setupWellRankingPage();
    const { loading, lazyParams, onPage, onSort } = setupDatatablePaginationHelper(loadLazyData);

    import { type DataTablePageEvent, type DataTableSortEvent } from 'primevue/datatable';
    import { deepEqual } from '@/utils/deepEqual';
    import { columns } from '@/constants/rankingConstants';

    const priorSortField = ref<string | null>('wellRank');
    const priorSortOrder = ref<number | null>(1);

    const reducedColumns = computed(() =>
        columns.filter((col) => Object.keys(rankingStore.rankingData[0]).includes(col.key))
    );

    const downloadProcessing = ref<boolean>(false);
    const totalRecords = ref<number>();
    const selectedWellTypes = ref<string[]>([]);
    const filteredWellTypeOptions = computed(() => {
        const selectedWellTypes = scenarioFormStore.form.generalSpecifications.basic.wellType;
        const hasGas = selectedWellTypes.includes('Gas');
        const hasOil = selectedWellTypes.includes('Oil');

        const options = [];

        if (hasGas) options.push({ label: 'DOW', value: 'Gas' });
        if (hasOil) options.push({ label: 'LUOW', value: 'Oil' });
        // if (hasGas && hasOil) options.push({ label: 'Gas and Oil', value: 'Oil and Gas' });

        return options;
    });

    const selectedSelectType = ref<string>('Ranking');
    const selectTypeOptions = ['Ranking', 'Raw Data'];

    function navigateToWell(well: any) {
        const routeName = 'well-overview';
        const data = { wellId: well.wellId, datasetId: scenarioFormStore.form.generalSpecifications.basic.datasetId };
        const routePath = router.resolve({ name: routeName, query: data }).href;
        window.open(routePath, '_blank');
    }

    onMounted(() => {
        lazyParams.value = {
            ...lazyParams.value,
            sortField: 'wellRank'
        };
        if (rankingStore.taskId === '') {
            loading.value = true;
            const formData: ScenarioForm = deepCopy(scenarioFormStore.form);
            rankingStore.setScenarioData(formData);
            formService
                .submitWellRanking()
                .then(() => {
                    loadLazyData();
                })
                .catch((error) => {
                    console.error('Error submitting well ranking:', error);
                });
        } else {
            if (deepEqual(rankingStore.createScenarioData, scenarioFormStore.form)) {
                loadLazyData();
            } else {
                loading.value = true;
                formService
                    .submitWellRanking()
                    .then(() => {
                        loadLazyData();
                    })
                    .catch((error) => {
                        console.error('Error submitting well ranking:', error);
                    });
            }
        }
    });

    function loadLazyData(event?: DataTablePageEvent | DataTableSortEvent) {
        loading.value = true;
        lazyParams.value = {
            ...lazyParams.value,
            first: event ? event?.first : lazyParams.value.first,
            wellType: selectedWellTypes.value
        };

        setTimeout(
            async () => {
                await rankingService
                    .getRankingData(lazyParams.value)
                    .then((res) => {
                        rankingStore.setRankingData(res.data);
                        totalRecords.value = res.total;
                    })
                    .finally(() => {
                        loading.value = false;
                    });

                loading.value = false;
            },
            Math.random() * 1000 + 250
        );
    }

    const handleWellDataSort = (sortField: string, sortOrder: number | null) => {
        lazyParams.value = {
            ...lazyParams.value,
            sortField: sortField,
            sortOrder: sortOrder
        };
    };

    const handleWellDataPage = (event: DataTablePageEvent) => {
        lazyParams.value = {
            ...lazyParams.value,
            first: event.first,
            page: event.page + 1
        };
    };

    watch(selectedWellTypes, () => {
        loadLazyData();
    });

    // When visting the ranking page, check if the sort field or order has changed, if so, reload the data
    watch(selectedSelectType, () => {
        if (selectedSelectType.value === 'Ranking') {
            if (
                priorSortField.value !== lazyParams.value.sortField ||
                priorSortOrder.value !== lazyParams.value.sortOrder
            ) {
                loadLazyData();
                priorSortField.value = lazyParams.value.sortField;
                priorSortOrder.value = lazyParams.value.sortOrder;
            }
        }
    });

    const downloadWells = async () => {
        downloadProcessing.value = true;

        try {
            if (selectedSelectType.value === 'Ranking') {
                await downloadService.downloadRankedWells(
                    rankingStore.taskId,
                    lazyParams.value,
                    reducedColumns.value,
                    scenarioFormStore.form.generalSpecifications.basic.name
                );
            } else {
                if (wellOverviewStore.getDataset && wellOverviewService.getComputedColumns().length) {
                    if (
                        lazyParams.value.sortField &&
                        !wellOverviewService
                            .getComputedColumns()
                            .map((col) => col?.key)
                            .includes(lazyParams.value.sortField)
                    ) {
                        lazyParams.value = {
                            ...lazyParams.value,
                            taskId: rankingStore.getTaskId
                        };
                    }

                    await downloadService.downloadRawWells(
                        wellOverviewStore.getDataset.id,
                        {
                            ...lazyParams.value
                        },
                        wellOverviewService.getComputedColumns(),
                        wellOverviewStore.getDataset.name
                    );
                }
            }
        } catch (error) {
            console.error('Error downloading wells:', error);
        } finally {
            setTimeout(() => {
                downloadProcessing.value = false;
            }, 1000);
        }
    };
</script>

<template>
    <div class="flex-auto">
        <ExportingDataDialog :isOpen="downloadProcessing" message="Exporting well data..." />
        <PCard class="no-border-card">
            <template #content>
                <div class="flex flex-row justify-between items-center font-bold w-100 gap-8">
                    <!-- Well Type Dropdown -->

                    <div class="flex flex-row items-center">
                        <label for="wellType" class="my-auto mr-1">Well Type:</label>
                        <MultiSelect
                            id="wellType"
                            v-model="selectedWellTypes"
                            :options="filteredWellTypeOptions"
                            optionLabel="label"
                            optionValue="value"
                            class="w-44 ml-2"
                            :filter="false"
                        />
                    </div>

                    <div class="flex flex-row items-center">
                        <label for="selectType" class="mr-2">Type:</label>
                        <SelectButton
                            id="selectType"
                            v-model="selectedSelectType"
                            :options="selectTypeOptions"
                            class="w-full"
                        />
                    </div>

                    <PButton
                        :class="{ 'bg-gray-400': downloadProcessing }"
                        class="font-bold"
                        @click="downloadWells"
                        :disabled="downloadProcessing"
                        title="Download Wells"
                        aria-label="Download wells"
                        :loading="downloadProcessing"
                    >
                        <span>Export</span>
                        <i class="pi pi-download ml-2"></i>
                    </PButton>
                </div>

                <div class="flex-grow flex min-w-0 items-center mt-10" v-if="selectedSelectType === 'Raw Data'">
                    <WellData
                        class="w-full"
                        :newTab="true"
                        :emitSortToParent="true"
                        :emitPageToParent="true"
                        :parentLazyParams="lazyParams"
                        :wellTypes="selectedWellTypes"
                        @sort="handleWellDataSort"
                        @page="handleWellDataPage"
                    />
                </div>

                <div v-else class="mx-auto mt-10">
                    <PCard>
                        <template #header>
                            <div class="flex flex-col items-left py-2 px-10 h-auto card-header cursor-pointer">
                                <div class="flex flex-row justify-between text-lg">
                                    <p class="text-md font-bold mt-0 mb-1">Well Rank</p>
                                </div>
                            </div>
                        </template>
                        <template #content>
                            <div class="overflow-hidden">
                                <div
                                    v-if="loading && rankingStore.rankingData.length === 0"
                                    class="flex justify-center items-center"
                                >
                                    <ProgressSpinner />
                                </div>
                                <div v-if="rankingStore.rankingData.length > 0">
                                    <RankingTable
                                        @page="onPage($event)"
                                        @sort="onSort($event)"
                                        @navigate="navigateToWell($event)"
                                        :ranking-data="rankingStore.rankingData"
                                        :lazy-params="lazyParams"
                                        :total-records="totalRecords || 0"
                                        :loading="loading"
                                        :columns="reducedColumns"
                                        :is-recommendation-only="scenarioFormStore.optimizationOnly"
                                    />
                                </div>
                            </div>
                        </template>
                    </PCard>
                </div>
            </template>
        </PCard>
    </div>
</template>

<style scoped>
    .accordion-enter-active,
    .accordion-leave-active {
        transition: max-height 0.5s ease-in-out;
    }
    .accordion-enter,
    .accordion-leave-to {
        max-height: 0;
    }
    .no-border-card {
        border: none;
        box-shadow: none; /* If you also want to remove any shadow */
    }
</style>
