import { createApiService } from './apiService';
import { createToastService } from '@/services/toastService';

import type { LazyParams } from '../types/pagination';
import type { ColumnDefinition } from '../constants/rankingConstants';

export function createDownloadService() {
    const apiService = createApiService();
    const toastService = createToastService();
    const { toastError, toastSuccess, removeAllToast } = toastService;
    const DOWNLOAD_TIMEOUT = 30000; // 30 seconds timeout

    const downloadRankedWells = async (
        taskId: string,
        lazyParams: LazyParams,
        columns: ColumnDefinition[],
        scenarioName: string,
        scenarioId?: number
    ) => {
        removeAllToast();
        const controller = new AbortController();

        const timeoutId = setTimeout(() => {
            controller.abort();
        }, DOWNLOAD_TIMEOUT);

        try {
            const response = await apiService.post(
                scenarioId ? `api/export/scenario-ranking/${scenarioId}` : 'api/export/ranked-wells',
                {
                    taskId: taskId,
                    sortField: lazyParams.sortField,
                    sortOrder: lazyParams.sortOrder,
                    wellType: lazyParams.wellType,
                    columns: columns
                },
                {
                    responseType: 'blob',
                    signal: controller.signal
                }
            );

            if (response.status === 200) {
                // Check if the response is actually an error message
                const contentType = response.headers['content-type'];
                if (contentType && contentType.includes('application/json')) {
                    const reader = new FileReader();
                    reader.onload = () => {
                        const error = JSON.parse(reader.result as string);
                        throw new Error(error.message || 'Download failed');
                    };
                    reader.readAsText(response.data);
                    return;
                }

                const url = window.URL.createObjectURL(new Blob([response.data]));
                const link = document.createElement('a');
                link.href = url;
                link.setAttribute('download', `scenario_${scenarioName}-ranked-wells.xlsx`);
                document.body.appendChild(link);
                link.click();

                // Cleanup
                document.body.removeChild(link);
                window.URL.revokeObjectURL(url);

                toastSuccess('Download started successfully');
                return response.data;
            }
        } catch (error: any) {
            if (error.name === 'AbortError') {
                toastError('Download request timed out. Please try again.');
            } else {
                toastError(
                    error.response?.status === 403
                        ? error.response.data.message
                        : 'An error occurred while downloading the file.'
                );
            }
            throw error; // Re-throw to be caught by the component
        } finally {
            clearTimeout(timeoutId);
        }
    };

    const downloadRawWells = async (
        datasetId: number,
        lazyParams: LazyParams,
        columns: ({ key: string; value: string | number | boolean | null; header: string } | undefined)[],
        datasetName: string
    ) => {
        removeAllToast();
        const controller = new AbortController();
        const timeoutId = setTimeout(() => {
            controller.abort();
        }, DOWNLOAD_TIMEOUT);

        try {
            const response = await apiService.post(
                'api/export/raw-data',
                {
                    datasetId: datasetId,
                    sortField: lazyParams.sortField,
                    sortOrder: lazyParams.sortOrder,
                    wellType: lazyParams.wellType,
                    columns: columns,
                    taskId: lazyParams.taskId
                },
                {
                    responseType: 'blob',
                    signal: controller.signal
                }
            );

            if (response.status === 200) {
                // Check if the response is actually an error message
                const contentType = response.headers['content-type'];
                if (contentType && contentType.includes('application/json')) {
                    const reader = new FileReader();
                    reader.onload = () => {
                        const error = JSON.parse(reader.result as string);
                        throw new Error(error.message || 'Download failed');
                    };
                    reader.readAsText(response.data);
                    return;
                }

                const url = window.URL.createObjectURL(new Blob([response.data]));
                const link = document.createElement('a');
                link.href = url;
                link.setAttribute('download', `dataset_${datasetName}-raw-data.xlsx`);
                document.body.appendChild(link);
                link.click();

                // Cleanup
                document.body.removeChild(link);
                window.URL.revokeObjectURL(url);

                toastSuccess('Download started successfully');
                return response.data;
            }
        } catch (error: any) {
            if (error.name === 'AbortError') {
                toastError('Download request timed out. Please try again.');
            } else {
                toastError(
                    error.response?.status === 403
                        ? error.response.data.message
                        : 'An error occurred while downloading the file.'
                );
            }
            throw error; // Re-throw to be caught by the component
        } finally {
            clearTimeout(timeoutId);
        }
    };

    const downloadUserList = async () => {
        removeAllToast();
        const controller = new AbortController();
        const timeoutId = setTimeout(() => {
            controller.abort();
        }, DOWNLOAD_TIMEOUT);

        try {
            const response = await apiService.get('api/export/user-list');
            if (response.status === 200) {
                // Check if the response is actually an error message
                const contentType = response.headers['content-type'];
                if (contentType && contentType.includes('application/json')) {
                    const reader = new FileReader();
                    reader.onload = () => {
                        const error = JSON.parse(reader.result as string);
                        throw new Error(error.message || 'Download failed');
                    };
                    reader.readAsText(response.data);
                    return;
                }

                const url = window.URL.createObjectURL(new Blob([response.data]));
                const link = document.createElement('a');
                link.href = url;
                link.setAttribute(
                    'download',
                    `user-list-${import.meta.env.VITE_APP_ENV}-${new Date().toDateString()}.csv`
                );
                document.body.appendChild(link);
                link.click();

                // Cleanup
                document.body.removeChild(link);
                window.URL.revokeObjectURL(url);

                toastSuccess('Download started successfully');
                return response.data;
            }
        } catch (error: any) {
            if (error.name === 'AbortError') {
                toastError('Download request timed out. Please try again.');
            } else {
                toastError(
                    error.response?.status === 403
                        ? error.response.data.message
                        : 'An error occurred while downloading the file.'
                );
            }
            throw error; // Re-throw to be caught by the component
        } finally {
            clearTimeout(timeoutId);
        }
    };

    return {
        downloadRankedWells,
        downloadRawWells,
        downloadUserList
    };
}
