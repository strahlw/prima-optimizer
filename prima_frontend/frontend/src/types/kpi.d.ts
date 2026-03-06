import type { EfficiencyFactors, ImpactFactors } from './scenarioForm';

export type KpiData = {
    numCandidateWells: number;
    numOilWells: number;
    numGasWells: number;
    numCombinedWells: number;
    numProjects: number | null;
    cost: number | null;
    budgetRemaining: number | null;
    impactFactors: ImpactFactors | null;
    efficiencyFactors: EfficiencyFactors | null;
    priorityImpactScoreMin: number | null;
    priorityImpactScoreMax: number | null;
    priorityImpactScoreAvg: number | null;
    efficiencyScoreMin: number | null;
    efficiencyScoreMax: number | null;
    efficiencyScoreAvg: number | null;
    overallImpactWeight: number | null;
    overallEfficiencyWeight: number | null;
};
