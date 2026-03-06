export interface ProjectData {
    id: number;
    scenarioId: number;
    projectId: number;
    json;
}

export interface Project {
    id: number;
    wells: any[]; // TODO: Properly type
}
export interface ScenarioProject extends Project {
    createdAt: string;
    updatedAt: string;
    scenarioId: number;
    projectId: number;
    impactScore: number;
    efficiencyScore: number;
    wellCount?: number;
    parentProjectDifferentials?: {
        impactScore?: number;
        efficiencyScore?: number;
    };
}

export type ProjectIdColorMap = {
    id: number;
    color: string;
};

// Used for the table view on the Scenarios Screen
export interface MinimalDetailsProject {
    id: number;
    projectId: number;
    scenarioId: number;
    impactScore?: number;
    efficiencyScore?: number;
    parentProjectDifferentials?: {
        impactScore?: number;
        efficiencyScore?: number;
    };
}
