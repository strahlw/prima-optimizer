<!-- 
 1. Create a new file for the new icon, copy paste the IconDownloading (or any other icon extending ReusableIcon into that new file.
 2. Overwrite the d=“”, to be d="THE 'd' from the raw SVG you downloaded" in the template. Do the same with viewbox
 3. Now you can use that icon in your Vue files, you can pass in the props of size (sm|md|lg|xl…….6xl) AND the prop fillClass for example fill-primary to color the icon -->
<script setup lang="ts">
    import { computed } from 'vue';

    const props = defineProps({
        size: {
            type: String,
            default: 'md'
        },
        fillClass: {
            type: String,
            default: 'fill-black'
        },
        viewBox: {
            type: String,
            default: '0 -960 960 960'
        },
        d: {
            type: Array as () => string[],
            default: null
        }
    });

    type SizeKeys = 'sm' | 'md' | 'lg' | 'xl' | '2xl' | '3xl' | '4xl' | '5xl' | '6xl' | '7xl' | '8xl';

    const sizeClasses: Record<SizeKeys, string> = {
        sm: 'w-4 h-4',
        md: 'w-6 h-6',
        lg: 'w-8 h-8',
        xl: 'w-10 h-10',
        '2xl': 'w-12 h-12',
        '3xl': 'w-14 h-14',
        '4xl': 'w-16 h-16',
        '5xl': 'w-20 h-20',
        '6xl': 'w-24 h-24',
        '7xl': 'w-28 h-28',
        '8xl': 'w-32 h-32'
    };

    const computedSizeClass = computed(() => {
        return `${sizeClasses[props.size as SizeKeys] || props.size}`;
    });
</script>

<template>
    <svg :class="computedSizeClass" xmlns="http://www.w3.org/2000/svg" :viewBox="viewBox">
        <slot></slot>
        <path v-for="(data, i) in d" :class="props.fillClass" :d="data" :key="i" />
    </svg>
</template>
