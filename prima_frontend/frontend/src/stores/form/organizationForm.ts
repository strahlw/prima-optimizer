import { defineStore } from 'pinia';
import { reactive, watch } from 'vue';
import useVuelidate from '@vuelidate/core';
import type { Organization } from '../../types/organization';
import { deepCopy } from '../../utils/deepCopy';
import { validationRules, initialOrganizationForm } from '../../constants/organizationForm';

export const useOrganizationFormStore = defineStore('organizationForm', () => {
    const form = reactive(deepCopy(initialOrganizationForm));
    // logo: { requiredUnless: () => !!form.logoUrl || !!form.logo } saving this incase we need to add it back
    const v$ = useVuelidate({ ...validationRules }, form);

    const resetForm = () => {
        Object.assign(form, deepCopy(initialOrganizationForm));
        v$.value.$reset();
    };

    watch(
        () => form.logoUrl,
        () => {
            v$.value.$touch(); // Trigger validation whenever logoUrl changes
        }
    );

    const setOrganization = (organization: Organization) => {
        form.id = organization.id;
        form.key = organization.key;
        form.name = organization.name;
        form.logo = organization.logo || null;
        form.availableFunding = organization.availableFunding;
        form.wellCount = organization.wellCount;
        form.paTarget = organization.paTarget;
        form.longitude = organization.longitude;
        form.latitude = organization.latitude;
        form.logoUrl = organization.logoUrl || null;
    };

    return {
        form,
        v$,
        resetForm,
        setOrganization
    };
});
