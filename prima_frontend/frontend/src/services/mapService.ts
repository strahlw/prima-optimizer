import mapboxgl from 'mapbox-gl';
import GeoJSON from 'geojson';

import type { Project, ScenarioProject } from '@/types/projects';
import type { Well } from '@/types/well';
import type { DatasetJsonLocation } from '@/types/dataset';

import { useMapStore } from '@/stores/mapStore';
import { LAYER_LAYOUT } from '@/constants/mapConstants';
import { wellColors } from '@/constants/wellConstants';

export function createMapService() {
    const mapStore = useMapStore();
    const mapStyle = 'mapbox://styles/mapbox/streets-v12';
    let updateTimeout: ReturnType<typeof setTimeout> | null = null;

    const US_CENTER_COORDINATES: [number, number] = [-98.5795, 39.8283]; // Longitude, Latitude
    const SUPER_ADMIN_ZOOM_LEVEL = 4;
    const DEFAULT_ZOOM_LEVEL = 6;
    const wellIconLookup = {
        Gas: 'gas-icon',
        Oil: 'oil-icon',
        Both: 'both-icon'
    };

    const initializeMap = (
        mapId: string,
        container: string | HTMLElement,
        center: [number, number],
        isSuperAdmin: boolean
    ): mapboxgl.Map => {
        mapboxgl.accessToken = import.meta.env.VITE_APP_MAPBOX_TOKEN;

        const newMap = new mapboxgl.Map({
            container: container,
            style: mapStyle,
            center: isSuperAdmin ? US_CENTER_COORDINATES : center,
            zoom: isSuperAdmin ? SUPER_ADMIN_ZOOM_LEVEL : DEFAULT_ZOOM_LEVEL,
            preserveDrawingBuffer: true
        });

        newMap.loadImage('/dow_marker.png', (error, image) => {
            if (error) throw error;
            if (image) {
                newMap.addImage('gas-icon', image, { sdf: true });
            }
        });

        newMap.loadImage('/luow_marker.png', (error, image) => {
            if (error) throw error;
            if (image) {
                newMap.addImage('oil-icon', image, { sdf: true });
            }
        });

        // newMap.loadImage('/arrows_to_dot.png', (error, image) => {
        //     if (error) throw error;
        //     if (image) {
        //         newMap.addImage('both-icon', image, { sdf: true });
        //     }
        // });

        newMap.scrollZoom.disable();
        newMap.addControl(new mapboxgl.NavigationControl(), 'top-left');

        mapStore.setMap(mapId, newMap);

        return newMap;
    };

    const addLoadListener = (mapId: string, callback: () => void): void => {
        const map = mapStore.getMap(mapId);
        if (map) {
            map.on('load', callback);
        }
    };

    const removeLoadListener = (mapId: string, callback: () => void): void => {
        const map = mapStore.getMap(mapId);
        if (map) {
            map.off('load', callback);
        }
    };

    const createCountyLayer = (mapId: string): void => {
        const map = mapStore.getMap(mapId);
        if (!map) return;

        map.addSource('counties', {
            type: 'geojson',
            data: '/counties/counties.geojson'
        });

        map.addLayer({
            id: 'counties-fill',
            type: 'fill',
            source: 'counties',
            layout: {},
            paint: {
                'fill-color': '#88C0D0',
                'fill-opacity': 0.3
            }
        });

        map.addLayer({
            id: 'counties-outline',
            type: 'line',
            source: 'counties',
            layout: {},
            paint: {
                'line-color': '#0E86D4',
                'line-width': 1
            }
        });
    };

    const createOrUpdateMapPointsFromDataset = (mapId: string, data: Array<DatasetJsonLocation>): void => {
        const project: Project = {
            id: 1,
            wells: data.map(function (parsedDataset: DatasetJsonLocation, index: number) {
                return {
                    wellId: parsedDataset.wellId.value,
                    wellName: parsedDataset.wellName.value,
                    wellType: parsedDataset.wellType.value,
                    latitude: parsedDataset.latitude.value,
                    longitude: parsedDataset.longitude.value,
                    operatorName: parsedDataset.operatorName.value
                };
            })
        };

        createOrUpdateMapPoints(mapId, { Project: project });
    };

    const createOrUpdateMapPoints = (
        mapId: string,
        data: { Projects?: ScenarioProject[]; Project?: Project }
    ): void => {
        const map = mapStore.getMap(mapId);
        if (!map) return;

        const projects = data.Projects || (data.Project ? [data.Project] : []);
        if (!projects.length) return;

        projects.forEach((project) => {
            const projectName = `projectLayer-${project.id}`;
            const sourceId = projectName; // Use project name as the source ID
            const layerId = projectName; // Use project name as the layer ID

            if (map.getLayer(layerId)) {
                toggleProjectLayerVisibility(mapId, project.id);
                return;
            }

            const geojsonData: GeoJSON.FeatureCollection<GeoJSON.Point> = {
                type: 'FeatureCollection',
                features: project.wells.map((well: Well) => ({
                    type: 'Feature',
                    geometry: {
                        type: 'Point',
                        coordinates: [well.longitude, well.latitude]
                    },
                    properties: {
                        description:
                            'scenarioId' in project
                                ? `<span><strong>Scenario ID: </strong>${project.scenarioId}</span><br><span><strong>Well ID: </strong>${well.wellId}</span><br><span><strong>Well Name: </strong>${well.wellName ?? '--'}</span><br>
                          <span><strong>Operator Name: </strong>${well.operatorName ?? '--'}</span>`
                                : `<span><strong>Well ID: </strong>${well.wellId ?? '--'}</span><br><span><strong>Well Name: </strong>${well.wellName ?? '--'}</span><br>
                          <span><strong>Operator Name: </strong>${well.operatorName ?? '--'}</span>`,
                        icon: wellIconLookup[well.wellType as keyof typeof wellIconLookup]
                    }
                }))
            };

            if (!map.getSource(sourceId)) {
                map.addSource(sourceId, {
                    type: 'geojson',
                    data: geojsonData
                });
            }

            const projectLayers = map.getStyle()?.layers.filter((layer) => layer.id.startsWith('project'));

            const layerType = 'symbol';
            // const layerLayout = project.type === 'Gas' ? LAYER_LAYOUT.GAS : LAYER_LAYOUT.OTHER;

            if (!map.getLayer(layerId)) {
                const colorIndex = projectLayers ? projectLayers?.length % wellColors.length : 0; // Cycle through the list of colors
                const wellColor = wellColors[colorIndex];
                map.addLayer({
                    id: layerId,
                    type: layerType,
                    source: sourceId,
                    layout: LAYER_LAYOUT.OTHER,
                    paint: {
                        'icon-color': wellColor
                    }
                });
            }

            const popup = new mapboxgl.Popup({
                closeButton: false,
                closeOnClick: false
            });

            map.on('mouseenter', layerId, (e) => {
                // Change the cursor style as a UI indicator.
                if (map) {
                    map.getCanvas().style.cursor = 'pointer';
                }

                // Copy coordinates array.
                const coordinates = (e as any).features[0].geometry.coordinates.slice();
                const description = (e as any).features[0].properties.description;

                // Ensure that if the map is zoomed out such that multiple
                // copies of the feature are visible, the popup appears
                // over the copy being pointed to.
                while (Math.abs(e.lngLat.lng - coordinates[0]) > 180) {
                    coordinates[0] += e.lngLat.lng > coordinates[0] ? 360 : -360;
                }

                // Populate the popup and set its coordinates
                // based on the feature found.
                if (map) {
                    popup.setLngLat(coordinates).setHTML(description).addTo(map);
                }
            });

            map.on('mouseleave', layerId, () => {
                if (map) {
                    map.getCanvas().style.cursor = '';
                }
                popup.remove();
            });

            if (data.Projects) {
                const coordinates = geojsonData.features.map(
                    (feature) => feature.geometry.coordinates as [number, number]
                );
                const bounds = coordinates.reduce(
                    (bounds, coord) => bounds.extend(coord),
                    new mapboxgl.LngLatBounds(coordinates[0], coordinates[0])
                );

                map.fitBounds(bounds, { padding: 20, maxZoom: 9 });
            }
        });

        if (updateTimeout) {
            clearTimeout(updateTimeout);
        }

        updateTimeout = setTimeout(() => {
            checkForDuplicates(mapId);
        }, 500);
    };

    const updateScenarioBasedColors = (mapId: string, scenarioIds: number[], projects: ScenarioProject[]): void => {
        const map = mapStore.getMap(mapId);
        if (!map) return;

        const colors = ['#4F46E5', '#008080'];

        const multipleScenarios = scenarioIds.length > 1;

        scenarioIds.forEach((scenarioId, scenarioIndex) => {
            const scenarioColor = colors[scenarioIndex % colors.length];

            projects
                .filter((p) => p.scenarioId === scenarioId)
                .forEach((project: ScenarioProject, projectIndex: number) => {
                    const projectColor = multipleScenarios
                        ? scenarioColor
                        : wellColors[projectIndex % wellColors.length];
                    const layerId = `projectLayer-${project.id}`;

                    if (map.getLayer(layerId)) {
                        map.setPaintProperty(layerId, 'icon-color', projectColor);
                    }
                });
        });
    };

    const toggleProjectLayerVisibility = (mapId: string, projectId: number): void => {
        const map = mapStore.getMap(mapId);
        if (!map) return;

        const layerId = `projectLayer-${projectId}`;
        if (map.getLayer(layerId)) {
            const visibility = map.getLayoutProperty(layerId, 'visibility');
            map.setLayoutProperty(layerId, 'visibility', visibility === 'visible' ? 'none' : 'visible');
        }

        if (updateTimeout) {
            clearTimeout(updateTimeout);
        }

        updateTimeout = setTimeout(() => {
            checkForDuplicates(mapId);
        }, 500);
    };

    const checkForDuplicates = (mapId: string) => {
        const map = mapStore.getMap(mapId);
        if (!map) return;

        const layers = map.getStyle()?.layers;
        if (!layers) return;

        const projectLayers = layers.filter(
            (layer) =>
                layer.id.startsWith('projectLayer-') && map.getLayoutProperty(layer.id, 'visibility') === 'visible'
        );

        const coordinateMap = new Map<string, Set<string>>();

        const normalizeCoordinate = (coord: [number, number], precision = 6): string =>
            coord.map((c) => c.toFixed(precision)).join(',');

        // Collect coordinates from all project layers
        projectLayers.forEach((layer) => {
            const features = map.querySourceFeatures(layer.source || '', {
                sourceLayer: layer['source-layer']
            });

            features.forEach((feature) => {
                if (feature.geometry.type === 'Point') {
                    const coord = normalizeCoordinate([
                        feature.geometry.coordinates[0],
                        feature.geometry.coordinates[1]
                    ]);
                    const layersSet = coordinateMap.get(coord) || new Set<string>();
                    layersSet.add(layer.id);
                    coordinateMap.set(coord, layersSet);
                }
            });
        });

        // Find duplicated coordinates that appear in multiple layers
        const duplicatedCoordinates = Array.from(coordinateMap.entries())
            .filter(([_, layersSet]) => layersSet.size > 1) // Appears in more than one layer
            .map(([coord]) => coord.split(',').map(Number) as [number, number]);

        // Remove existing layer and source if they exist
        if (map.getLayer('duplicated-points')) {
            map.removeLayer('duplicated-points');
        }
        if (map.getSource('duplicated-points')) {
            map.removeSource('duplicated-points');
        }

        if (duplicatedCoordinates.length > 0) {
            const geojsonData: GeoJSON.FeatureCollection<GeoJSON.Point> = {
                type: 'FeatureCollection',
                features: duplicatedCoordinates.map((coord) => ({
                    type: 'Feature',
                    geometry: {
                        type: 'Point',
                        coordinates: coord
                    },
                    properties: {}
                }))
            };

            // Create a new layer with duplicated points
            map.addSource('duplicated-points', {
                type: 'geojson',
                data: geojsonData
            });

            map.addLayer({
                id: 'duplicated-points',
                type: 'circle',
                source: 'duplicated-points',
                paint: {
                    'circle-radius': 9,
                    'circle-color': 'transparent', // No fill
                    'circle-stroke-color': '#f57e42',
                    'circle-stroke-width': 2
                }
            });
        }
    };

    const easeToCoordinates = (mapId: string, well: Well): void => {
        const map = mapStore.getMap(mapId);
        if (!map) return;

        map.easeTo({
            center: [well.longitude, well.latitude],
            zoom: 10,
            duration: 1000
        });

        // Create a new popup
        const popup = new mapboxgl.Popup({
            closeButton: true,
            closeOnClick: false
        });

        const description = `
            <p style="margin: 2px 0;"><strong>Well ID:</strong> ${well.wellId}</p>
            <p style="margin: 2px 0;"><strong>Well Name:</strong> ${well.wellName}</p>
            <p style="margin: 2px 0;"><strong>Operator Name:</strong> ${well.operatorName}</p>
        `;

        popup.setLngLat([well.longitude, well.latitude]).setHTML(description).addTo(map);

        map.getCanvas().style.cursor = 'pointer';

        popup.on('close', () => {
            map.getCanvas().style.cursor = '';
        });
    };

    const setMapCenterToCoordinates = (mapId: string, latitude: number, longitude: number): void => {
        const map = mapStore.getMap(mapId);
        if (!map) return;
        map.easeTo({
            center: [longitude, latitude],
            zoom: 6,
            duration: 1000
        });
    };

    const resize = (mapId: string): void => {
        const map = mapStore.getMap(mapId);
        if (map) {
            map.resize();
        }
    };

    return {
        initializeMap,
        addLoadListener,
        removeLoadListener,
        createCountyLayer,
        createOrUpdateMapPoints,
        createOrUpdateMapPointsFromDataset,
        toggleProjectLayerVisibility,
        easeToCoordinates,
        updateScenarioBasedColors,
        setMapCenterToCoordinates,
        resize
    };
}
