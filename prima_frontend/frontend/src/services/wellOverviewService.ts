import { useWellOverviewStore } from '../stores/wellOverviewStore';
import { createApiService } from './apiService';

import type { LazyParams } from '../types/pagination';

export function createWellOverviewService() {
    const wellOverviewStore = useWellOverviewStore();
    const apiService = createApiService();

    const prioritizedFields = [
        'wellId',
        'name',
        'wellType',
        'age',
        'depth',
        'oil',
        'gas',
        'fiveYearGasProduction',
        'fiveYearOilProduction',
        'latitude',
        'longitude',
        'operatorName',
        'censusTractId'
    ];

    const getWells = async (lazyParams: LazyParams) => {
        try {
            const dataset = wellOverviewStore.getDataset;
            if (dataset) {
                const response = await apiService.get(`/api/dataset/${dataset.id}`, {
                    params: lazyParams
                });

                if (!Array.isArray(response.data.data)) {
                    response.data.data = Object.values(response.data.data);
                }

                console.log('Data before modifying:', response.data.data);

                for (let i = 0; i < response.data.data.length; i++) {
                    if (response.data.data[i].wellType.value === 'Oil') {
                        response.data.data[i].wellType.value = 'LUOW';
                    }
                    if (response.data.data[i].wellType.value === 'Gas') {
                        response.data.data[i].wellType.value = 'DOW';
                    }

                    response.data.data[i].wellType.label = 'Well Type [LUOW, DOW]';
                }

                console.log('Data after modifying:', response.data.data);

                return response.data;
            }
        } catch (error) {
            console.error('Failed to fetch wells');
            throw error;
        }
    };

    function getComputedColumns(): (
        | { key: string; value: string | number | boolean | null; header: string }
        | undefined
    )[] {
        const jsonData = wellOverviewStore.getJsonData[0];
        if (!jsonData) return [];

        // Map the JSON data to column objects
        const allColumns = Object.entries(jsonData).map(([key, { value, label }]) => ({
            key,
            value: value ?? null,
            header: label
        }));

        // Separate prioritized columns from the rest
        const prioritizedColumns = prioritizedFields
            .map((field) => allColumns.find((column) => column.key === field))
            .filter(Boolean); // Removes undefined if any prioritized field is missing

        // Filter out prioritized fields from the rest
        const defaultColumns = allColumns.filter((column) => !prioritizedFields.includes(column.key));

        // Combine prioritized columns with the default columns
        return [...prioritizedColumns, ...defaultColumns];
    }

    return {
        getWells,
        getComputedColumns
    };
}
