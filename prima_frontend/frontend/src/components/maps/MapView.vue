<script setup lang="ts">
    import { ref, onMounted, onUnmounted, nextTick, watchEffect, computed } from 'vue';
    import type { PropType } from 'vue';
    import type { Well } from '@/types/well';

    import IconGasWells from '../icons/IconGasWells.vue';
    import IconOilWells from '../icons/IconOilWells.vue';
    import IconBothWells from '../icons/IconBothWells.vue';

    import { useMapStore } from '@/stores/mapStore';
    import { useAuthStore } from '@/stores/authStore';
    import { createMapService } from '@/services/mapService';
    import { useWellOverviewStore } from '@/stores/wellOverviewStore';

    const props = defineProps({
        activeTab: {
            required: true
        },
        singleWell: {
            required: false,
            type: Object as PropType<Well>
        },
        specificProject: {
            required: false,
            type: Object
        },
        datasetSelected: {
            required: false,
            type: Boolean
        }
    });

    const wellOverviewStore = useWellOverviewStore();
    const mapContainer = ref(null);
    const mapInitialized = ref(false);
    const onLoadHandled = ref(false);
    const mapStore = useMapStore();
    const authStore = useAuthStore();
    const mapService = createMapService();
    const mapName = 'data_set_map';
    const coordinates = computed(() => wellOverviewStore.getOrgCoordinates);

    const onLoadListener = () => {
        if (!onLoadHandled.value) {
            mapService.createCountyLayer(mapName);
            if (wellOverviewStore.getDatasetLocations.length > 0) {
                mapService.createOrUpdateMapPointsFromDataset(mapName, wellOverviewStore.getDatasetLocations);
            }
            mapInitialized.value = true;
            onLoadHandled.value = true; // Mark onLoad as handled

            if (props.singleWell) {
                mapService.easeToCoordinates(mapName, props.singleWell);
            }
        }
    };

    onMounted(() => {
        if (coordinates.value.longitude === 0 && coordinates.value.latitude === 0 && !authStore.isSuperAdmin) {
            wellOverviewStore.setOrgCoordinates({
                longitude: authStore.getOrganization.longitude,
                latitude: authStore.getOrganization.latitude
            });
        }

        if (!mapInitialized.value) {
            mapService.initializeMap(
                mapName,
                mapContainer.value || '',
                [coordinates.value.longitude ?? -75.6107, coordinates.value.latitude ?? 42.9377],
                authStore.isSuperAdmin && !props.datasetSelected
            );

            mapService.addLoadListener(mapName, onLoadListener);
        }
    });

    onUnmounted(() => {
        mapService.removeLoadListener(mapName, onLoadListener);
    });

    watchEffect(() => {
        if (props.activeTab === 0 && onLoadHandled.value) {
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
</script>
<template>
    <div class="container relative">
        <div class="mapbox w-full" ref="mapContainer"></div>
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
            <!-- <div class="flex items-center">
                <div class="font-bold flex items-center italic">
                    <IconBothWells /><span class="mt-1">&nbsp;Oil & Gas Well</span>
                </div>
            </div> -->
        </div>
    </div>
</template>

<style scoped>
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
</style>
