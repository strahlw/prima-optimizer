<script setup lang="ts">
    import { computed } from 'vue';

    const props = defineProps({
        label: { type: String, required: false, default: '' },
        labelFor: { type: String, required: false }, // Omit if the label isn't directly for an input element
        tooltip: { type: String, required: true },
        icon: { type: String, required: false },
        containerClass: { type: String, required: false },
        labelClass: { type: String, required: false }
    });

    const computedIconClass = computed(() => {
        const iconValue = props.icon ? props.icon : 'pi-info-circle';
        return `pi ml-2 text-sm ml-2 text-gray-400 cursor-help ${iconValue}`;
    });
</script>

<template>
    <div :class="containerClass">
        <label :for="labelFor" :class="labelClass" v-if="labelFor">{{ label }}</label>
        <span v-else :class="labelClass">{{ label }}</span>
        <i :class="computedIconClass" v-tooltip="tooltip"></i>
    </div>
</template>

<style>
    .p-tooltip .p-tooltip-text {
        color: black;
        font-size: 12px;
        background-color: rgb(186, 192, 202);
    }
</style>
