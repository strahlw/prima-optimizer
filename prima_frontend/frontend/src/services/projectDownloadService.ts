import { createApiService } from './apiService';
import { createToastService } from '@/services/toastService';
import type { ScenarioProject, ProjectIdColorMap } from '@/types/projects';
import { base64ToBlob } from '@/utils/base64ToBlob';

import { useMapStore } from '@/stores/mapStore';
import type { Scenario } from '../types/scenario';

export function createProjectDownloadService() {
    const mapStore = useMapStore();
    const apiService = createApiService();
    const toastService = createToastService();
    const { toastError, removeAllToast } = toastService;

    const getColorByLayerId = (mapId: string, layerId: string): string | undefined => {
        const map = mapStore.getMap(mapId);
        if (!map) return;

        const layer = map.getLayer(layerId);
        if (!layer) return;

        // Technically void | TransitionSpecification | PropertyValueSpecification<unknown>
        let color: any;

        switch (layer.type) {
            case 'symbol':
                color = map.getPaintProperty(layerId, 'icon-color');
                break;
            case 'fill':
                color = map.getPaintProperty(layerId, 'fill-color');
                break;
            case 'line':
                color = map.getPaintProperty(layerId, 'line-color');
                break;
            default:
                console.warn(`Layer type ${layer.type} is not supported for color retrieval.`);
        }

        return color;
    };

    const getColorData = (mapId: string, projects: Array<ScenarioProject>): { projects: Array<ProjectIdColorMap> } => {
        const map = mapStore.getMap(mapId);
        if (!map) return { projects: [] };

        const mappedProjectColors: Array<ProjectIdColorMap> = [];
        projects.forEach(function (project: ScenarioProject) {
            mappedProjectColors.push({
                id: project.id,
                color: getColorByLayerId(mapId, `projectLayer-${project.id}`) ?? ''
            });
        });

        return { projects: mappedProjectColors };
    };

    const downloadScenarioData = async (
        dataUrl: string,
        projectIdColorMap: Array<ProjectIdColorMap>,
        width: number,
        height: number,
        scenario: Scenario
    ) => {
        try {
            removeAllToast();

            const base64Image = dataUrl.split(',')[1];
            const imageBlob = base64ToBlob(base64Image, 'image/png');

            const formData = new FormData();
            formData.append('image', imageBlob, 'map-screenshot.png');
            formData.append('projectIdColorMap', JSON.stringify(projectIdColorMap));
            formData.append('width', width.toString());
            formData.append('height', height.toString());
            formData.append('scenarioId', scenario.id.toString());

            const response = await apiService.post('api/export/download-projects', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data'
                },
                responseType: 'blob'
            });

            if (response.status === 200) {
                const blob = new Blob([response.data]);

                if (blob.size === 0) {
                    console.error('❌ Empty Excel file returned from API.');
                    toastError('The downloaded file is empty. Please try again.');
                    return null;
                }

                const url = window.URL.createObjectURL(blob);

                // Create an anchor element and trigger a download
                const link = document.createElement('a');
                link.href = url;
                link.setAttribute('download', `${scenario.data.name ?? ''}_${new Date().toISOString()}.xlsx`); // Adjust filename if necessary
                document.body.appendChild(link);
                link.click();

                // Clean up
                document.body.removeChild(link);
                window.URL.revokeObjectURL(url);
                return blob;
            } else {
                console.error('❌ Failed to download scenario data:', response.statusText);
                toastError('Failed to download scenario data. Please try again.');
                return null;
            }
        } catch (error: any) {
            console.error('Error downloading scenario data:', error);
            toastError(
                error.response?.status === 403
                    ? error.response.data.message
                    : 'An error occurred while fetching the published scenarios.'
            );
            return null;
        }
    };

    return {
        getColorData,
        downloadScenarioData
    };
}
