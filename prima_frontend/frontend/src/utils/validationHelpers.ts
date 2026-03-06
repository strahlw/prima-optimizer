import type { Validation } from '@vuelidate/core';
import { computed } from 'vue';
import { helpers } from '@vuelidate/validators';
import { createApiService } from '@/services/apiService';

function debounce(fn: any, delay: number) {
    let timeout: ReturnType<typeof setTimeout>;
    return function (...args: any[]) {
        clearTimeout(timeout);
        timeout = setTimeout(() => fn(...args), delay);
    };
}

export function createValidation(vuelidateInstance: any, path: string) {
    return computed<Validation | undefined>(() => {
        const value = path.split('.').reduce((acc, part) => acc?.[part], vuelidateInstance.value);
        return value as Validation | undefined;
    });
}

// Define the function signature for the callback to get the other field value
type GetOtherFieldValue = () => number | null;

// Define the type for the value being validated
type ValidatorValue = number | null;

export function lessThanOrNull(getOtherFieldValue: GetOtherFieldValue, otherFieldName: string = '') {
    return helpers.withMessage(
        ({ $params }) =>
            otherFieldName
                ? `Value must be less than ${otherFieldName} or null.`
                : `Value must be less than ${$params.otherValue} or null.`,
        helpers.withParams({ type: 'lessThanOrNull', otherValue: getOtherFieldValue() }, (value: ValidatorValue) => {
            const otherFieldValue = getOtherFieldValue();
            if (otherFieldValue === null) return true;
            return value === null || (otherFieldValue !== null && value < otherFieldValue);
        })
    );
}

export function greaterThanOrNull(getOtherFieldValue: GetOtherFieldValue, otherFieldName: string = '') {
    return helpers.withMessage(
        ({ $params }) =>
            otherFieldName
                ? `Value must be greater than ${otherFieldName} or null.`
                : `Value must be greater than ${$params.otherValue} or null.`,
        helpers.withParams({ type: 'greaterThanOrNull', otherValue: getOtherFieldValue() }, (value: ValidatorValue) => {
            const otherFieldValue = getOtherFieldValue();
            if (otherFieldValue === null) return true;
            return value === null || (otherFieldValue !== null && value > otherFieldValue);
        })
    );
}

export function customMinValue(min: number) {
    return helpers.withParams(
        { customMinValue: min },
        helpers.withMessage(
            () => `Value must be ${min} or greater.`,
            (value: number | null) => value === null || value >= min
        )
    );
}

export function customMaxValue(max: number) {
    return helpers.withParams(
        { customMaxValue: max },
        helpers.withMessage(
            () => `Value must be ${max} or less.`,
            (value: number | null) => value === null || value <= max
        )
    );
}

export function createDebouncedApiCheck() {
    let currentPromise: Promise<boolean> | null = null;
    let currentResolve: ((value: boolean) => void) | null = null;
    let currentValue: string = '';
    let currentOrgId: number = 0;

    const debounced = debounce(async (value: string, orgId: number) => {
        // Only proceed if this matches the current pending validation
        if (value !== currentValue || orgId !== currentOrgId) {
            return;
        }

        const apiService = createApiService();
        try {
            const response = await apiService.get(`api/scenario/check-name`, {
                params: { name: value, organizationId: orgId }
            });

            // Double-check we're still validating the same value
            if (value === currentValue && orgId === currentOrgId && currentResolve) {
                currentResolve(response.data.unique === true);
                currentPromise = null;
                currentResolve = null;
            }
        } catch (error) {
            console.error('Failed to check scenario name uniqueness');
            if (value === currentValue && orgId === currentOrgId && currentResolve) {
                currentResolve(false);
                currentPromise = null;
                currentResolve = null;
            }
        }
    }, 500);

    return (value: string, orgId: number): Promise<boolean> => {
        // If validating the same value, return existing promise
        if (currentPromise && currentValue === value && currentOrgId === orgId) {
            return currentPromise;
        }

        // Cancel previous validation by not resolving it
        currentValue = value;
        currentOrgId = orgId;

        currentPromise = new Promise((resolve) => {
            currentResolve = resolve;
        });

        debounced(value, orgId);
        return currentPromise;
    };
}

const debouncedApiCheck = createDebouncedApiCheck();

export const uniqueNameWithinOrg = (getOrgId: () => number | null) =>
    helpers.withAsync(
        helpers.withMessage('Name must be unique within the organization', (value: string | null) => {
            if (!value) return Promise.resolve(true); // Let required handle empty
            const orgId = getOrgId();
            if (!orgId) return Promise.resolve(true); // Skip if no orgId

            // Call the debounced function here
            return debouncedApiCheck(value, orgId);
        })
    );
