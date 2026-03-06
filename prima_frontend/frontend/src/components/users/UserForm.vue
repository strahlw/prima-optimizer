<script setup lang="ts">
    import { useUserFormStore } from '@/stores/form/userForm';
    import { useAuthStore } from '@/stores/authStore';
    import { usePermissions } from '@/composables/usePermissions';
    import { useOrganizationStore } from '@/stores/organizationStore';
    import { onMounted, computed } from 'vue';
    import type { Organization } from '@/types/organization';

    const userFormStore = useUserFormStore();
    const organizationStore = useOrganizationStore();
    const authStore = useAuthStore();
    const { form, resetForm, v$, resetExternalResult } = userFormStore;
    const { hasPermission } = usePermissions();
    const selectableRoles = computed(() => {
        const roles = authStore.getAvailableRoles.filter((role) =>
            props.edit && form.roleId !== 1 ? role.name !== 'super-admin' : role
        );

        if (!hasPermission('add-super-admins') && !props.edit) {
            return roles.filter((role) => role.name !== 'super-admin');
        }

        return roles;
    });

    const props = defineProps({
        selectedOrg: {
            type: Object as () => Organization,
            default: null
        },
        edit: {
            type: Boolean,
            default: false
        }
    });

    onMounted(() => {
        // An Organization Admin can only create a normal user.
        if (!props.edit) {
            resetForm();
        }

        if (!hasPermission('add-org-admins') && authStore.getUser?.id !== form.id) {
            const userRole = authStore.getAvailableRoles.find((role) => role.name === 'user');
            if (userRole) {
                form.roleId = userRole.id;
            }
        }

        if (props.selectedOrg) {
            form.organizationId = props.selectedOrg.id;
        }
    });

    const touchAndResetField = (field: string) => {
        resetExternalResult(field);
        if (v$[field]) {
            v$[field].$touch();
        }
    };
</script>

<template>
    <div>
        <div>
            <label for="firstName" class="block mb-2 text-xs">First Name:</label>
            <InputText
                class="w-full"
                id="firstName"
                placeholder="First Name"
                type="text"
                v-model="form.firstName"
                @input="touchAndResetField('firstName')"
                @blur="touchAndResetField('firstName')"
            ></InputText>
            <ValidationError :errors="v$.firstName.$errors" />
            <ValidationError
                :errors="v$.firstName.$externalResults"
                v-if="v$.firstName.$errors.length === 0 && v$.firstName.$externalResults.length !== 0"
            />
        </div>

        <div class="mt-4">
            <label for="lastName" class="block mb-2 text-xs">Last Name:</label>
            <InputText
                class="w-full"
                id="lastName"
                placeholder="Last Name"
                type="text"
                v-model="form.lastName"
                @input="touchAndResetField('lastName')"
                @blur="touchAndResetField('lastName')"
            ></InputText>
            <ValidationError :errors="v$.lastName.$errors" />
            <ValidationError
                :errors="v$.lastName.$externalResults"
                v-if="v$.lastName.$errors.length === 0 && v$.lastName.$externalResults.length !== 0"
            />
        </div>

        <div class="mt-4">
            <label for="email" class="block mb-2 text-xs">Email:</label>
            <InputText
                class="w-full"
                id="email"
                placeholder="Email"
                type="email"
                autocomplete="off"
                v-model="form.email"
                :disabled="edit"
                @input="touchAndResetField('email')"
                @blur="touchAndResetField('email')"
            ></InputText>
            <ValidationError :errors="v$.email.$errors" />
            <ValidationError
                :errors="v$.email.$externalResults"
                v-if="v$.email.$errors.length === 0 && v$.email.$externalResults.length !== 0"
            />
        </div>

        <div :hidden="!hasPermission('add-org-admins')" class="mt-4">
            <label for="role" class="block mb-2 text-xs">Role:</label>
            <PSelect
                :options="selectableRoles"
                optionLabel="label"
                optionValue="id"
                placeholder="Select a role"
                v-model="form.roleId"
                :hidden="!hasPermission('add-org-admins')"
                :disabled="!hasPermission('add-org-admins')"
                id="role"
                name="role"
                @input="touchAndResetField('roleId')"
                @blur="touchAndResetField('roleId')"
            ></PSelect>
            <ValidationError :errors="v$.roleId.$errors" />
            <ValidationError
                :errors="v$.roleId.$externalResults"
                v-if="v$.roleId.$errors.length === 0 && v$.roleId.$externalResults.length !== 0"
            />
        </div>

        <div :hidden="!hasPermission('add-org-admins')" class="mt-4">
            <label for="organization" class="block mb-2 text-xs">Organization:</label>
            <PSelect
                :options="organizationStore.getOrganizations"
                optionLabel="key"
                optionValue="id"
                placeholder="Select an organization"
                v-model="form.organizationId"
                :hidden="!hasPermission('add-org-admins')"
                :disabled="!hasPermission('add-org-admins') || edit"
                id="organization"
                name="organization"
                @input="touchAndResetField('organizationId')"
                @blur="touchAndResetField('organizationId')"
            ></PSelect>
            <ValidationError :errors="v$.organizationId.$errors" />
            <ValidationError
                :errors="v$.organizationId.$externalResults"
                v-if="v$.organizationId.$errors.length === 0 && v$.organizationId.$externalResults.length !== 0"
            />
        </div>
    </div>
</template>
