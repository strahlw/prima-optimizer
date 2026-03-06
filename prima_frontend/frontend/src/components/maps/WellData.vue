<script setup lang="ts">
    import { computed, onMounted, ref, watch } from 'vue';
    import type { PropType } from 'vue';
    import { useRouter } from 'vue-router';
    import { useWellOverviewStore } from '@/stores/wellOverviewStore';
    import { createWellOverviewService } from '@/services/wellOverviewService';
    import { useRankingStore } from '@/stores/form/rankingStore';

    import { type DataTablePageEvent, type DataTableSortEvent } from 'primevue/datatable';
    import type { LazyParams } from '@/types/pagination';
    import type { DatasetJson } from '@/types/dataset';

    const wellOverviewStore = useWellOverviewStore();
    const wellOverviewService = createWellOverviewService();
    const rankingStore = useRankingStore();
    const router = useRouter();

    const props = defineProps({
        newTab: {
            type: Boolean,
            required: false,
            default: false
        },
        emitSortToParent: {
            type: Boolean,
            required: false,
            default: false
        },
        emitPageToParent: {
            type: Boolean,
            required: false,
            default: false
        },
        parentLazyParams: {
            type: Object as PropType<LazyParams>,
            required: false,
            default: null
        },
        wellTypes: {
            type: Array as PropType<string[]>,
            required: false,
            default: () => []
        }
    });

    const columns = computed(() => wellOverviewService.getComputedColumns());

    const emit = defineEmits(['changeTab', 'sort', 'page']);
    const loading = ref<boolean>(false);
    const first = ref<number>(0);
    const totalRecords = ref<number>();
    const lazyParams = ref<LazyParams>({
        page: 1,
        first: 0,
        rows: 20,
        sortField: null,
        sortOrder: null
    });

    const navigateToWell = (dataset: DatasetJson) => {
        if (props.newTab) {
            const routeName = 'well-overview';
            const data = {
                wellId: dataset.wellId.value,
                datasetId: wellOverviewStore.getDataset?.id
            };
            const routePath = router.resolve({ name: routeName, query: data }).href;
            window.open(routePath, '_blank');
        } else {
            emit('changeTab', dataset);
        }
    };

    onMounted(() => {
        if (wellOverviewStore.getDataset !== null) {
            loading.value = true;

            lazyParams.value = {
                page: props.parentLazyParams?.page || 1,
                first: props.parentLazyParams?.first || 0,
                rows: 20,
                sortField: props.parentLazyParams?.sortField || null,
                sortOrder: props.parentLazyParams?.sortOrder || null
            };

            loadLazyData();
        }
    });

    const loadLazyData = (event?: DataTablePageEvent | DataTableSortEvent) => {
        loading.value = true;
        if (lazyParams.value.sortField && !columns.value.map((col) => col?.key).includes(lazyParams.value.sortField)) {
            lazyParams.value = {
                ...lazyParams.value,
                taskId: rankingStore.getTaskId
            };
        }

        lazyParams.value = {
            ...lazyParams.value,
            first: event ? event?.first : props.parentLazyParams?.first || first.value,
            wellType: props.wellTypes && props.wellTypes.length ? props.wellTypes : undefined
        };

        setTimeout(
            () => {
                wellOverviewService
                    .getWells(lazyParams.value)
                    .then((res) => {
                        wellOverviewStore.setJsonData(res.data);
                        totalRecords.value = res.total;
                    })
                    .finally(() => {
                        loading.value = false;
                    });

                loading.value = false;
            },
            Math.random() * 1000 + 250
        );
    };

    const onPage = (event: DataTablePageEvent) => {
        lazyParams.value = {
            page: event.page + 1,
            first: event.first,
            rows: event.rows,
            sortField: typeof event.sortField === 'string' ? event.sortField : null,
            sortOrder: event.sortOrder || null
        };
        if (props.emitSortToParent) {
            emit('page', event);
        }
        loadLazyData(event);
    };

    const onSort = (event: DataTableSortEvent) => {
        const sortField = typeof event.sortField === 'string' ? event.sortField : null;
        wellOverviewStore.setWellDataSortField(sortField);
        wellOverviewStore.setWellDataSortOrder(event.sortOrder || null);
        lazyParams.value = {
            page: sortField != lazyParams.value.sortField ? 1 : lazyParams.value.page,
            first: event.first,
            rows: event.rows,
            sortField: sortField,
            sortOrder: event.sortOrder || null
        };
        if (props.emitSortToParent) {
            emit('sort', sortField, event.sortOrder || null);
        }
        loadLazyData(event);
    };

    watch(
        () => props.parentLazyParams,
        (newVal) => {
            if (!newVal) return;

            wellOverviewStore.setWellDataSortField(newVal.sortField);
            wellOverviewStore.setWellDataSortOrder(newVal.sortOrder);

            lazyParams.value = {
                ...lazyParams.value,
                sortField: newVal.sortField,
                sortOrder: newVal.sortOrder
            };
        },
        { immediate: true }
    );

    watch(
        () => props.wellTypes,
        () => {
            loadLazyData();
        }
    );
</script>

<template>
    <PCard>
        <template #header>
            <div class="flex flex-col items-left py-2 px-10 h-auto card-header cursor-pointer">
                <div class="flex flex-row justify-between text-lg">
                    <p class="text-md font-bold mt-0 mb-1">Well Data</p>
                </div>
                <div class="flex flex-row justify-between">
                    <p class="text-sm my-0 italic">
                        Uploaded By: {{ wellOverviewStore.getDataset?.user?.firstName }}
                        {{ wellOverviewStore.getDataset?.user?.lastName }}
                    </p>
                    <p class="text-sm my-0">
                        Uploaded On:
                        {{
                            wellOverviewStore.getDataset?.createdAt
                                ? new Date(wellOverviewStore.getDataset?.createdAt).toLocaleDateString()
                                : ''
                        }}
                    </p>
                </div>
            </div>
        </template>
        <template #content>
            <div class="overflow-hidden">
                <div v-if="wellOverviewStore.jsonData.length > 0">
                    <DataTable
                        :sortField="wellOverviewStore.getWellDataSortField || 'wellId'"
                        :sortOrder="wellOverviewStore.getWellDataSortOrder || 1"
                        :value="wellOverviewStore.jsonData"
                        :first="lazyParams.first"
                        size="small"
                        dataKey="key"
                        showGridlines
                        lazy
                        paginator
                        :totalRecords="totalRecords"
                        :loading="loading"
                        @page="onPage($event)"
                        @sort="onSort($event)"
                        :rows="20"
                        :pt="{
                            header: { class: 'border-none' },
                            headerRow: { class: 'bg-primary' },
                            columnTitle: { class: 'text-white' },
                            thead: { class: 'bg-primary' },
                            column: { class: 'bg-primary-500' },
                            tableContainer: { class: 'rounded-t-lg' }
                        }"
                    >
                        <template #header>
                            <div class="font-bold">{{ wellOverviewStore.getDataset?.name }}</div>
                        </template>
                        <PColumn
                            label="Map"
                            :pt="{
                                headerCell: { class: 'bg-primary border-l-0' },
                                headerTitle: { class: 'text-slate-50 text-sm' }
                            }"
                        >
                            <template #body="slotProps">
                                <i
                                    class="pi pi-map text-secondary cursor-pointer"
                                    @click="navigateToWell(slotProps.data)"
                                >
                                </i>
                            </template>
                        </PColumn>
                        <PColumn
                            :sortable="true"
                            :pt="{
                                headerCell: { class: 'bg-primary border-l-0' },
                                headerTitle: {
                                    class: 'w-auto overflow-visible text-sm text-white'
                                },
                                sortIcon: { class: 'text-white' }
                            }"
                            v-for="col in columns"
                            :key="col?.key"
                            :field="`${col?.key}.value`"
                            :sortField="col?.key"
                            :header="col?.header"
                        ></PColumn>
                    </DataTable>
                </div>
            </div>
        </template>
    </PCard>
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
</style>
