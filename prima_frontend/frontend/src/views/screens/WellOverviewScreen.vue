<script setup lang="ts">
    import { ref, watch, onMounted, computed } from 'vue';
    import { useRoute, useRouter } from 'vue-router';

    import MapView from '../../components/maps/MapView.vue';
    import WellData from '../../components/maps/WellData.vue';
    import SelectWellData from '../../components/maps/SelectWellData.vue';
    import { Tabs, Tab, TabList, TabPanels, TabPanel } from 'primevue';

    import type { Well } from '@/types/well';
    import type { Dataset, DatasetJson, DatasetJsonLocation } from '@/types/dataset';
    import type { Organization } from '@/types/organization';
    import { useWellOverviewStore } from '@/stores/wellOverviewStore';
    import { useOrganizationStore } from '@/stores/organizationStore';
    import { useAuthStore } from '@/stores/authStore';
    import { createDatasetService } from '../../services/datasetService';

    defineProps({
        oilWells: {
            required: false, //set to false for now
            type: Object // setting as object as thats what im expecting
        },
        gasWells: {
            required: false,
            type: Object
        }
    });

    const { getDatasetLocationData } = createDatasetService();
    const route = useRoute();
    const router = useRouter();
    const authStore = useAuthStore();
    const activeTab = ref(0);
    const loading = ref<boolean>(false);
    const singleWell = ref<Well | undefined>(undefined);
    const wellOverviewStore = useWellOverviewStore();
    const organizationStore = useOrganizationStore();
    const organizations = computed(() => organizationStore.getOrganizations ?? []);
    const datasets = computed(() =>
        Object.values(wellOverviewStore.getAvailableDatasets).flatMap((val: Array<any>) => val)
    );

    //watch to not hold map at singular point
    watch(activeTab, (newVal) => {
        if (newVal === 1) {
            singleWell.value = undefined;
        }
    });

    function convertToWell(datasetLocation: DatasetJsonLocation | DatasetJson): Well {
        return {
            wellId: datasetLocation.wellId.value,
            wellType: datasetLocation.wellType.value,
            depth: datasetLocation.depth?.value || null,
            wellName: datasetLocation.wellName?.value || 'Unknown',
            operatorName: datasetLocation.operatorName?.value || 'Unknown',
            latitude: datasetLocation.latitude.value,
            longitude: datasetLocation.longitude.value,
            age: 0, // Irrelevant
            compliance: false, // Irrelevant
            incident: false, // Irrelevant
            leak: false, // Irrelevant
            violation: false, // Irrelevant
            h2sLeak: false, // Irrelevant
            datasetJsonId: '', // Irrelevant
            priorityScore: 0, // Irrelevant,
            taskId: '' // Irrelevant
        };
    }

    const focusClickedWell = (rowData: DatasetJson) => {
        activeTab.value = 0;
        singleWell.value = convertToWell(rowData);
    };

    async function loadDataset(datasetId?: number, wellId?: number) {
        if (!wellOverviewStore.getDataset && !datasetId) {
            loading.value = false;
            return;
        }

        if (wellOverviewStore.getDataset || datasetId) {
            loading.value = true;
            try {
                const id = datasetId ? datasetId : wellOverviewStore.getDataset?.id;
                if (id) {
                    const response = await getDatasetLocationData(id);
                    if (response.data) {
                        const org = organizations.value.find(
                            (o: Organization) => o.name === wellOverviewStore.getOrgName
                        );
                        if (org) {
                            wellOverviewStore.setOrgCoordinates({
                                longitude: org.longitude,
                                latitude: org.latitude
                            });
                        }
                        wellOverviewStore.setDatasetLocations(response.data);

                        if (wellId) {
                            const foundLocation = wellOverviewStore.getDatasetLocations.find(
                                (d: DatasetJsonLocation) => d.wellId.value === +wellId
                            );

                            singleWell.value = foundLocation ? convertToWell(foundLocation) : undefined;
                        }
                    }
                }
                loading.value = false;
            } catch (error) {
                console.error(error);
                loading.value = false;
            }
        }
    }

    function resetSpecifications() {
        router.replace({ path: route.path, query: {} });
        singleWell.value = undefined;
    }

    function loadSelectedDataset() {
        resetSpecifications();
        loadDataset();
    }

    onMounted(async () => {
        loading.value = true;
        const { wellId, datasetId } = route.query;
        await wellOverviewStore.fetchDatasets();
        await organizationStore.fetchOrganizations(true);

        if (!authStore.isSuperAdmin) {
            wellOverviewStore.setOrgName(authStore.getOrganization.name);
        }

        if (!!datasetId && !!wellId) {
            const dataset = datasets.value?.find((d: Dataset) => d.id == +datasetId);
            wellOverviewStore.setDataset(dataset);
            const org = organizations.value.find((o: Organization) => o.id === dataset?.organizationId);
            if (org) {
                wellOverviewStore.setOrgName(org.name);
            }
            await loadDataset(+datasetId, +wellId);
        } else if (
            wellOverviewStore.getOrgCoordinates.latitude === 0 &&
            wellOverviewStore.getOrgCoordinates.longitude === 0
        ) {
            activeTab.value = 2;
            loading.value = false;
        } else {
            loading.value = false;
        }
    });
</script>
<template>
    <div class="w-screen ml-auto mr-auto">
        <Tabs :value="`${activeTab}`" @update:value="activeTab = Number($event)" class="w-full">
            <TabList
                :pt="{
                    activeBar: { class: 'bg-secondary border-b-4 border-secondary' },
                    tabList: { class: 'bg-bgDefault' }
                }"
            >
                <Tab value="0" :pt="{ root: { class: 'text-secondary-500 bg-bgDefault' } }"
                    ><div :class="{ 'opacity-50': activeTab !== 0 }" class="flex items-center space-x-1">
                        <i class="p-2 pi pi-map text-xl"></i>
                        <div class="text-black">Well Overview</div>
                    </div></Tab
                >
                <Tab value="1" :pt="{ root: { class: 'text-secondary-500 bg-bgDefault' } }"
                    ><div :class="{ 'opacity-50': activeTab !== 1 }" class="flex items-center" @click="activeTab = 1">
                        <i class="p-2 pi pi-folder-open text-xl"></i>
                        <div class="text-black">Well Data</div>
                    </div></Tab
                >
                <Tab value="2" :pt="{ root: { class: 'text-secondary-500 bg-bgDefault' } }">
                    <div :class="{ 'opacity-50': activeTab !== 2 }" class="flex items-center" @click="activeTab = 2">
                        <i class="p-2 pi pi-file-plus text-xl"></i>
                        <div class="text-black">Select Well Data</div>
                    </div></Tab
                ></TabList
            >
            <TabPanels :pt="{ root: { class: 'bg-bgDefault' } }">
                <TabPanel value="0"
                    ><div v-if="activeTab === 0 && loading" class="flex flex-1 justify-center items-center h-full">
                        <ProgressSpinner />
                    </div>

                    <div class="p-col-12" v-if="activeTab === 0 && !loading">
                        <div class="m-2">
                            <MapView
                                :activeTab="activeTab"
                                :singleWell="singleWell"
                                :datasetSelected="wellOverviewStore.getDatasetLocations.length > 0"
                            />
                        </div></div
                ></TabPanel>
                <TabPanel value="1"
                    ><div class="p-col-12" v-if="activeTab === 1">
                        <div class="m-2">
                            <WellData @change-tab="focusClickedWell" />
                        </div></div
                ></TabPanel>
                <TabPanel value="2"
                    ><div class="p-col-12" v-if="activeTab === 2">
                        <div class="m-2">
                            <SelectWellData
                                :loading="loading"
                                @confirm="loadSelectedDataset"
                                @reset="resetSpecifications"
                            />
                        </div></div
                ></TabPanel>
            </TabPanels>
        </Tabs>
    </div>
</template>

<style scoped>
    .border-b-4 {
        border-bottom: 5px solid #f0f0f0 !important;
    }
    /* TODO: Update */
    .tabview .p-tabview-nav li {
        opacity: 0.5;
    }

    .tabview .p-tabview-nav li.p-highlight {
        opacity: 1;
    }
</style>
