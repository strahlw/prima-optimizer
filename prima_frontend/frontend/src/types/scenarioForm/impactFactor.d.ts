import type { Factor } from '../factor';
import type { ScenarioForm } from './scenarioForm';

export interface ImpactFactorsLabel {
    name: string;
    field: keyof ScenarioForm['impactFactors'];
    childFields?: null;
    toolTip?: string;
}

export interface LossesFactor extends Factor {
    childFactors: {
        [key: string]: Factor;
        leak: Factor;
        violation: Factor;
        compliance: Factor;
        incident: Factor;
        hydrocarbonLosses: Factor;
    };
}

export interface ImpactFactorsLossesLabel {
    name: string;
    field: 'losses';
    childFields: ImpactFactorsLossesChildLabel[];
}

export interface ImpactFactorsLossesChildLabel {
    name: string;
    field: keyof ScenarioForm['impactFactors']['losses']['childFactors'];
}

export interface AnnProductionVolumeFactor extends Factor {
    childFactors: {
        [key: string]: Factor;
        annGasProduction: Factor;
        annOilProduction: Factor;
    };
}

export interface ImpactFactorsAnnProductionVolumeLabel {
    name: string;
    field: 'annProductionVolume';
    childFields: ImpactFactorsAnnProductionVolumeChildLabel[];
}

export interface ImpactFactorsAnnProductionVolumeChildLabel {
    name: string;
    field: keyof ScenarioForm['impactFactors']['annProductionVolume']['childFactors'];
}

export interface FiveYearProductionVolumeFactor extends Factor {
    childFactors: {
        [key: string]: Factor;
        fiveYearGasProduction: Factor;
        fiveYearOilProduction: Factor;
    };
}

export interface ImpactFactorsFiveYearProductionVolumeLabel {
    name: string;
    field: 'fiveYearProductionVolume';
    childFields: ImpactFactorsFiveYearProductionVolumeChildLabel[];
}

export interface ImpactFactorsFiveYearProductionVolumeChildLabel {
    name: string;
    field: keyof ScenarioForm['impactFactors']['fiveYearProductionVolume']['childFactors'];
}

export interface LifelongProductionVolumeFactor extends Factor {
    childFactors: {
        [key: string]: Factor;
        lifelongGasProduction: Factor;
        lifelongOilProduction: Factor;
    };
}

export interface ImpactFactorsLifelongProductionVolumeLabel {
    name: string;
    field: 'lifelongProductionVolume';
    childFields: ImpactFactorsLifelongProductionVolumeChildLabel[];
}

export interface ImpactFactorsLifelongProductionVolumeChildLabel {
    name: string;
    field: keyof ScenarioForm['impactFactors']['lifelongProductionVolume']['childFactors'];
}

export interface SiteConsiderationsFactor extends Factor {
    childFactors: {
        [key: string]: Factor;
        historicalPreservationSite: Factor;
        homeUseGasWell: Factor;
        postPluggingLandUse: Factor;
        surfaceEquipmentOnSite: Factor;
    };
}

export interface ImpactFactorsSiteConsiderationsLabel {
    name: string;
    field: 'siteConsiderations';
    childFields: ImpactFactorsSiteConsiderationsChildLabel[];
}

export interface ImpactFactorsSiteConsiderationsChildLabel {
    name: string;
    field: keyof ScenarioForm['impactFactors']['siteConsiderations']['childFactors'];
}

export interface SensitiveReceptorsFactor extends Factor {
    childFactors: {
        [key: string]: Factor;
        schools: Factor;
        hospitals: Factor;
        agricultureAreaNearby: Factor;
        buildingsNear: Factor;
        buildingsFar: Factor;
    };
}

export interface ImpactFactorsSensitiveReceptorsLabel {
    name: string;
    field: 'sensitiveReceptors';
    childFields: ImpactFactorsSensitiveReceptorsChildLabel[];
}

export interface ImpactFactorsSensitiveReceptorsChildLabel {
    name: string;
    field: keyof ScenarioForm['impactFactors']['sensitiveReceptors']['childFactors'];
}

export interface EnvironmentFactor extends Factor {
    childFactors: {
        [key: string]: Factor;
        waterSourceNearby: Factor;
        knownSoilOrWaterImpact: Factor;
        fedWetlandsNear: Factor;
        fedWetlandsFar: Factor;
        stateWetlandsNear: Factor;
        stateWetlandsFar: Factor;
    };
}

export interface ImpactFactorsEnvironmentLabel {
    name: string;
    field: 'environment';
    childFields: ImpactFactorsEnvironmentChildLabel[];
}

export interface ImpactFactorsEnvironmentChildLabel {
    name: string;
    field: keyof ScenarioForm['impactFactors']['environment']['childFactors'];
}

export interface ImpactFactorInputProps {
    label:
        | ImpactFactorsLabel
        | ImpactFactorsLossesChildLabel
        | ImpactFactorsSensitiveReceptorsChildLabel
        | ImpactFactorsAnnProductionVolumeChildLabel
        | ImpactFactorsLifelongProductionVolumeChildLabel
        | ImpactFactorsEcologicalReceptorsChildLabel
        | ImpactFactorsFiveYearProductionVolumeChildLabel
        | ImpactFactorsEnvironmentChildLabel
        | ImpactFactorsOtherLossesChildLabel
        | ImpactFactorsSiteConsiderationsChildLabel;
    parentFactor?:
        | Factor
        | LossesFactor
        | SensitiveReceptorsFactor
        | AnnProductionVolumeFactor
        | EcologicalReceptorsFactor
        | FiveYearProductionVolumeFactor
        | LifelongProductionVolumeFactor
        | EnvironmentFactor
        | OtherLossesFactor
        | SiteConsiderationsFactor;
    disabled?: boolean;
    parentDisabled?: boolean;
    remainingTotal: number;
}

export interface EcologicalReceptorsFactor extends Factor {
    childFactors: {
        [key: string]: Factor;
        endangeredSpeciesOnSite: Factor;
    };
}

export interface ImpactFactorsEcologicalReceptorsLabel {
    name: string;
    field: 'ecologicalReceptors';
    childFields: ImpactFactorsEcologicalReceptorsChildLabel[];
}

export interface ImpactFactorsEcologicalReceptorsChildLabel {
    name: string;
    field: keyof ScenarioForm['impactFactors']['ecologicalReceptors']['childFactors'];
}

export interface OtherLossesFactor extends Factor {
    childFactors: {
        [key: string]: Factor;
        brineLeak: Factor;
        h2sLeak: Factor;
    };
}

export interface ImpactFactorsOtherLossesLabel {
    name: string;
    field: 'otherLosses';
    childFields: ImpactFactorsOtherLossesChildLabel[];
}

export interface ImpactFactorsOtherLossesChildLabel {
    name: string;
    field: keyof ScenarioForm['impactFactors']['otherLosses']['childFactors'];
}

export interface ImpactFactors {
    [key: string]:
        | Factor
        | LossesFactor
        | SensitiveReceptorsFactor
        | EnvironmentFactor
        | AnnProductionVolumeFactor
        | FiveYearProductionVolumeFactor
        | LifelongProductionVolumeFactor
        | SiteConsiderationsFactor
        | EcologicalReceptorsFactor
        | OtherLossesFactor;
    losses: LossesFactor;
    annProductionVolume: AnnProductionVolumeFactor;
    fiveYearProductionVolume: FiveYearProductionVolumeFactor;
    lifelongProductionVolume: LifelongProductionVolumeFactor;
    siteConsiderations: SiteConsiderationsFactor;
    ecologicalReceptors: EcologicalReceptorsFactor;
    otherLosses: OtherLossesFactor;
    wellAge: Factor;
    ownerWellCount: Factor;
    sensitiveReceptors: SensitiveReceptorsFactor;
    inTribalLand: Factor;
    likelyToBeOrphaned: Factor;
    costOfPlugging: Factor;
    highPressureObserved: Factor;
    idleStatusDuration: Factor;
    numberOfMcwsNearby: Factor;
    mechanicalIntegrityTest: Factor;
    otherwiseIncentivizedWell: Factor;
    wellIntegrity: Factor;
    placeholderOne: Factor;
    placeholderTwo: Factor;
    placeholderThree: Factor;
    placeholderFour: Factor;
    placeholderFive: Factor;
    placeholderSix: Factor;
    placeholderSeven: Factor;
    placeholderEight: Factor;
    placeholderNine: Factor;
    placeholderTen: Factor;
    placeholderEleven: Factor;
    placeholderTwelve: Factor;
    placeholderThirteen: Factor;
    placeholderFourteen: Factor;
    placeholderFifteen: Factor;
    placeholderSixteen: Factor;
    placeholderSeventeen: Factor;
    placeholderEighteen: Factor;
    placeholderNineteen: Factor;
    placeholderTwenty: Factor;
    environment: EnvironmentFactor;
}
