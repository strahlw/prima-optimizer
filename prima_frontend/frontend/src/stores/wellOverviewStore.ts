import { defineStore } from 'pinia';
import { createApiService } from '../services/apiService';
import type { DatasetJson, Dataset, DatasetJsonLocation } from '../types/dataset';

export const useWellOverviewStore = defineStore('wellOverviewStore', {
    state: () => ({
        orgName: '',
        orgCoordinates: { longitude: 0, latitude: 0 },
        jsonData: [] as Array<DatasetJson>,
        dataset: {} as Dataset | null,
        datasetLocations: [] as Array<DatasetJsonLocation>,
        availableDatasets: {} as { [key: string]: Dataset[] },
        availableAdditionalDatasets: {} as { [key: string]: Array<{ [key: string]: Array<DatasetJson> }> },
        wellDataSortField: 'wellId' as string | null,
        wellDataSortOrder: null as number | null
    }),
    persist: true,
    getters: {
        getOrgName: (state) => state.orgName,
        getOrgCoordinates: (state) => state.orgCoordinates,
        getJsonData: (state) => state.jsonData,
        getDataset: (state) => state.dataset,
        getDatasetLocations: (state) => state.datasetLocations,
        getAvailableDatasets: (state) => state.availableDatasets,
        getAvailableAdditionalDatasets: (state) => state.availableAdditionalDatasets,
        getWellDataSortField: (state) => state.wellDataSortField,
        getWellDataSortOrder: (state) => state.wellDataSortOrder
    },
    actions: {
        async fetchDatasets() {
            // NOTE: Technically incorrect usage of inject() outside of a component
            const apiService = createApiService();
            try {
                const response = await apiService.get('/api/dataset?all=true');
                const datasets = response.data;

                const availableDatasets = {} as { [key: string]: Dataset[] };
                const availableAdditionalDatasets = {} as {
                    [key: string]: Array<{ [key: string]: Array<DatasetJson> }>;
                };

                Object.keys(datasets).forEach((orgKey) => {
                    const orgDatasets = datasets[orgKey];

                    availableDatasets[orgKey] = orgDatasets.filter((dataset: any) => !dataset.additional);
                    availableAdditionalDatasets[orgKey] = orgDatasets.filter((dataset: any) => dataset.additional);
                });

                this.availableDatasets = availableDatasets;
                this.availableAdditionalDatasets = availableAdditionalDatasets;
            } catch (error) {
                console.error('Failed to fetch available datasets');
                throw error;
            }
        },
        setOrgName(orgName: string) {
            this.orgName = orgName;
        },
        setOrgCoordinates(orgCoordinates: { longitude: number; latitude: number }) {
            this.orgCoordinates = { ...orgCoordinates };
        },
        setDataset(dataset: Dataset) {
            this.dataset = dataset;
        },
        resetSelectedDataset() {
            this.dataset = null;
            this.datasetLocations = [];
            this.jsonData = [];
        },
        setJsonData(jsonData: Array<DatasetJson>) {
            this.jsonData = jsonData;
        },
        setDatasetLocations(datasetLocations: Array<DatasetJsonLocation>) {
            this.datasetLocations = datasetLocations;
        },
        setWellDataSortField(sortField: string | null) {
            this.wellDataSortField = sortField;
        },
        setWellDataSortOrder(sortOrder: number | null) {
            this.wellDataSortOrder = sortOrder;
        }
    }
});
