<script setup lang="ts">
    import { computed } from 'vue';

    import { ScenarioFormTitle } from '@/constants/scenarioEnums';

    import EfficiencyFactorInput from '../../components/scenario/EfficiencyFactorInput.vue';
    import CreateScenarioSubHeading from '@/components/scenario/CreateScenarioSubHeading.vue';

    import { useScenarioFormStore } from '../../stores/form/scenarioForm';
    import { efficiencyFactorsLabels, efficiencyFactorsSubHeading } from '@/constants/scenarioForm';
    import type { ScenarioForm } from '@/types/scenarioForm/scenarioForm';

    const scenarioFormStore = useScenarioFormStore();
    const { form } = scenarioFormStore;

    const total = computed((): number => {
        let sum = 0;
        for (const key in form.efficiencyFactors) {
            if (form.efficiencyFactors[key].selected) {
                sum += form.efficiencyFactors[key].value;
            }
        }

        return sum;
    });

    const progressClass = computed(() => {
        return total.value < 50 ? 'bg-red-500' : total.value < 100 ? 'bg-yellow-500' : 'bg-green-500';
    });

    const factorDisabled = computed(() => (field: string | number) => {
        // Temporary Phase 2 instruction from the Python API
        if (field === 'numUniqueOwners' || field === 'avgAge' || field === 'avgDepth') return true;
        const isSelected = form.efficiencyFactors[field].selected;
        const currentValue = form.efficiencyFactors[field].value;

        return (total.value >= 100 && currentValue === 0) || (!isSelected && total.value >= 100 && currentValue > 0);
    });

    const exclusiveTotal = (field: keyof ScenarioForm['efficiencyFactors']) => {
        let sum = 0;
        for (const key in form.efficiencyFactors) {
            if (key !== field) {
                if (form.efficiencyFactors[key].selected) {
                    sum += form.efficiencyFactors[key].value;
                }
            }
        }

        return 100 - sum;
    };

    const onInput = (event: any, field: any) => {
        const inputElement = event.target as HTMLInputElement;
        let newValue = parseInt(inputElement.value, 10) || 0;

        const excess = newValue - exclusiveTotal(field);

        if (excess > 0) {
            form.efficiencyFactors[field].value = newValue - excess;
        } else {
            form.efficiencyFactors[field].value = newValue;
        }
    };

    const sendEmail = () => {
        const recipient = import.meta.env.VITE_EMAIL_RECIPIENT;

        const mailtoLink = `mailto:${recipient}`;

        window.location.href = mailtoLink;
    };
</script>

<template>
    <div class="flex-auto">
        <CreateScenarioSubHeading :text="efficiencyFactorsSubHeading" />

        <PCard class="mb-4">
            <template #content>
                <ProgressBar
                    :value="total"
                    :display-value="`${total}%`"
                    :style="{ height: '1.5rem' }"
                    class="w-full"
                    :pt="{ value: { class: `text-green ${progressClass}` } }"
                />
            </template>
        </PCard>

        <PCard
            class="mb-4 shadow-md shadow-slate-300"
            :pt="{
                root: {
                    class: `input-card ${factorDisabled(label.field) ? 'bg-gray-200' : ''}`
                },
                body: { class: 'p-3' }
            }"
            v-for="(label, index) in efficiencyFactorsLabels"
            :key="index"
        >
            <template #content>
                <EfficiencyFactorInput
                    :label="label"
                    :disabled="
                        factorDisabled(label.field) ||
                        !scenarioFormStore.availableEfficiencyFactors?.[label.field].selected
                    "
                    :remainingTotal="exclusiveTotal(label.field)"
                >
                    <InputNumber
                        inputId="integeronly"
                        class="percentage-input-number"
                        v-model="form.efficiencyFactors[label.field].value"
                        size="small"
                        @input="(event) => onInput(event.originalEvent, label.field.toString())"
                        :disabled="
                            factorDisabled(label.field) ||
                            !form.efficiencyFactors[label.field].selected ||
                            !scenarioFormStore.availableEfficiencyFactors?.[label.field].selected
                        "
                    />
                </EfficiencyFactorInput>
            </template>
        </PCard>
        <ul class="requirements list-disc ml-8">
            <li
                key="parents-100"
                :class="
                    scenarioFormStore.sumsTo100(ScenarioFormTitle.EfficiencyFactors)
                        ? 'text-green-500'
                        : 'text-gray-400'
                "
            >
                Factors must add to 100%
            </li>
        </ul>
        <div class="flex flex-col items-start">
            <span>Require additional efficiency factors? Email us to suggest a new field.</span>
            <PButton class="btn-secondary mt-4 bg-secondary-500 py-2 px-6" @click="sendEmail">
                <span class="font-bold">Contact Us</span>
            </PButton>
        </div>
    </div>
</template>
