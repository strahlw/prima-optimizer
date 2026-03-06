<script setup lang="ts">
    import { watch, ref } from 'vue';
    import { type ErrorObject } from '@vuelidate/core';

    const categorizedErrors = ref<ErrorObject[]>();
    const generalErrors = ref<ErrorObject[]>();

    const props = defineProps({
        maxValue: {
            type: Number,
            default: null as number | null
        },
        minValue: {
            type: Number,
            default: null as number | null
        },
        errors: {
            type: Array as () => ErrorObject[],
            default: () => []
        }
    });

    const commonValidators = ['required', 'numeric'];

    watch(
        () => props.errors,
        (newErrors: ErrorObject[]) => {
            categorizedErrors.value = newErrors.filter((error) => commonValidators.includes(error.$validator)) ?? [];
            generalErrors.value = newErrors.filter((error) => !commonValidators.includes(error.$validator));
        },
        { immediate: true }
    );
</script>

<template>
    <div v-if="props.errors.length > 0" class="mt-2 text-sm">
        <span class="text-red-500" v-if="categorizedErrors?.some((e) => e.$validator === 'required')"
            >This field is required</span
        >
        <span class="text-red-500" v-else-if="categorizedErrors?.some((e) => e.$validator === 'maxValue')">
            Value must be less than
            {{
                'max' in categorizedErrors[0].$params
                    ? Intl.NumberFormat().format((categorizedErrors[0].$params.max as number) + 1)
                    : ''
            }}
        </span>
        <span class="text-red-500" v-else-if="categorizedErrors?.some((e) => e.$validator === 'minValue')">
            Value must be greater than
            {{
                'min' in categorizedErrors[0].$params
                    ? Intl.NumberFormat().format((categorizedErrors[0].$params.min as number) - 1)
                    : ''
            }}
        </span>
        <span v-else-if="categorizedErrors?.some((e) => e.$validator === 'numeric')">This field must be numeric</span>

        <div v-for="error in generalErrors" :key="error.$validator" class="text-red-500">
            <span class="text-red-500">{{ error.$message }}</span>
        </div>
    </div>
</template>
