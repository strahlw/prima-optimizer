<script setup lang="ts">
    import { computed, ref } from 'vue';

    import { useAuthStore } from '@/stores/authStore';
    import { useOrganizationStore } from '@/stores/organizationStore';

    import type { Organization } from '@/types/organization';

    const authStore = useAuthStore();
    const organizationStore = useOrganizationStore();

    const organizations = computed(() => organizationStore.getOrganizations ?? []);
    const selectedOrganization = ref<Organization | null>();

    const emit = defineEmits(['organizationSelected']);

    const onOrganizationChange = async () => {
        if (selectedOrganization.value) {
            emit('organizationSelected', selectedOrganization.value);
        }
    };
</script>

<template>
    <div class="flex flex-col" v-if="organizations && organizations.length > 0">
        <div class="flex flex-row items-center mb-4">
            <PSelect
                :options="organizations"
                optionLabel="name"
                optionValue="id"
                placeholder="Select an Organization"
                v-model="selectedOrganization"
                :disabled="!authStore.isSuperAdmin"
                @change="onOrganizationChange"
                :pt="{ label: { class: 'text-base font-normal' } }"
            ></PSelect>
        </div>
    </div>
    <div v-else>
        <div>There are currently no datasets to choose from.</div>
    </div>
</template>
