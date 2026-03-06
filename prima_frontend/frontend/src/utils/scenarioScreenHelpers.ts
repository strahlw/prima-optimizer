import { ref, computed } from 'vue';
import { createScenarioService } from '@/services/scenarioService';
import { createApiService } from '@/services/apiService';
import { createToastService } from '@/services/toastService';
import { useScenarioStore } from '@/stores/scenarioStore';
import { useOrganizationStore } from '@/stores/organizationStore';
import { useWellOverviewStore } from '@/stores/wellOverviewStore';
import { ScenarioFormTitle, ScenarioType } from '@/constants/scenarioEnums';
import type { PaginationMeta } from '@/types/pagination';

export function parseParam(param: string | string[] | undefined): number | null {
    if (!param) return null;
    return Number(Array.isArray(param) ? param[0] : param);
}

export function setupScenarioScreenServices() {
    return {
        scenarioService: createScenarioService(),
        apiService: createApiService(),
        toastService: createToastService(),
        scenarioStore: useScenarioStore(),
        organizationStore: useOrganizationStore(),
        wellOverviewStore: useWellOverviewStore()
    };
}

// Define some of the standard variables that do not need much modification to make component slimmer
export function setupScenarioScreenVars() {
    const tabKeys: string[] = ['kpi', 'ranking', 'recommendations', 'projects', 'parameters'];
    const view = ref<{ name: string; label: string }>({ name: 'overlay', label: 'Overlay' });
    const viewOptions = [
        { name: 'overlay', label: 'Overlay' },
        { name: 'sideBySide', label: 'Side-by-Side' }
    ];
    const filters = ref<ScenarioFormTitle[]>([]);
    const filterOptions = [
        { name: ScenarioFormTitle.WellRanking, label: ScenarioType.Rank },
        { name: ScenarioFormTitle.PAProjectRecommendations, label: ScenarioType.Recommend },
        { name: ScenarioFormTitle.PAProjectComaprisons, label: ScenarioType.Compare }
    ];
    const activeTab = ref<number>(0);
    const first = ref<number>(0);
    const currentPage = ref<number>(1);
    const rowsPerPage = ref<number>(10);
    const paginationMeta = ref<PaginationMeta>({
        current_page: 1,
        last_page: 1,
        per_page: 10,
        total: 0,
        from: 0,
        to: 0
    });
    const downloadTrigger = ref<number>(0);
    const downloadProcessing = ref<boolean>(false);
    const loading = ref<boolean>(false);
    const initialLoadComplete = ref<boolean>(false);
    const totalRecords = computed(() => paginationMeta.value.total);

    return {
        tabKeys,
        view,
        viewOptions,
        filters,
        filterOptions,
        activeTab,
        currentPage,
        rowsPerPage,
        paginationMeta,
        downloadTrigger,
        downloadProcessing,
        loading,
        initialLoadComplete,
        totalRecords,
        first
    };
}
