// Used to hold type / interface definitions for all forms.
import type { ImpactFactors } from './impactFactor';
import type { EfficiencyFactors } from './efficiencyFactor';
import type { GeneralSpecificationsInputs } from './generalSpecification';

type ScenarioFormKey =
    | 'useCases'
    | 'generalSpecifications'
    | 'impactFactors'
    | 'efficiencyFactors'
    | 'wellRanking'
    | 'paProjectComparisons'
    | 'paProjectReccomendations'
    | '$validationGroups';

export interface ScenarioForm {
    [key: ScenarioFormKey]: Object;
    id: number | null;
    useCases: {
        cases: array<string>;
    };
    generalSpecifications: GeneralSpecificationsInputs;
    impactFactors: ImpactFactors;
    efficiencyFactors: EfficiencyFactors;
    wellRanking: {
        rank: string;
    };
    paProjectComparisons: {
        comparison: string;
    };
    copyParentId?: number | null;
    $validationGroups: any;
}
