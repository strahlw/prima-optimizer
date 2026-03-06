interface FieldConfig {
    defaultValue: number | string | boolean | null;
    rankOnly: number | string | boolean | null;
    other: number | string | boolean | null | 'preserve';
}

interface StrictAffectedFieldsConfig {
    generalSpecifications: {
        basic: {
            budget: FieldConfig;
            maxWellsPerOwner: FieldConfig;
            minWellsInProject: FieldConfig;
            maxWellsInProject: FieldConfig;
            wellDepthLimit: FieldConfig;
            maxDistanceBetweenProjectWells: FieldConfig;
        };
        plugging: {
            shallowGasWellCost: FieldConfig;
            deepGasWellCost: FieldConfig;
            shallowOilWellCost: FieldConfig;
            deepOilWellCost: FieldConfig;
        };
        solver: {
            solverTime: FieldConfig;
        };
    };
}

export const AFFECTED_FIELDS: StrictAffectedFieldsConfig = {
    generalSpecifications: {
        basic: {
            budget: {
                defaultValue: 0,
                rankOnly: 0,
                other: 'preserve'
            },
            maxWellsPerOwner: {
                defaultValue: null,
                rankOnly: null,
                other: 'preserve'
            },
            minWellsInProject: {
                defaultValue: 2,
                rankOnly: null,
                other: 'preserve'
            },
            maxWellsInProject: {
                defaultValue: 30,
                rankOnly: null,
                other: 'preserve'
            },
            wellDepthLimit: {
                defaultValue: 4000,
                rankOnly: null,
                other: 'preserve'
            },
            maxDistanceBetweenProjectWells: {
                defaultValue: 10,
                rankOnly: null,
                other: 'preserve'
            }
        },
        plugging: {
            shallowGasWellCost: {
                defaultValue: null,
                rankOnly: null,
                other: 'preserve'
            },
            deepGasWellCost: {
                defaultValue: null,
                rankOnly: null,
                other: 'preserve'
            },
            shallowOilWellCost: {
                defaultValue: null,
                rankOnly: null,
                other: 'preserve'
            },
            deepOilWellCost: {
                defaultValue: null,
                rankOnly: null,
                other: 'preserve'
            }
        },
        solver: {
            solverTime: {
                defaultValue: 3600,
                rankOnly: 3600,
                other: 'preserve'
            }
        }
    }
} as const;

export type { FieldConfig, StrictAffectedFieldsConfig };
