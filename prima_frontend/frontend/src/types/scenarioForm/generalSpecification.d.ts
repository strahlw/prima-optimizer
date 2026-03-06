export interface GeneralSpecifications {
    [key: string]: any;
    organizationId: number | null;
    datasetId: number | null;
    additionalDatasets: Array;
    wellType: array;
    name: string;
    budget: number;
    maxWellsPerOwner?: number | null;
}

export interface GeneralSpecificationsInputs {
    [key: string]: any;
    basic: {
        // Basic Specifications
        organizationId: number | null;
        datasetId: number | null;
        additionalDatasets: Array;
        name: string;
        budget: number;
        minWellsInProject: number | null;
        maxWellsInProject: number | null;
        wellDepthLimit: number | null;
        maxDistanceBetweenProjectWells: number | null;
        maxWellsPerOwner: number | null;
        minLifetimeGasProduction: number | null;
        maxLifetimeGasProduction: number | null;
        minLifetimeOilProduction: number | null;
        maxLifetimeOilProduction: number | null;
        wellType: array;
        maxWellsPerOwner: number | null;
    };
    plugging: {
        // Plugging Costs
        shallowGasWellCost: number | null;
        deepGasWellCost: number | null;
        shallowOilWellCost: number | null;
        deepOilWellCost: number | null;
        costEfficiency: number | null;
    };
    dataQuality: {
        basicDataChecks: boolean;
        handleMissingWellAge: string;
        specifiedAge: number | null;
        handleMissingDepth: string;
        specifiedDepth: number | null;
        handleMissingProduction: string;
        specifiedAnnualOilProduction: number | null;
        specifiedLifetimeOilProduction: number | null;
        specifiedAnnualGasProduction: number | null;
        specifiedLifetimeGasProduction: number | null;
        handleMissingType: string;
        specifiedType: string | null;
    };
    solver: {
        solverTime: number;
        absoluteGap: number | null;
        relativeGap: number | null;
        model: string | null;
    };
}
