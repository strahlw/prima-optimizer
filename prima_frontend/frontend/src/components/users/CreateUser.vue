<script setup lang="ts">
    import { ref, watchEffect } from 'vue';

    import { createUserManagementService } from '@/services/userManagementService';
    import { useUserFormStore } from '../../stores/form/userForm';
    import type { Organization } from '../../types/organization';

    import Dialog from 'primevue/dialog';
    import UserForm from './UserForm.vue';

    const userManagementService = createUserManagementService();
    const userFormStore = useUserFormStore();

    const props = defineProps({
        dialogVisible: {
            type: Boolean,
            default: false
        },
        selectedOrg: {
            type: Object as () => Organization,
            default: null
        }
    });

    const visible = ref(props.dialogVisible);
    const loading = ref(false);

    watchEffect(() => {
        visible.value = props.dialogVisible;
    });

    const emit = defineEmits(['closeDialog', 'userCreated']);

    const onClose = () => {
        emit('closeDialog');
    };

    const createUser = async () => {
        if (userFormStore.v$.$invalid) {
            return;
        }

        loading.value = true;
        const response = await userManagementService.createUser();
        if (response) {
            emit('userCreated', response);
        }

        loading.value = false;
    };
</script>

<template>
    <div>
        <Dialog v-model:visible="visible" @hide="onClose" modal header="Create User" :style="{ width: '25rem' }">
            <UserForm :selectedOrg="selectedOrg" />
            <div class="flex items-end justify-end gap-2 mt-4">
                <PButton type="button" label="Cancel" severity="secondary" @click="visible = false"></PButton>
                <PButton
                    type="button"
                    label="Save"
                    severity="primary"
                    @click="createUser"
                    :disabled="userFormStore.v$.$invalid || loading"
                ></PButton>
            </div>
        </Dialog>
    </div>
</template>
