<script setup lang="ts">
    import { ref, watch } from 'vue';

    import type { User } from '@/types/user';

    import { createUserManagementService } from '@/services/userManagementService';
    import { useUserFormStore } from '../../stores/form/userForm';

    import Dialog from 'primevue/dialog';
    import UserForm from './UserForm.vue';

    const userManagementService = createUserManagementService();
    const userFormStore = useUserFormStore();

    const props = defineProps({
        dialogVisible: {
            type: Boolean,
            default: false
        },
        user: {
            type: Object as () => User | null,
            default: null
        }
    });

    const visible = ref(props.dialogVisible);
    const loading = ref(false);

    watch(
        () => props.dialogVisible,
        (newVal) => {
            visible.value = newVal;
            if (visible.value && props.user) {
                userFormStore.setUser(props.user);
            }
        }
    );

    const emit = defineEmits(['closeDialog', 'userUpdated']);

    const onClose = () => {
        emit('closeDialog');
    };

    const updateUser = async () => {
        if (userFormStore.v$.$invalid) {
            return;
        }
        loading.value = true;
        const response = await userManagementService.updateUser();
        if (response) {
            emit('userUpdated', response);
        }

        loading.value = false;
    };
</script>

<template>
    <div>
        <Dialog v-model:visible="visible" @hide="onClose" modal header="Edit User" :style="{ width: '25rem' }">
            <UserForm :edit="true" />
            <div class="flex items-end justify-end gap-2 mt-4">
                <PButton type="button" label="Cancel" severity="secondary" @click="visible = false"></PButton>
                <PButton
                    type="button"
                    label="Save"
                    severity="primary"
                    @click="updateUser"
                    :disabled="userFormStore.v$.$invalid || loading"
                ></PButton>
            </div>
        </Dialog>
    </div>
</template>
