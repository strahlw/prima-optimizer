import { ref } from 'vue';
import type { LazyParams } from '../types/pagination';
import type { DataTablePageEvent, DataTableSortEvent } from 'primevue/datatable';

export function setupDatatablePaginationHelper(
    loadLazyData: (event?: DataTablePageEvent | DataTableSortEvent, projectId?: number) => void
) {
    const first = ref<number>(0);
    const loading = ref<boolean>(false);
    const lazyParams = ref<LazyParams>({
        page: 1,
        first: 0,
        rows: 20,
        sortField: null,
        sortOrder: null
    });

    const initializeLoad = () => {
        loading.value = true;
        lazyParams.value = {
            page: 1,
            first: 0,
            rows: 20,
            sortField: null,
            sortOrder: null
        };

        loadLazyData();
    };

    const onSort = (event: DataTableSortEvent, projectId?: number) => {
        const sortField = typeof event.sortField === 'string' ? event.sortField : null;
        const sortOrder = event.sortOrder || null;
        lazyParams.value = {
            page:
                sortField !== lazyParams.value.sortField || sortOrder !== lazyParams.value.sortOrder
                    ? 1
                    : lazyParams.value.page,
            first: event.first,
            rows: event.rows,
            sortField,
            sortOrder: event.sortOrder || null
        };

        loadLazyData(event, projectId);
    };

    const onPage = (event: DataTablePageEvent, projectId?: number) => {
        lazyParams.value = {
            page: event.page + 1,
            first: event.first,
            rows: event.rows,
            sortField: typeof event.sortField === 'string' ? event.sortField : null,
            sortOrder: event.sortOrder || null
        };

        loadLazyData(event, projectId);
    };

    return {
        first,
        loading,
        lazyParams,
        initializeLoad,
        onSort,
        onPage
    };
}
