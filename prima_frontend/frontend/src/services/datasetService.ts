import { createApiService } from './apiService';
import { createToastService } from './toastService';

export function createDatasetService() {
    const apiService = createApiService();
    const toastService = createToastService();
    const { toastError, toastSuccess, toastWarn } = toastService;

    // Return available datasets for the admin
    const getDatasets = async (organizationId: number, mustContainRanking: boolean = false) => {
        const url = organizationId
            ? `/api/dataset?organization_id=${organizationId}&ranking=${mustContainRanking}`
            : '/api/dataset';

        try {
            const response = await apiService.get(url);
            const datasets = response.data;

            const wellData = datasets.filter((dataset: any) => dataset.additional === 0);
            const additionalData = datasets.filter((dataset: any) => dataset.additional === 1);

            return { wellData, additionalData };
        } catch (error) {
            toastError('Failed to fetch datasets');
            throw error;
        }
    };

    const uploadFile = async (file: any, organizationId: number, additional: boolean) => {
        //  TODO: Handle multiple files (?)
        const formData = new FormData();
        formData.append('file', file);
        formData.append('organization_id', `${organizationId}`);
        formData.append('name', file.name);
        formData.append('additional', additional.toString());

        try {
            const response = await apiService.post('/api/dataset/upload', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data'
                },
                timeout: 60000
            });
            if (response.status === 202) {
                toastWarn(response.data.message, 7000);
            } else {
                toastSuccess(response.data.message, 5000);
            }

            return response;
        } catch (error: any) {
            toastError('Failed to upload file');
            return error.response;
        }
    };

    const getDatasetLocationData = async (datasetId: number) => {
        try {
            const response = await apiService.get(`/api/dataset/${datasetId}`, { params: { mapOnly: true } });

            if (response.status === 200) {
                toastSuccess('Dataset loaded successfully', 5000);
            }

            return response.data;
        } catch (error) {
            toastError('Failed to fetch dataset data', 5000);
            throw error;
        }
    };

    const getImportTemplate = async () => {
        try {
            const response = await apiService.getBlob('/api/dataset/template');
            const blob = new Blob([response.data], { type: response.headers['content-type'] });
            const link = document.createElement('a');

            // Create a URL for the blob
            link.href = window.URL.createObjectURL(blob);

            // Set the download attribute to specify the filename
            link.download = 'well_data_import_template.xlsx'; // Change to the desired filename

            // Append the link to the document body
            document.body.appendChild(link);

            // Programmatically click the link to trigger the download
            link.click();

            // Clean up by removing the link and revoking the blob URL
            document.body.removeChild(link);
            window.URL.revokeObjectURL(link.href);

            return response.data;
        } catch (error) {
            toastError('Failed to fetch import template');
            throw error;
        }
    };

    return {
        getDatasets,
        uploadFile,
        getDatasetLocationData,
        getImportTemplate
    };
}
