import { useScenarioFormStore } from '../stores/form/scenarioForm';
import { useRankingStore } from '../stores/form/rankingStore';
import { createApiService } from './apiService';
import { createToastService } from '../services/toastService';
import type { Dataset } from '@/types/dataset';
import { deepCopy } from '@/utils/deepCopy';

export function createFormService() {
    const apiService = createApiService();
    const toastService = createToastService();
    const { toastSuccess, toastError, stickyError } = toastService;

    const formatFormData = (): any => {
        const scenarioStore = useScenarioFormStore();

        const formData: any = deepCopy(scenarioStore.form);

        formData.generalSpecifications.basic.additionalDatasets =
            formData.generalSpecifications.basic.additionalDatasets.map((dataset: Dataset) => dataset.id);

        formData.generalSpecifications = {
            ...scenarioStore.form.generalSpecifications.basic,
            ...scenarioStore.form.generalSpecifications.plugging,
            ...scenarioStore.form.generalSpecifications.dataQuality,
            ...scenarioStore.form.generalSpecifications.solver
        };

        return formData;
    };

    const submitScenarioForm = async () => {
        try {
            const response = await apiService.post('/api/scenario', formatFormData());
            if (response) {
                const scenarioStore = useScenarioFormStore();
                toastSuccess('Scenario optimization in progress...', 3000);
                scenarioStore.form.id = response.data.id;
            }
        } catch (error) {
            console.error(error);
            toastError('An issue occured when submitting the optimization');
        }
    };

    const submitWellRanking = async () => {
        const rankingStore = useRankingStore();

        try {
            const response = await apiService.post('/api/scenario/rank', formatFormData());

            rankingStore.setTaskId(response.data.taskId);
            if (response) {
                toastSuccess('Scenario ranking in progress...', 3000);
            }
        } catch (error) {
            console.error(error);
            stickyError('An issue occured when submitting the ranking');
        }
    };

    const getAvailableFactors = async () => {
        try {
            const response = await apiService.post('/api/scenario/available-factors', formatFormData());
            return response.data;
        } catch (error) {
            console.error(error);
            stickyError('An issue occured when identifying the available factors');
        }
    };

    const submitRankOnlyScenarioForm = async () => {
        try {
            const response = await apiService.post('/api/scenario/rankOnly', formatFormData());
            if (response) {
                toastSuccess('Rank only scenario created', 3000);
                return response.data;
            }
        } catch (error) {
            console.error(error);
            toastError('An issue occured when submitting the Scenario for ranking');
        }
    };

    return {
        submitScenarioForm,
        submitWellRanking,
        submitRankOnlyScenarioForm,
        getAvailableFactors
    };
}
