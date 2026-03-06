<script setup lang="ts">
    import { watch, ref, computed } from 'vue';
    import type { Factor } from '@/types/factor';
    import type { ImpactFactorInputProps } from '@/types/scenarioForm/impactFactor';
    import CheckboxInput from '../../components/forms/CheckboxInput.vue';
    import { useScenarioFormStore } from '../../stores/form/scenarioForm';

    const scenarioFormStore = useScenarioFormStore();
    const { form } = scenarioFormStore;

    const props = defineProps<ImpactFactorInputProps>();
    const factor = ref(props.parentFactor || form.impactFactors[props.label.field as keyof typeof form.impactFactors]);

    watch(factor.value, (newValue: Factor) => {
        if (newValue.selected === false) {
            factor.value.value = 0;
        }

        if (newValue.selected && newValue.value !== 0) {
            handleValueUpdate(newValue.value);
        }
    });

    const sliderDisabled = computed(() => {
        return !factor.value.selected || props.parentDisabled;
    });

    watch(
        () => props.parentDisabled,
        () => {
            if (props.parentDisabled) {
                factor.value.selected = false;
            } else {
                factor.value.selected = true;
            }
        }
    );

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
        <div class="flex flex-row items-center" :class="parentFactor ? 'pl-20' : ''">
            <CheckboxInput
                :label="label.name"
                :inputId="`${label.field}-check`"
                labelClass="ml-2 text-sm"
                className="accent-primary"
                v-model="factor.selected"
                :disabled="props.parentFactor ? props.parentDisabled && disabled : disabled"
            />
            <LabelTooltip
                containerClass="ml-2 text-sm flex flex-row items-center"
                :labelFor="label.field"
                :tooltip="factor.toolTip"
            />
        </div>

        <div class="flex ml-auto items-center" :class="parentFactor ? '' : 'mr-6'">
            <div class="text-sm" :class="sliderDisabled || disabled ? 'text-gray-400' : ''">Importance:</div>
            <div class="w-56 grid grid-cols-2 items-center">
                <input
                    :id="label.field as string"
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
            <div class="ml-2" v-if="parentFactor">%</div>
        </div>
    </div>
</template>
