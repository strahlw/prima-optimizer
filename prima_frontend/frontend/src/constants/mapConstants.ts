export const LAYER_PAINT = {
    GAS: {
        'circle-color': '#dc2626', // Tailwind red 600
        'circle-stroke-width': 3,
        'circle-opacity': 0,
        'circle-stroke-color': '#dc2626', // Tailwind red 600
        'circle-radius': 10
    },
    OTHER: {
        'text-color': '#2563eb' // Tailwind blue 600
    }
};

// export const LAYER_LAYOUT = {
//   GAS: {
//     visibility: 'visible'
//   } as mapboxgl.CircleLayout,
//   OTHER: {
//     visibility: 'visible',
//     'text-field': 'X',
//     'text-size': 35,
//     'text-transform': 'lowercase',
//     'text-font': ['Open Sans Regular', 'Arial Unicode MS Regular'],
//     'text-ignore-placement': true // Ignore placement rules
//   } as mapboxgl.SymbolLayout
// };

export const LAYER_LAYOUT = {
    GAS: {
        visibility: 'visible',
        'icon-image': ['get', 'icon'],
        'icon-size': 0.6,
        'icon-allow-overlap': true
    } as mapboxgl.SymbolLayout,
    OTHER: {
        visibility: 'visible',
        'icon-image': ['get', 'icon'],
        'icon-size': 0.6,
        'icon-allow-overlap': true,
        'text-size': 35,
        'text-transform': 'lowercase',
        'text-font': ['Open Sans Regular', 'Arial Unicode MS Regular'],
        'text-ignore-placement': true // Ignore placement rules
    } as mapboxgl.SymbolLayout
};
