<script setup lang="ts">
    import { watch, ref, computed } from 'vue';
    import type { Factor } from '@/types/factor';
    import type { EfficiencyFactorInputProps } from '@/types/scenarioForm/efficiencyFactor';
    import CheckboxInput from '@/components/forms/CheckboxInput.vue';
    import { useScenarioFormStore } from '@/stores/form/scenarioForm';

    const scenarioFormStore = useScenarioFormStore();
    const { form } = scenarioFormStore;
    const props = defineProps<EfficiencyFactorInputProps>();
    const factor = ref(form.efficiencyFactors[props.label.field as keyof typeof form.efficiencyFactors]);

    watch(factor.value, (newValue: Factor) => {
        if (newValue.selected === false) {
            factor.value.value = 0;
        }

        if (newValue.selected && newValue.value !== 0) {
            handleValueUpdate(newValue.value);
        }
    });

    const sliderDisabled = computed(() => {
        return !factor.value.selected;
    });

    const handleValueUpdate = (newValue: number) => {
        const excess = newValue - props.remainingTotal;

        if (excess > 0) {
            factor.value.value = newValue - excess;
        } else {
            factor.value.value = newValue;
        }
    };

    const onInput = (event: any) => {
        const newValue = parseInt(event.target.value, 10);

        handleValueUpdate(newValue);
    };
</script>

<template>
    <div class="grid grid-cols-2">
        <div class="flex flex-row items-center">
            <CheckboxInput
                :label="label.name"
                labelClass="ml-2 text-sm"
                className="accent-primary"
                v-model="factor.selected"
                :disabled="disabled"
            />
            <LabelTooltip
                containerClass="ml-2 text-sm flex flex-row items-center"
                :labelFor="label.field"
                :tooltip="factor.toolTip"
            />
        </div>

        <div class="flex ml-auto items-center mr-6">
            <div class="text-sm" :class="sliderDisabled || disabled ? 'text-gray-400' : ''">Importance:</div>
            <div class="w-56 grid grid-cols-2 items-center">
                <input
                    class="cursor-pointer accent-primary mx-4 w-full"
                    type="range"
                    v-model.number="factor.value"
                    min="0"
                    :max="100"
                    :disabled="sliderDisabled || disabled"
                    @input="onInput"
                    step="1"
                />
                <slot></slot>
            </div>
        </div>
    </div>
</template>
