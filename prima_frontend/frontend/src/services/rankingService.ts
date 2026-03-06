import { createApiService } from './apiService';
import type { LazyParams } from '../types/pagination';
import { useRankingStore } from '../stores/form/rankingStore';
import { createToastService } from '../services/toastService';

export function createRankingService() {
    const rankingStore = useRankingStore();
    const apiService = createApiService();
    const toastService = createToastService();
    const { toastSuccess, toastError } = toastService;

    const getRankingData = async (lazyParams: LazyParams, taskId?: string) => {
        try {
            const id = taskId ? taskId : rankingStore.getTaskId;
            if (id) {
                const response = await apiService.get(`/api/scenario/rank/${id}`, {
                    params: lazyParams
                });

                if (!Array.isArray(response.data.data)) {
                    response.data.data = Object.values(response.data.data);
                }

                console.log('Data before modifying:', response.data.data);

                for (let i = 0; i < response.data.data.length; i++) {
                    if (response.data.data[i].wellType === 'Oil') {
                        response.data.data[i].wellType = 'LUOW';
                    }
                    if (response.data.data[i].wellType === 'Gas') {
                        response.data.data[i].wellType = 'DOW';
                    }
                }

                return response.data;
            }
        } catch (error) {
            console.error('Failed to fetch wells');
            throw error;
        }
    };

    const resetRankingData = async () => {
        try {
            const taskId = rankingStore.getTaskId;
            if (taskId) {
                const response = await apiService.delete(`/api/scenario/rank/${taskId}`);
                if (response) {
                    rankingStore.deleteRankingData();
                }
            }
        } catch (error) {
            console.log('Error resetting ranking data');
        }
    };

    const submitScenarioWellRanking = async (scenarioId: number | null, ranking_page: boolean = true) => {
        try {
            const response = await apiService.post(`/api/scenario/${scenarioId}/rank`, { id: scenarioId });

            if (response && scenarioId) {
                rankingStore.setTaskIdMap({ id: scenarioId, taskId: response.data.taskId });
            }

            if (response && ranking_page) {
                toastSuccess('Scenario ranking in progress...', 3000);
            }
        } catch (error) {
            console.error(error);
            toastError('An issue occurred when fetching the ranking data');
        }
    };

    return {
        getRankingData,
        resetRankingData,
        submitScenarioWellRanking
    };
}
