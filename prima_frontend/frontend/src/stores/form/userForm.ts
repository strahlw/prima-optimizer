import { defineStore } from 'pinia';
import { reactive, ref, computed } from 'vue';
import useVuelidate from '@vuelidate/core';
import { required, email, numeric, requiredIf } from '@vuelidate/validators';
import type { User } from '../../types/user';
import { deepCopy } from '../../utils/deepCopy';

export interface UserForm {
    id?: number | null;
    firstName: string;
    lastName: string;
    email: string;
    roleId: number | null;
    organizationId: number | null;
}

export interface UserFormErrors {
    firstName: Array<string> | null;
    lastName: Array<string> | null;
    email: Array<string> | null;
    roleId: Array<string> | null;
    organizationId: Array<string> | null;
}

const initialUserForm: UserForm = {
    id: null,
    firstName: '',
    lastName: '',
    email: '',
    roleId: null,
    organizationId: null
};

const initialUserFormErrors = {
    firstName: [],
    lastName: [],
    email: [],
    roleId: [],
    organizationId: []
};

export const useUserFormStore = defineStore('userForm', () => {
    const $externalResults = ref(deepCopy(initialUserFormErrors));
    const form = reactive(deepCopy(initialUserForm));
    const isOrganizationIdRequired = computed(() => form.roleId !== 1);

    const validationRules = {
        firstName: { required },
        lastName: { required },
        email: { required, email },
        roleId: { required, numeric },
        organizationId: {
            required: requiredIf(isOrganizationIdRequired), // Required only if roleId is not 1
            numeric
        }
    };

    const v$ = useVuelidate(validationRules, form, { $externalResults });

    const resetForm = () => {
        Object.assign(form, deepCopy(initialUserForm));
        v$.value.$reset();
    };

    const setExternalResults = (errorData: any) => {
        $externalResults.value = errorData;
    };

    const resetExternalResult = (field: string) => {
        $externalResults.value = deepCopy({ ...$externalResults.value, [field]: [] });
    };

    const setUser = (user: User) => {
        form.id = user.id;
        form.firstName = user.firstName;
        form.lastName = user.lastName;
        form.email = user.email;
        form.roleId = user.roleId;
        form.organizationId = user.organizationId === 0 ? null : user.organizationId;
    };

    return {
        form,
        v$,
        resetForm,
        setUser,
        setExternalResults,
        resetExternalResult
    };
});
