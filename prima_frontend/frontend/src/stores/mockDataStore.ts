import { defineStore } from 'pinia';
import type { Scenario } from '../types/scenario.d.ts';
import type { Project } from '../types/projects.d.ts';

// TODO: Phase 2 - remove need for this file, this will come when the 'Review' page is revisited

export interface userScenario {
    id: number;
    'Scenario Name': string;
    Owner: string;
    'Created At': string;
    Projects: Project[];
}

// TODO: Reflect actual data structure
export interface ReviewProject {
    project: string;
    numWellsScore: number;
    proximityScore: number;
    depthRangeScore: number;
    distanceToRoadScore: number;
    elevationDeltaScore: number;
    efficiencyScore: number;
}

const mockReviewProject: ReviewProject[] = [
    {
        project: 'Shallow Oil 173',
        numWellsScore: 8.71,
        proximityScore: 17.42,
        depthRangeScore: 18.34,
        distanceToRoadScore: 8.44,
        elevationDeltaScore: 9.42,
        efficiencyScore: 69.17
    },
    {
        project: 'Shallow Gas 89',
        numWellsScore: 8.71,
        proximityScore: 16.84,
        depthRangeScore: 10.86,
        distanceToRoadScore: 9.84,
        elevationDeltaScore: 7.12,
        efficiencyScore: 70.12
    },
    {
        project: 'Shallow Gas 76',
        numWellsScore: 8.71,
        proximityScore: 26.41,
        depthRangeScore: 12.87,
        distanceToRoadScore: 7.86,
        elevationDeltaScore: 6.84,
        efficiencyScore: 63.09
    },
    {
        project: 'Shallow Oil 76',
        numWellsScore: 8.71,
        proximityScore: 26.41,
        depthRangeScore: 12.87,
        distanceToRoadScore: 7.86,
        elevationDeltaScore: 6.84,
        efficiencyScore: 63.09
    },
    {
        project: 'Shallow Gas 76',
        numWellsScore: 8.71,
        proximityScore: 26.41,
        depthRangeScore: 12.87,
        distanceToRoadScore: 7.86,
        elevationDeltaScore: 6.84,
        efficiencyScore: 63.09
    }
];

export interface User {
    id: number;
    firstName: string;
    lastName: string;
    email: string;
}

const mockUsers: User[] = [
    {
        id: 1,
        firstName: 'David',
        lastName: 'Chen',
        email: 'david.chen@gmail.com'
    },
    {
        id: 2,
        firstName: 'Alison',
        lastName: 'Brown',
        email: 'alison.brown@gmail.com'
    },
    {
        id: 3,
        firstName: 'John',
        lastName: 'Doe',
        email: 'john.doe@gmail.com'
    },
    {
        id: 4,
        firstName: 'Jane',
        lastName: 'Smith',
        email: 'jane.smith@gmail.com'
    },
    {
        id: 5,
        firstName: 'Michael',
        lastName: 'Johnson',
        email: 'michael.johnson@gmail.com'
    },
    {
        id: 6,
        firstName: 'Sarah',
        lastName: 'Williams',
        email: 'sarah.williams@gmail.com'
    },
    {
        id: 7,
        firstName: 'Robert',
        lastName: 'Jones',
        email: 'robert.jones@gmail.com'
    }
];

export interface Organization {
    // TODO: Add ID when utilizing backend
    label: string;
    value: string;
}

const mockOrganizations: Organization[] = [
    { label: 'New York', value: 'NY' },
    { label: 'Massachusetts', value: 'MA' },
    { label: 'New Jersey', value: 'NJ' }
];

export const useMockDataStore = defineStore('data', {
    state: () => ({
        projects: [] as Project[],
        scenarios: [] as Scenario[],
        userScenarios: [] as userScenario[]
    }),
    getters: {
        getProjects: (state) => state.projects,

        getReviewProjects: () => mockReviewProject,
        getScenarios: (state) => state.scenarios,
        getUsers: () => mockUsers,
        getOrganizations: () => mockOrganizations,
        getUserScenarios: (state) => state.userScenarios
    },
    actions: {
        setProjects(projects: Project[]) {
            this.projects = projects;
        },
        setScenarios(scenarios: userScenario[]) {
            this.userScenarios = scenarios;
        },
        getRandomNumber(min: number, max: number, decimals: number) {
            const factor = Math.pow(10, decimals);
            const randomNumber = Math.random() * (max - min) + min;
            return Math.round(randomNumber * factor) / factor;
        },
        randomCoordinate(min: number, max: number): number {
            return Math.random() * (max - min) + min;
        }
    }
});
