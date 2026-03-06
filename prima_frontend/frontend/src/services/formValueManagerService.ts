// formValueManager.ts
import { AFFECTED_FIELDS } from '@/constants/fieldConfig';

export class FormValueManager {
    private originalValues: any = {};
    private isEditMode: boolean;

    constructor(isEditMode = false, originalData: any = null) {
        this.isEditMode = isEditMode;
        this.originalValues = originalData || {};
    }

    getValueForField(sectionPath: string[], fieldKey: string, isRankOnly: boolean): any {
        const fieldConfig = this.getNestedFieldConfig(sectionPath, fieldKey);

        if (!fieldConfig) return undefined;

        const expectedValue = isRankOnly ? fieldConfig.rankOnly : fieldConfig.other;

        // If not in edit mode, use expected value or default
        if (!this.isEditMode) {
            return expectedValue === 'preserve' ? fieldConfig.defaultValue : expectedValue;
        }

        // In edit mode
        const originalValue = this.getNestedOriginalValue(sectionPath, fieldKey);

        if (expectedValue === 'preserve' && originalValue !== undefined) {
            return originalValue;
        }

        if (expectedValue === 'preserve') {
            return fieldConfig.defaultValue;
        }

        return expectedValue;
    }

    private getNestedFieldConfig(sectionPath: string[], fieldKey: string): any {
        let config: any = AFFECTED_FIELDS;
        for (const path of sectionPath) {
            config = config[path];
            if (!config) return null;
        }
        return config[fieldKey];
    }

    private getNestedOriginalValue(sectionPath: string[], fieldKey: string): any {
        if (sectionPath[0] === 'generalSpecifications' && this.originalValues.generalSpecifications) {
            const value = this.originalValues.generalSpecifications[fieldKey];
            if (value !== undefined) {
                return value;
            }
        }

        // Fallback to nested traversal for other cases
        let value = this.originalValues;
        for (const path of sectionPath) {
            value = value?.[path];
            if (value === undefined) return undefined;
        }
        return value?.[fieldKey];
    }
}
