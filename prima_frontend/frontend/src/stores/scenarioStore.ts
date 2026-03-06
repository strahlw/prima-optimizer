import { defineStore } from 'pinia';
import { createApiService } from '../services/apiService';
import type { Scenario } from '@/types/scenario';
import type { PublishedScenario } from '@/types/scenario';

export const useScenarioStore = defineStore('scenarioStore', {
    state: () => ({
        scenarios: [] as Scenario[],
        publishedScenarios: [] as PublishedScenario[]
    }),
    persist: true,
    getters: {
        getScenarios: (state) => state.scenarios,
        getScenarioById: (state) => (id: number) => {
            return state.scenarios.find((scenario) => scenario.id === id);
        },
        getScenariosByOrganizationId: (state) => (organizationId: number) => {
            return state.scenarios.filter((scenario) => scenario.organizationId === organizationId);
        },
        getPublishedScenarios: (state) => state.publishedScenarios,
        getPublishedScenariosByOrganizationId: (state) => (organizationId: number) => {
            return state.publishedScenarios.filter((scenario) => scenario.organizationId === organizationId);
        }
    },
    actions: {
        async fetchScenarios() {
            // NOTE: Technically incorrect usage of inject() outside of a component
            const apiService = createApiService();
            try {
                const response = await apiService.get('/api/scenario');
                this.scenarios = response.data;
                return response.data;
            } catch (error) {
                console.error('Error fetching scenarios:', error);
                return [];
            }
        },
        setPublishedScenarios(scenarios: PublishedScenario[]) {
            this.publishedScenarios = scenarios;
        }
    }
});
