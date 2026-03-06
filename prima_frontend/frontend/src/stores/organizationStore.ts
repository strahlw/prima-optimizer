import { defineStore } from 'pinia';
import type { Organization } from '../types/organization';
import { createApiService } from '../services/apiService';
import type { Dataset } from '@/types/dataset';

export const useOrganizationStore = defineStore('organization', {
    state: () => ({
        organizations: Array<Organization>(),
        users: Array<any>(),
        organizationsFetched: false,
        organizationDatasets: Array<Dataset>(),
        organizationAdditionalDatasets: Array<Dataset>()
    }),
    persist: true,
    getters: {
        getOrganizations: (state) => state.organizations,
        getOrganizationDatasets: (state) => state.organizationDatasets,
        getOrganizationAdditionalDatasets: (state) => state.organizationAdditionalDatasets,
        getOrganizationCoordinates: (state) => (organizationId: number) => {
            const organization = state.organizations.find((org) => org.id === organizationId);
            return organization ? [organization.latitude, organization.longitude] : null;
        },
        getDatasetById: (state) => (datasetId: number) => {
            let dataset = state.organizationDatasets.find((ds) => ds.id === datasetId);
            if (dataset) {
                return dataset;
            }
            dataset = state.organizationAdditionalDatasets.find((ds) => ds.id === datasetId);
            return dataset || null;
        }
    },
    actions: {
        setOrganizations(organizations: Array<Organization>) {
            this.organizations = [...organizations];
        },
        async fetchOrganizations(override = false) {
            if (this.organizationsFetched && !override) return;
            try {
                // NOTE: Technically incorrect usage of inject() outside of a component
                const apiService = createApiService();
                const response = await apiService.get('/api/organizations');
                if (response.data && response.data.organizations) {
                    this.organizations = response.data.organizations;
                    this.organizationsFetched = true;
                }
            } catch (error) {
                console.error('Error fetching organizations:', error);
            }
        },
        setOrganizationDatasets(datasets: Array<Dataset>) {
            this.organizationDatasets = datasets;
        },
        setOrganizationAdditionalDatasets(datasets: Array<Dataset>) {
            this.organizationAdditionalDatasets = datasets;
        }
    }
});
