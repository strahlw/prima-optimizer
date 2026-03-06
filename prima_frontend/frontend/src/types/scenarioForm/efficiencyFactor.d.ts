import type { Factor } from '../factor';
import type { ScenarioForm } from './scenarioForm';

export interface EfficiencyFactors {
    [key: string]: Factor;
    numWells: Factor;
    numUniqueOwners: Factor;
    distanceToCentroid: Factor;
    avgDistanceToNearestRoad: Factor;
    avgElevationChangeFromNearestRoad: Factor;
    ageRange: Factor;
    avgAge: Factor;
    depthRange: Factor;
    avgDepth: Factor;
    distanceRange: Factor;
    populationDensity: Factor;
}

export interface EfficiencyFormLabel {
    name: string;
    field: keyof ScenarioForm['efficiencyFactors'];
}

export interface EfficiencyFactorInputProps {
    label: EfficiencyFormLabel;
    disabled?: boolean;
    remainingTotal: number;
}
