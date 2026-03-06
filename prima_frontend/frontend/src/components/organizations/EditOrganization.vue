<script setup lang="ts">
    import { defineEmits, ref, watch } from 'vue';

    import type { Organization } from '@/types/organization';

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
        },
        organization: {
            type: Object as () => Organization | null,
            default: null
        }
    });

    const visible = ref(props.dialogVisible);

    watch(
        () => props.dialogVisible,
        (newVal) => {
            visible.value = newVal;
            if (visible.value && props.organization) {
                organizationFormStore.setOrganization(props.organization);
            }
        }
    );

    const emit = defineEmits(['closeDialog', 'organizationUpdated']);

    const onClose = () => {
        emit('closeDialog');
    };

    const updateOrganization = async () => {
        const response = await organizationManagementService.updateOrganization();
        if (response) {
            emit('organizationUpdated', response.organization);
        }
    };
</script>

<template>
    <div>
        <Dialog v-model:visible="visible" @hide="onClose" modal header="Edit Organization" :style="{ width: '25rem' }">
            <OrganizationForm :edit="true" />
            <div class="flex items-end justify-end gap-2 mt-4">
                <PButton type="button" label="Cancel" severity="secondary" @click="visible = false"></PButton>
                <PButton
                    type="button"
                    label="Save"
                    severity="primary"
                    @click="updateOrganization"
                    :disabled="organizationFormStore.v$.$invalid"
                ></PButton>
            </div>
        </Dialog>
    </div>
</template>
