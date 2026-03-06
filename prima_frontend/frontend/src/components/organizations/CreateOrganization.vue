<script setup lang="ts">
    import { ref, watchEffect } from 'vue';

    import { createOrganizationManagementService } from '@/services/organizationManagementService';
    import { useOrganizationFormStore } from '@/stores/form/organizationForm';

    import Dialog from 'primevue/dialog';
    import OrganizationForm from './OrganizationForm.vue';

    const organizationManagementService = createOrganizationManagementService();
    const organizationFormStore = useOrganizationFormStore();

    const props = defineProps({
        dialogVisible: {
            type: Boolean,
            default: false
        }
    });

    const visible = ref(props.dialogVisible);

    watchEffect(() => {
        visible.value = props.dialogVisible;
    });

    const emit = defineEmits(['closeDialog', 'organizationCreated']);

    const onClose = () => {
        emit('closeDialog');
    };

    const createOrganization = async () => {
        const response = await organizationManagementService.createOrganization();
        if (response) {
            emit('organizationCreated', response.organization);
        }
    };
</script>

<template>
    <div>
        <Dialog
            v-model:visible="visible"
            @hide="onClose"
            modal
            header="Create Organization"
            :style="{ width: '25rem' }"
        >
            <OrganizationForm />
            <div class="flex items-end justify-end gap-2 mt-4">
                <PButton type="button" label="Cancel" severity="secondary" @click="visible = false"></PButton>
                <PButton
                    type="button"
                    label="Save"
                    severity="primary"
                    @click="createOrganization"
                    :disabled="organizationFormStore.v$.$invalid"
                ></PButton>
            </div>
        </Dialog>
    </div>
</template>
