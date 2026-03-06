<script setup lang="ts">
    import { ref, onMounted, nextTick, watchEffect, watch, onUnmounted, computed } from 'vue';

    import type { ScenarioProject } from '@/types/projects';
    import { createMapService } from '@/services/mapService';
    import { createProjectDownloadService } from '@/services/projectDownloadService';
    import { useMapStore } from '@/stores/mapStore';

    import IconGasWells from '../icons/IconGasWells.vue';
    import IconOilWells from '../icons/IconOilWells.vue';
    import IconBothWells from '../icons/IconBothWells.vue';
    import type { Scenario } from '@/types/scenario';
    import type { Well } from '@/types/well';
    import { useAuthStore } from '@/stores/authStore';
    import { useWellOverviewStore } from '@/stores/wellOverviewStore';

    const props = defineProps({
        activeTab: {
            required: true
        },
        visibleProjects: {
            required: false,
            type: Array as () => ScenarioProject[],
            default: () => []
        },
        visibleScenarios: {
            required: false,
            type: Array as () => Scenario[],
            default: () => []
        },
        mapKey: {
            required: false,
            type: Number,
            default: 1
        },
        scenario: {
            required: false,
            type: Object as () => Scenario,
            default: () => null
        },
        singleWell: {
            required: false,
            type: Object as () => Well | null,
            default: () => null
        },
        triggerDownload: {
            required: false,
            type: Number,
            default: 0
        },
        loading: {
            required: false,
            type: Boolean,
            default: false
        }
    });

    const emit = defineEmits(['download-complete']);

    const mapContainer = ref(null);
    const mapInitialized = ref(false);
    const onLoadHandled = ref(false);
    const mapService = createMapService();
    const mapStore = useMapStore();
    const authStore = useAuthStore();
    const projectDownloadService = createProjectDownloadService();
    const currentVisibleProjects = ref<ScenarioProject[]>([...props.visibleProjects]);
    const mapName = `scenariosMap${props.mapKey}`;
    const wellOverviewStore = useWellOverviewStore();
    const coordinates = computed(() => wellOverviewStore.getOrgCoordinates);
    const rankOnlyVisible = computed(() => {
        return (
            props.visibleScenarios.length !== 0 &&
            props.visibleScenarios.some((scenario: Scenario) => scenario.isRankOnly)
        );
    });

    function updateVisibleScenariosOnMap(newScenarioIds: Array<number>) {
        const scenarioLength = newScenarioIds.length;

        if (!props.scenario) {
            if (scenarioLength === 1) {
                mapService.updateScenarioBasedColors(mapName, newScenarioIds, props.visibleProjects || []);
                return;
            } else {
                mapService.updateScenarioBasedColors(mapName, newScenarioIds, props.visibleProjects || []);
            }
        }
    }

    const downloadProjects = () => {
        const map = mapStore.getMap(mapName);
        if (!map) return;

        const canvas = map.getCanvas();

        const dataUrl = canvas.toDataURL('image/png');
        const colorData = projectDownloadService.getColorData(mapName, currentVisibleProjects.value);

        projectDownloadService.downloadScenarioData(
            dataUrl,
            colorData.projects,
            canvas.width,
            canvas.height,
            props.visibleScenarios[0]
        );

        emit('download-complete');
    };

    const onLoadListener = () => {
        if (!onLoadHandled.value) {
            mapService.createCountyLayer(mapName);
            mapInitialized.value = true;
            onLoadHandled.value = true; // Mark onLoad as handled

            // Set initial map points, mostly used for switching between comparison views.
            if (props.scenario) {
                updateVisibleScenariosOnMap([props.scenario.id]);
                props.visibleProjects.forEach((project) => {
                    mapService.createOrUpdateMapPoints(mapName, { Project: project });
                });
                if (props.scenario.latitude && props.scenario.longitude) {
                    mapService.setMapCenterToCoordinates(mapName, props.scenario.latitude, props.scenario.longitude);
                }
            } else {
                props.visibleProjects.forEach((project) => {
                    mapService.createOrUpdateMapPoints(mapName, { Project: project });
                });

                updateVisibleScenariosOnMap(activeScenarioIds.value);
            }

            if (props.singleWell && (props.scenario?.id === props.singleWell.scenarioId || !props.scenario)) {
                mapService.easeToCoordinates(mapName, props.singleWell);
            }

            if (props.triggerDownload && props.visibleScenarios.length === 1) {
                const targetScenario = props.visibleScenarios[0];
                if (targetScenario.latitude && targetScenario.longitude) {
                    mapService.setMapCenterToCoordinates(mapName, targetScenario.latitude, targetScenario.longitude);
                    setTimeout(() => {
                        downloadProjects();
                    }, 1200);
                } else {
                    downloadProjects();
                }
            }

            mapService.resize(mapName);
        }
    };

    onMounted(async () => {
        await nextTick();

        if (coordinates.value.longitude === 0 && coordinates.value.latitude === 0 && !authStore.isSuperAdmin) {
            wellOverviewStore.setOrgCoordinates({
                longitude: authStore.getOrganization.longitude,
                latitude: authStore.getOrganization.latitude
            });

            await nextTick();
        }

        if (!mapInitialized.value) {
            mapService.initializeMap(
                mapName,
                mapContainer.value || '',
                [coordinates.value.longitude ?? -75.6107, coordinates.value.latitude ?? 42.9377],
                authStore.isSuperAdmin
            );

            mapService.addLoadListener(mapName, onLoadListener);
        }
    });

    onUnmounted(() => {
        mapService.removeLoadListener(mapName, onLoadListener);
    });

    const activeScenarioIds = computed(() => {
        return props.visibleScenarios?.map((scenario) => scenario.id);
    });

    watchEffect(() => {
        if (props.activeTab === 0) {
            nextTick(() => {
                const map = mapStore.getMap(mapName);
                if (map) {
                    map.resize();
                } else {
                    console.error(`Map with name ${mapName} is not initialized.`);
                }
            });
        }
    });

    watch(
        () => props.visibleProjects,
        (newVal) => {
            if (JSON.stringify(newVal) !== JSON.stringify(currentVisibleProjects.value)) {
                currentVisibleProjects.value = [...newVal];
            }
        },
        { deep: true }
    );

    // This toggle functionality is not using the prop directly because of lack of Vue handling of reactivity
    watch(
        () => currentVisibleProjects.value,
        (newVal, oldVal) => {
            if (newVal && mapStore.getMap(mapName)) {
                const newSet = new Set(Object.values(newVal).map((project) => project.id)); // Adjust property if needed
                const oldSet = oldVal ? new Set(Object.values(oldVal).map((project) => project.id)) : new Set(); // Adjust property if needed

                // Find items to remove
                if (oldVal) {
                    Object.values(oldVal).forEach((project) => {
                        if (!newSet.has(project.id)) {
                            mapService.toggleProjectLayerVisibility(mapName, project.id);
                        }
                    });
                }

                // Find items to add
                Object.values(newVal).forEach((project) => {
                    if (!oldSet.has(project.id)) {
                        mapService.createOrUpdateMapPoints(mapName, { Project: project });
                    }
                });
            }
        },
        { deep: true }
    );

    watch(
        () => activeScenarioIds.value.filter((id): id is number => id !== undefined),
        (newVal) => {
            if (newVal && mapStore.getMap(mapName)) {
                nextTick(() => {
                    updateVisibleScenariosOnMap(newVal);
                });
            }
        },
        { deep: true }
    );

    watch(
        () => props.triggerDownload,
        (newVal) => {
            if (newVal) {
                downloadProjects();
            }
        }
    );

    watch(
        () => coordinates.value,
        (newCoordinates, oldCoordinates) => {
            if (
                newCoordinates &&
                (newCoordinates.latitude !== 0 || newCoordinates.longitude !== 0) &&
                (newCoordinates.latitude !== oldCoordinates?.latitude ||
                    newCoordinates.longitude !== oldCoordinates?.longitude)
            ) {
                nextTick(() => {
                    setTimeout(() => {
                        mapService.setMapCenterToCoordinates(
                            mapName,
                            newCoordinates.latitude,
                            newCoordinates.longitude
                        );
                    }, 100);
                });
            }
        },
        { deep: true, immediate: true }
    );
</script>

<template>
    <div class="container relative">
        <div class="mapbox w-full" ref="mapContainer"></div>
        <div id="spinner" class="spinner" :class="loading ? '' : 'hidden'"></div>
        <div id="overlay" class="overlay" :class="loading ? '' : 'hidden'"></div>
        <div
            id="legend"
            class="absolute top-0 right-0 mt-2 mr-2 bg-white rounded-md p-3 z-10 border-2 border-gray-400 border-solid"
        >
            <div class="flex items-center mb-2">
                <div class="font-bold italic flex items-center"><IconGasWells /><span class="mt-1">DOW</span></div>
            </div>
            <div class="flex items-center mb-2">
                <div class="font-bold flex items-center italic"><IconOilWells /><span class="mt-1">LUOW</span></div>
            </div>
            <!-- <div class="flex items-center mb-2">
                <div class="font-bold flex items-center italic">
                    <IconBothWells /><span class="mt-1">&nbsp;Oil & Gas Well</span>
                </div>
            </div> -->
            <div class="flex items-center" :class="rankOnlyVisible ? 'mb-2' : ''">
                <div class="font-bold flex items-center italic ml-[0.75]">
                    <div class="rounded-full border-[#f57e42] border-2 border-solid h-[20px] w-[20px] mt-1"></div>

                    <span class="ml-1">Intersection</span>
                </div>
            </div>
            <div v-if="rankOnlyVisible" class="flex items-center justify-center hover:cursor-help">
                <div
                    v-tooltip.left="{
                        value: 'A Scenario configured for Well Ranking only has been selected and does not include any P&A project recommendations, and therefore will not be shown. \n\n If you wish to obtain the corresponding P&A project recommendations, please use the Copy and Edit Scenario Inputs button for the scenario. This will allow you to create a new scenario. When doing so, be sure to select the P&A Project Recommendations use case to access this functionality.',
                        pt: {
                            text: '!bg-yellow-100 !text-black !font-medium w-[300px]'
                        }
                    }"
                >
                    <i class="pi pi-exclamation-triangle text-yellow-500" style="font-size: 30px"></i>
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped>
    .container {
        height: 100%;
    }
    .mapbox {
        height: 75vh; /* You need to set a height for the map container */
        width: 100%; /* You can also set a width, or use flex as needed */
    }
    #legend {
        padding: 10px;
        font-size: 14px;
    }
    .legend div span {
        display: inline-block;
        height: 10px;
        width: 10px;
        margin-right: 5px;
    }

    .mapboxgl-popup {
        max-width: 400px;
        font:
            12px/20px 'Helvetica Neue',
            Arial,
            Helvetica,
            sans-serif;
    }

    .spinner {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        border: 8px solid #f3f3f3;
        border-top: 8px solid #3498db;
        border-radius: 50%;
        width: 60px;
        height: 60px;
        animation: spin 1s linear infinite;
    }

    .overlay {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(0, 0, 0, 0.5); /* 50% gray transparency */
        z-index: 10;
    }

    .hidden {
        display: none;
    }

    @keyframes spin {
        0% {
            transform: rotate(0deg);
        }
        100% {
            transform: rotate(360deg);
        }
    }
</style>
