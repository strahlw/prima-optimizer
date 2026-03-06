import { defineStore } from 'pinia';
import type { RankingDataJson } from '../../types/ranking';
import type { ScenarioForm } from '../../types/scenarioForm/scenarioForm';

export const useRankingStore = defineStore('rankingStore', {
    state: () => ({
        taskId: '',
        taskIdMap: {} as Record<number, string>,
        rankingData: [] as Array<RankingDataJson>,
        scenarioIdMappedRankingData: {} as Record<number, Array<RankingDataJson>>,
        createScenarioData: {} as ScenarioForm
    }),
    getters: {
        getRankingData: (state) => {
            return state.rankingData;
        },
        getTaskId(): string {
            return this.taskId;
        },
        getTaskIdMap(): Record<number, string> {
            return this.taskIdMap;
        },
        getScenarioIdMappedRankingData(): Record<number, Array<RankingDataJson>> {
            return this.scenarioIdMappedRankingData;
        },
        getScenarioData(): ScenarioForm {
            return this.createScenarioData;
        }
    },
    actions: {
        setRankingData(jsonData: Array<RankingDataJson>) {
            this.rankingData = jsonData;
        },
        setTaskId(newTaskId: string) {
            this.taskId = newTaskId;
        },
        setTaskIdMap(newTaskIdMap: { id: number; taskId: string }) {
            this.taskIdMap[newTaskIdMap.id] = newTaskIdMap.taskId;
        },
        setScenarioIdMappedRankingData(data: Record<number, Array<RankingDataJson>>) {
            this.scenarioIdMappedRankingData = data;
        },
        setScenarioData(data: ScenarioForm) {
            this.createScenarioData = data;
        },
        deleteRankingData() {
            this.taskId = '';
            this.rankingData = [];
            this.createScenarioData = {} as ScenarioForm;
        },
        clearTaskIdMap() {
            this.taskIdMap = {};
        }
    }
});
