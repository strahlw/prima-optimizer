<script setup lang="ts">
    defineProps({
        label: {
            type: String,
            default: '',
            required: true
        },
        className: {
            type: String,
            default: ''
        },
        labelClass: {
            type: String,
            default: ''
        },
        modelValue: {
            type: Boolean,
            default: true
        },
        disabled: {
            type: Boolean,
            default: false
        }
    });

    const emit = defineEmits(['update:modelValue']);

    const updateValue = (event: Event) => {
        const input = event.target as HTMLInputElement;
        emit('update:modelValue', input.checked);
    };
</script>

<template>
    <div class="flex flex-row items-center">
        <input
            type="checkbox"
            :class="className"
            :inputId="label"
            :checked="modelValue"
            @change="updateValue"
            :disabled="disabled"
        />
        <label :for="label" :class="labelClass">{{ label }}</label>
    </div>
</template>

<style scoped>
    input {
        width: 1rem;
        height: 1rem;
        color: rgb(51, 65, 85);
        border-radius: 4px;
    }
</style>
