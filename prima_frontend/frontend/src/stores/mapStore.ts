import { defineStore } from 'pinia';
import mapboxgl from 'mapbox-gl';

export const useMapStore = defineStore('mapStore', {
    state: () => ({
        maps: {} as Record<string, mapboxgl.Map>
    }),
    getters: {
        getMaps(): Record<string, mapboxgl.Map> {
            return this.maps;
        }
    },
    actions: {
        setMap(mapId: string, map: mapboxgl.Map) {
            this.maps[mapId] = map;
        },
        getMap(mapId: string): mapboxgl.Map | null {
            return this.maps[mapId] || null;
        },
        removeMap(mapId: string) {
            const map = this.getMap(mapId);
            if (map) {
                map.remove(); // Clean up the map instance
                delete this.maps[mapId]; // Remove the map from the store
            }
        }
    }
});
