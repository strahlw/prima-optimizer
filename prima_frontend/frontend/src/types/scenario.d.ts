import type { ScenarioFormTitle } from '../constants/scenarioEnums';
import type { Dataset } from './dataset';
import type { Organization } from './organization';
import type { ScenarioProject } from './projects';
import type { ImpactFactors } from './scenarioForm/impactFactor';
import type { EfficiencyFactors } from './scenarioForm/efficiencyFactor';
import type { GeneralSpecifications } from './scenarioForm/generalSpecification';
import type { User } from './user';

export type ScenarioStatus = 'optimizing' | 'published' | 'reviewable';

export type ApiScenarioType = {
    [key: string]: string;
    id: number;
    name:
        | ScenarioFormTitle.WellRanking
        | ScenarioFormTitle.PAProjectRecommendations
        | ScenarioFormTitle.PAProjectComaprisons;
};

export type ScenarioTableColumn = {
    field: string;
    header: string;
};
export interface ScenarioData {
    name: string;
    status: string;
    numWells: number;
    avgImpact: number;
    createdBy: string;
    efficiency: number;
    numProjects: number;
    wellFileName: string;
    generalSpecifications?: GeneralSpecifications;
    impactFactors?: ImpactFactors;
    efficiencyFactors?: EfficiencyFactors;
}

export interface Scenario {
    id: number;
    name: string;
    userId: number;
    organizationId: number;
    status: string;
    data: ScenarioData;
    deletedAt: string | null;
    createdAt: string;
    updatedAt: string;
    isRankOnly?: boolean;
    wellCount?: number;
    latitude?: number;
    longitude?: number;
    user?: User;
    types?: ScenarioType | ApiScenarioType[];
}

// TODO: Revise utilization of scenario params
export interface PublishedScenario extends Scenario {
    projects: ScenarioProject[];
    user: User;
    parent?: MinimalDetailsScenario;
    copyParent?: MinimalDetailsScenario;
}

// Used for the table view on the Scenarios Screen
export interface MinimalDetailsScenario {
    id: number;
    user: User;
    name: string;
    parent?: MinimalDetailsScenario;
    copyParent?: MinimalDetailsScenario;
    data: ScenarioData;
    wellTypes?: Array;
    dataset?: Dataset;
    organization?: Organization;
    isRankOnly?: boolean;
    types?: ScenarioType | ApiScenarioType[];
    isRecommendationOnly?: boolean;
}

export interface ParamsMinimalDetailsScenario extends MinimalDetailsScenario {
    dataset: Dataset;
    organization: Organization;
    data: ScenarioData;
}

export type OverrideData = {
    name: string;
    projectsRemove: number[];
    wellsRemove: { [projectId: number]: Well[] }; // projectID => [wellID] TODO: Trim down to jiust id, can autopopulate for all removed by projectsRemove
    projectsLock: number[]; // Phase 2
    wellsLock: { [projectId: number]: number[] }; // Phase 2: projectID => [wellID]
    wellsReassignFrom: Well[]; // wells that are being reassigned - discuss with Python API team, as these already have ProjectID in the object
    wellsReassignTo: { [projectId: number]: Well[] }; // projectID => [wellID] // wells that are being reassigned
    newWellAdditions: number[]; // Datasets that were not previously assigned, but are newly added.
};
