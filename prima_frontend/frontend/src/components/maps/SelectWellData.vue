<script setup lang="ts">
    import { onMounted, computed } from 'vue';

    import { useAuthStore } from '@/stores/authStore';
    import { useWellOverviewStore } from '@/stores/wellOverviewStore';
    import { useOrganizationStore } from '@/stores/organizationStore';

    import type { Dataset } from '@/types/dataset';

    const authStore = useAuthStore();
    const wellOverviewStore = useWellOverviewStore();
    const organizationStore = useOrganizationStore();

    const organizations = computed(() => organizationStore.getOrganizations ?? []);
    const datasets = computed(
        () =>
            Object.values(wellOverviewStore.getAvailableDatasets).filter(
                (d: Dataset[]) => d[0]?.organization?.name === wellOverviewStore.getOrgName
            )[0]
    );
    const datasetDisabled = computed(() => datasets?.value?.length === 0 || wellOverviewStore.getOrgName === null);

    defineProps({
        loading: {
            required: false,
            type: Boolean,
            default: false
        }
    });

    const emit = defineEmits(['confirm', 'reset']);

    onMounted(async () => {
        await wellOverviewStore.fetchDatasets();
        await organizationStore.fetchOrganizations(true);

        if (!authStore.isSuperAdmin) {
            wellOverviewStore.setOrgName(authStore.getOrganization.name);
        }
    });

    const reset = () => {
        emit('reset');
        if (authStore.isSuperAdmin) {
            wellOverviewStore.setOrgName('');
            wellOverviewStore.setOrgCoordinates({ longitude: 0, latitude: 0 });
        }
        wellOverviewStore.resetSelectedDataset();
    };
</script>

<template>
    <div class="flex flex-col" v-if="organizations && organizations.length > 0">
        <h1 class="mb-8">Select a dataset to view</h1>
        <div class="flex flex-row items-center mb-4">
            <div class="font-bold mr-4 w-40">
                {{ authStore.isSuperAdmin ? 'Select an Organization:' : 'Organization:' }}
            </div>
            <PSelect
                :options="organizations"
                optionLabel="name"
                optionValue="name"
                placeholder="Select an Organization"
                v-model="wellOverviewStore.orgName"
                :disabled="!authStore.isSuperAdmin"
            ></PSelect>
        </div>

        <div class="flex flex-row items-center mb-4">
            <div class="font-bold mr-4 w-40">Select a dataset:</div>
            <PSelect
                :disabled="datasetDisabled"
                v-model="wellOverviewStore.dataset"
                :options="datasets"
                optionLabel="name"
                placeholder="Select a Dataset"
            ></PSelect>
        </div>

        <div class="gap-4 flex">
            <PButton @click="$emit('confirm')" :disabled="loading">Confirm Selection</PButton>
            <PButton severity="danger" @click="reset">Reset</PButton>
        </div>
    </div>
    <div v-else>
        <div>There are currently no datasets to choose from.</div>
    </div>
</template>
