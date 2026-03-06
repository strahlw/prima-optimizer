<script setup lang="ts">
    import { computed } from 'vue';

    interface Props {
        avg: number;
        min: number;
        max: number;
        gradientStart?: string;
        gradientMiddle?: string;
        gradientEnd?: string;
    }

    const defaultGradientStart = '#3b82f6';
    const defaultGradientMiddle = '#6366f1';
    const defaultGradientEnd = '#8b5cf6';

    const props = withDefaults(defineProps<Props>(), {
        gradientStart: defaultGradientStart,
        gradientMiddle: defaultGradientMiddle,
        gradientEnd: defaultGradientEnd,
        avg: 50,
        min: 0,
        max: 100
    });

    const radius = 80;
    const strokeWidth = 18;
    const centerX = 100;
    const centerY = 100;

    // Clamp average value between min and max
    const clampedValue = computed(() => Math.max(props.min!, Math.min(props.max!, props.avg!)));

    // Helper function to convert percentage to angle (0% = 180°, 100% = 0°)
    const percentToAngle = (percent: number) => {
        return 180 - (percent / 100) * 180; // This maps 0% to 180° (left) and 100% to 0° (right)
    };

    // Helper function to get coordinates for a given percentage
    const getCoordinates = (percent: number, radiusOffset = 0) => {
        const angle = percentToAngle(percent);
        const r = radius + radiusOffset;
        const x = centerX + r * Math.cos((angle * Math.PI) / 180);
        const y = centerY - r * Math.sin((angle * Math.PI) / 180); // Negative because SVG Y axis is flipped
        return { x, y, angle };
    };

    // Background path (full half circle)
    const backgroundPath = computed(() => {
        const startX = centerX - radius;
        const startY = centerY;
        const endX = centerX + radius;
        const endY = centerY;
        return `M ${startX} ${startY} A ${radius} ${radius} 0 0 1 ${endX} ${endY}`;
    });

    const needlePoints = computed<string>(() => {
        const needleLength = 50;
        const needleWidth = 8;
        const tipX = 100;
        const tipY = 100 - needleLength;
        const baseY = 100 - 15;

        return `${tipX},${tipY} ${tipX - needleWidth / 2},${baseY} ${tipX + needleWidth / 2},${baseY}`;
    });

    const needleTransform = computed<string>(() => {
        const angle = -90 + (clampedValue.value / 100) * 180;
        return `rotate(${angle} 100 100)`;
    });
</script>

<template>
    <div class="flex flex-col items-center p-4">
        <div class="relative">
            <svg width="200" height="120" viewBox="0 0 200 120" class="overflow-visible">
                <!-- Define gradients -->
                <defs>
                    <!-- Main arc gradient -->
                    <linearGradient id="arcGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                        <stop offset="0%" :style="`stop-color:${gradientStart};stop-opacity:1`" />
                        <stop offset="50%" :style="`stop-color:${gradientMiddle};stop-opacity:1`" />
                        <stop offset="100%" :style="`stop-color:${gradientEnd};stop-opacity:1`" />
                    </linearGradient>

                    <!-- Shadow -->
                    <filter id="shadow" x="-50%" y="-50%" width="200%" height="200%">
                        <feDropShadow dx="2" dy="2" stdDeviation="3" flood-opacity="0.3" />
                    </filter>
                </defs>

                <!-- Background arc (gray) -->
                <path :d="backgroundPath" fill="none" stroke="#e5e7eb" :stroke-width="strokeWidth - 2" />

                <!-- Colored arc (only the range from min to max) -->

                <!-- Needle -->
                <g
                    class="transition-transform duration-700 ease-out"
                    :transform="needleTransform"
                    v-tooltip="{
                        value: `Average ${clampedValue}%`,
                        pt: {
                            root: '!bg-black !bg-opacity-0',
                            text: '!text-white !bg-black !bg-opacity-80 font-semibold'
                        }
                    }"
                >
                    <!-- Main needle -->
                    <polygon
                        :points="needlePoints"
                        fill="black"
                        stroke="#000000"
                        stroke-width="1"
                        filter="url(#shadow)"
                    />
                    <!-- Needle center hub -->
                    <circle cx="100" cy="100" r="8" fill="black" stroke="#000000" stroke-width="2" />
                    <!-- Inner hub highlight -->
                    <circle cx="100" cy="100" r="4" fill="black" />
                </g>

                <!-- Tick marks -->
                <g stroke="#444444" stroke-width="2" opacity="1">
                    <!-- 0% tick (left) -->
                    <line x1="12" y1="100" x2="35" y2="100" class="stroke-[#c7c8c9]" v-if="min != 0" />

                    <!-- Min value tick -->
                    <line
                        :x1="getCoordinates(min, -10).x"
                        :y1="getCoordinates(min, -10).y"
                        :x2="getCoordinates(min, 10).x"
                        :y2="getCoordinates(min, 10).y"
                        class="stroke-[#3D82F6]"
                    />

                    <!-- Avg value tick -->
                    <line
                        :x1="getCoordinates(clampedValue, -10).x"
                        :y1="getCoordinates(clampedValue, -10).y"
                        :x2="getCoordinates(clampedValue, 10).x"
                        :y2="getCoordinates(clampedValue, 10).y"
                    />

                    <!-- Max value tick -->
                    <line
                        :x1="getCoordinates(max, -10).x"
                        :y1="getCoordinates(max, -10).y"
                        :x2="getCoordinates(max, 10).x"
                        :y2="getCoordinates(max, 10).y"
                        class="stroke-[#3D82F6]"
                    />

                    <!-- 100% tick (right) -->
                    <line x1="188" y1="100" x2="165" y2="100" class="stroke-[#c7c8c9]" v-if="max != 100" />
                </g>

                <!-- Labels -->
                <g
                    fill="#6b7280"
                    font-family="system-ui, sans-serif"
                    font-size="12"
                    font-weight="500"
                    text-anchor="middle"
                >
                    <!-- 0 label (bottom left) -->
                    <text x="2" y="106" text-anchor="start" fill="#c7c8c9" v-if="min != 0">0</text>

                    <!-- Min label -->
                    <text :x="getCoordinates(min, 20).x" :y="getCoordinates(min, 20).y + 4" fill="#3D82F6">
                        {{ min }}
                    </text>

                    <!-- Avg label (positioned inside the arc) -->
                    <text
                        :x="getCoordinates(clampedValue, -25).x"
                        :y="getCoordinates(clampedValue, -25).y"
                        font-size="16px"
                        fill="#39475A"
                    >
                        {{ clampedValue }}
                    </text>

                    <!-- Max label -->
                    <text :x="getCoordinates(max, 20).x" :y="getCoordinates(max, 20).y + 4" fill="#3D82F6">
                        {{ max }}
                    </text>

                    <!-- 100 label (bottom right) -->
                    <text x="210" y="106" text-anchor="end" fill="#c7c8c9" v-if="max != 100">100</text>
                </g>
            </svg>
        </div>

        <div class="mt-2">Average: {{ clampedValue }}</div>
    </div>
</template>
