import { createApiService } from './apiService';
import { createToastService } from '@/services/toastService';
import { useRouter } from 'vue-router';
import type { LazyParams } from '../types/pagination';
import type { OverrideData } from '../types/scenario';

export function createScenarioService() {
    const apiService = createApiService();
    const router = useRouter();
    const toastService = createToastService();
    const { toastError, toastSuccess, removeAllToast } = toastService;

    const publishScenario = async (scenarioId: number) => {
        try {
            removeAllToast();
            const response = await apiService.post(`api/scenario/publish/${scenarioId}`, {});
            if (response.status === 200) {
                toastSuccess('Scenario Successfully published.');
                router.push('/scenario-queue');
            }
        } catch (error: any) {
            toastError(
                error.response.status === 403
                    ? error.response.data.message
                    : 'An error occurred while publishing the scenario.'
            );
        }
    };

    const deleteScenario = async (scenarioId: number) => {
        try {
            removeAllToast();
            const response = await apiService.delete(`api/scenario/delete/${scenarioId}`);
            if (response.status === 200) {
                toastSuccess('Scenario Successfully Deleted.');
                router.push('/scenario-queue');
            }
        } catch (error: any) {
            toastError(
                error.response.status === 403
                    ? error.response.data.message
                    : 'An error occurred while deleting the scenario.'
            );
        }
    };

    const getPublishedScenarios = async (
        page: number = 1,
        perPage: number = 10,
        orgId: number | null = null,
        filters: string[] | null = null,
        selectedScenarioId: number | null = null
    ) => {
        try {
            removeAllToast();
            const response = await apiService.get('api/scenario/published', {
                params: {
                    page,
                    per_page: perPage,
                    organization_id: orgId,
                    filters: filters,
                    scenario_id: selectedScenarioId
                }
            });
            if (response.status === 200) {
                return response.data;
            }
        } catch (error: any) {
            toastError(
                error.response.status === 403
                    ? error.response.data.message
                    : 'An error occurred while fetching the published scenarios.'
            );
        }
    };

    const killScenarioOptimization = async (scenarioId: number) => {
        try {
            removeAllToast();
            const response = await apiService.put(`api/scenario/kill/${scenarioId}`, {});
            if (response.status === 200) {
                toastSuccess('Scenario Optimization Successfully Killed.');
                router.push('/scenario-queue');
            }
        } catch (error: any) {
            toastError(
                error.response.status === 403
                    ? error.response.data.message
                    : 'An error occurred while killing the scenario optimization.'
            );
        }
    };

    const getProjectWells = async (lazyParams: LazyParams, projectId: number) => {
        try {
            const response = await apiService.get(`api/project/wells/${projectId}`, {
                params: lazyParams
            });

            return response.data;
        } catch (error) {
            console.error('Failed to fetch wells');
            throw error;
        }
    };

    const getInitialVisibleScenarioWells = async (scenarios: { [key: number]: string[] } | {} | undefined) => {
        try {
            if (!scenarios) return;
            const response = await apiService.get('api/scenario/initial-visible-wells', { params: scenarios });

            console.log('Data initial visible scenario wells before modifying:', response.data);

            for (const key of Object.keys(response.data)) {
                const innerObject = response.data[key];
                for (const innerObjectKey of Object.keys(innerObject)) {
                    for (let i = 0; i < innerObject[innerObjectKey].data.length; i++) {
                        if (innerObject[innerObjectKey].data[i].wellType === 'Oil') {
                            innerObject[innerObjectKey].data[i].wellType = 'LUOW';
                        }
                        if (innerObject[innerObjectKey].data[i].wellType === 'Gas') {
                            innerObject[innerObjectKey].data[i].wellType = 'DOW';
                        }
                    }
                }
            }

            console.log('Data initial visible scenario wells after modifying:', response.data);

            return response.data;
        } catch (error) {
            console.error('Failed to fetch initial visible scenario wells');
            throw error;
        }
    };

    const saveScenarioOverride = async (scenarioId: number, overrideData: OverrideData) => {
        try {
            const response = await apiService.post(`api/scenario/override/${scenarioId}`, overrideData);
            if (response.data) {
                toastSuccess('Scenario Override Successfully Saved.');
            }
            return response.data;
        } catch (error: any) {
            toastError(
                error.response.status === 422
                    ? error.response.data.message
                    : 'An error occurred while creating a scenario.'
            );
            throw error;
        }
    };

    const updateScenarioName = async (scenarioId: number, scenarioName: string) => {
        try {
            const response = await apiService.put(`api/scenario/${scenarioId}/rename`, { name: scenarioName });
            if (response.data) {
                toastSuccess('Scenario Override Successfully Saved.');
            }
            return response.data;
        } catch (error: any) {
            toastError(
                error.response.status === 422
                    ? error.response.data.message
                    : 'An error occurred while creating a scenario.'
            );
            throw error;
        }
    };

    const fetchScenarioParams = async (scenarioId: number) => {
        try {
            const response = await apiService.get(`api/scenario/${scenarioId}/params`);
            if (response.data) {
                toastSuccess('Scenario inputs loaded.');
            }
            return response.data;
        } catch (error: any) {
            toastError(
                error?.response?.status === 422
                    ? error?.response?.data?.message
                    : 'An error occurred while fetching scenario params.'
            );
            throw error;
            return;
        }
    };

    const fetchKpiSummary = async (scenarioId: number) => {
        try {
            const response = await apiService.get(`api/scenario/${scenarioId}/kpi-summary`);
            if (response.data) {
                toastSuccess('KPI summary loaded.');
            }
            return response.data;
        } catch (error: any) {
            toastError(
                error?.response?.status === 422
                    ? error?.response?.data?.message
                    : 'An error occurred while fetching the kpi data.'
            );
            console.error('Error fetching KPI summary:', error);
            throw error;
            return;
        }
    };

    return {
        publishScenario,
        deleteScenario,
        getPublishedScenarios,
        killScenarioOptimization,
        getProjectWells,
        saveScenarioOverride,
        getInitialVisibleScenarioWells,
        updateScenarioName,
        fetchScenarioParams,
        fetchKpiSummary
    };
}
