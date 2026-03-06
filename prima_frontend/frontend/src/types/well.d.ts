import type { ScenarioProject } from './projects';
import type { UploadDatasetJsonKeys } from './dataset';

export type WellType = 'Oil' | 'Gas' | 'Both';

export type WellBase = {
    [K in keyof UploadDatasetJsonKeys]: UploadDatasetJsonKeys[K];
};

export type Well = WellBase & {
    id?: string | null; // MongoDB Object ID
    wellId: number;
    wellRank?: number | null; // No uses seems strange
    datasetJsonId: string;
    priorityScore: number;
    taskId: string;
    projects?: ScenarioProject[];
    scenarioId?: number | null;
    projectId?: string | null | number; // Only for overrides
};

export type SingleWell = {
    scenarioId?: number;
    wellId: { value: number; label: string };
    wellName: { value: string; label: string };
    operatorName: { value: string; label: string };
    depth: { value: number; label: string };
    latitude: { value: number; label: string };
    longitude: { value: number; label: string };
};
