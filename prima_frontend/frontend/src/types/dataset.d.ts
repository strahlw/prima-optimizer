import type { User } from './user';
import type { WellType } from './well';
import type { Organization } from './organization';

export type UploadDatasetJsonKeys = {
    wellId: number;
    latitude: number;
    longitude: number;
    operatorName?: string | null;
    name?: string | null;
    wellName?: string | null;
    wellType: WellType;
    hydrocarbonLosses?: number | null;
    age?: number | null;
    depth?: number | null;
    annualOilProduction?: number | null;
    annualGasProduction?: number | null;
    fiveYearGasProduction?: number | null;
    fiveYearOilProduction?: number | null;
    lifelongGasProduction?: number | null;
    lifelongOilProduction?: number | null;
    leak: boolean;
    violation: boolean;
    incident: boolean;
    compliance: boolean;
    hydrocarbonLosses?: number | null;
    h2sLeak: boolean | null;
    stateWetlandsCloseRange?: boolean | null;
    stateWetlandsWideRange?: boolean | null;
    federalWetlandsCloseRange?: boolean | null;
    federalWetlandsWideRange?: boolean | null;
    fedWetlandsNear?: boolean | null;
    fedWetlandsFar?: boolean | null;
    stateWetlandsNear?: boolean | null;
    stateWetlandsFar?: boolean | null;
    buildingsCloseRange?: boolean | null;
    buildingsWideRange?: boolean | null;
    buildingsNear?: boolean | null;
    buildingsFar?: boolean | null;
    agricultureAreaNearby?: boolean | null;
    numOfSchoolsNearWell?: number | null;
    numOfHospitalsNearWell?: number | null;
    elevationDelta?: number | null;
    distanceToRoad?: number | null;
    waterSourceNearby?: boolean | null;
    knownSoilOrWaterImpact?: boolean | null;
    inTribalLand?: boolean | null;
    likelyToBeOrphaned?: boolean | null;
    costOfPlugging?: number | null;
    highPressureObserved?: boolean | null;
    idleStatusDuration?: boolean | null;
    numberOfMcwsNearby?: number | null;
    mechanicalIntegrityTest?: number | null;
    otherwiseIncentivizedWell?: boolean | null;
    historicalPreservationSite?: boolean | null;
    homeUseGasWell?: boolean | null;
    postPluggingLandUse?: boolean | null;
    surfaceEquipmentOnSite?: boolean | null;
    endangeredSpeciesOnSite?: boolean | null;
    brineLeak?: boolean | null;
    wellIntegrity?: boolean | null;
    placeholderOne?: boolean | null;
    placeholderTwo?: boolean | null;
    placeholderThree?: boolean | null;
    placeholderFour?: boolean | null;
    placeholderFive?: boolean | null;
    placeholderSix?: number | null;
    placeholderSeven?: number | null;
    placeholderEight?: number | null;
    placeholderNine?: number | null;
    placeholderTen?: number | null;
    placeholderEleven?: boolean | null;
    placeholderTwelve?: boolean | null;
    placeholderThirteen?: boolean | null;
    placeholderFourteen?: boolean | null;
    placeholderFifteen?: boolean | null;
    placeholderSixteen?: number | null;
    placeholderSeventeen?: number | null;
    placeholderEighteen?: number | null;
    placeholderNineteen?: number | null;
    placeholderTwenty?: number | null;
    populationDensity?: number | null;
    stateCode?: number | null;
    countyCode?: number | null;
    censusTractId?: number | null;
};

export type Dataset = {
    id: number;
    name: string;
    uploadedById: number;
    organizationId: number;
    filePath: string;
    user?: User;
    organization?: Organization;
    createdAt: string;
};

export type DatasetJsonLocation = {
    wellId: { value: number; label: string };
    latitude: { value: number; label: string };
    longitude: { value: number; label: string };
    wellName: { value: string | null; label: string };
    wellType: { value: WellType; label: string };
    operatorName: { value: string; label: string };
    depth: { value: number; label: string };
};

export type DatasetJson = {
    // Is there a way to accomplish this programmatically?
    [K in keyof UploadDatasetJsonKeys]: { value: UploadDatasetJsonKeys[K]; label: string };
};

export type DatasetChangeEvent = {
    value: number;
};
