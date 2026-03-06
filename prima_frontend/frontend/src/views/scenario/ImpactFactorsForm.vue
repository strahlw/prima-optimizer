<script setup lang="ts">
    import { computed } from 'vue';
    import { ScenarioFormTitle } from '@/constants/scenarioEnums';

    import ImpactFactorInput from '../../components/scenario/ImpactFactorInput.vue';
    import CreateScenarioSubHeading from '../../components/scenario/CreateScenarioSubHeading.vue';
    import Divider from 'primevue/divider';

    import { useScenarioFormStore } from '../../stores/form/scenarioForm';
    import { orderedImpactFactorsLabels, impactFactorsSubHeading } from '@/constants/scenarioForm';
    import type {
        LossesFactor,
        SensitiveReceptorsFactor,
        EnvironmentFactor,
        AnnProductionVolumeFactor,
        FiveYearProductionVolumeFactor,
        LifelongProductionVolumeFactor,
        SiteConsiderationsFactor,
        EcologicalReceptorsFactor,
        OtherLossesFactor
    } from '@/types/scenarioForm/impactFactor';
    import type { ScenarioForm } from '@/types/scenarioForm/scenarioForm';

    const scenarioFormStore = useScenarioFormStore();
    const { form } = scenarioFormStore;

    const total = computed((): number => {
        let sum = 0;
        for (const key in form.impactFactors) {
            if (form.impactFactors[key].selected) {
                sum += form.impactFactors[key].value;
            }
        }

        return sum;
    });

    const progressClass = computed(() => {
        return total.value < 50 ? 'bg-red-500' : total.value < 100 ? 'bg-yellow-500' : 'bg-green-500';
    });
    const factorDisabled = computed(() => (field: string | number) => {
        const isSelected = form.impactFactors[field].selected;
        const currentValue = form.impactFactors[field].value;

        return (total.value >= 100 && currentValue === 0) || (!isSelected && total.value >= 100 && currentValue > 0);
    });

    const childFactorDisabled = (parentField: string | number, childField: string | number) => {
        if (
            parentField === 'losses' ||
            parentField === 'sensitiveReceptors' ||
            parentField === 'environment' ||
            parentField === 'annProductionVolume' ||
            parentField === 'fiveYearProductionVolume' ||
            parentField === 'lifelongProductionVolume' ||
            parentField === 'siteConsiderations' ||
            parentField === 'ecologicalReceptors' ||
            parentField === 'otherLosses'
        ) {
            return (
                factorDisabled.value(parentField) ||
                (form.impactFactors[parentField].childFactors &&
                    !form.impactFactors[parentField].childFactors[childField].selected) ||
                (!childExclusiveTotal(parentField, childField) &&
                    !(form.impactFactors[parentField].childFactors[childField].value > 0))
            );
        }
    };

    const onInput = (event: any, field: any) => {
        const inputElement = event.target as HTMLInputElement;
        let newValue = parseInt(inputElement.value, 10) || 0;
        const excess = newValue - exclusiveTotal(field);

        if (excess > 0) {
            form.impactFactors[field].value = newValue - excess;
        } else {
            form.impactFactors[field].value = newValue;
        }
    };

    const onChildInput = (
        event: any,
        parentField: keyof ScenarioForm['impactFactors'],
        field:
            | keyof LossesFactor['childFactors']
            | keyof SensitiveReceptorsFactor['childFactors']
            | keyof EnvironmentFactor['childFactors']
            | keyof AnnProductionVolumeFactor['childFactors']
            | keyof FiveYearProductionVolumeFactor['childFactors']
            | keyof LifelongProductionVolumeFactor['childFactors']
            | keyof SiteConsiderationsFactor['childFactors']
            | keyof EcologicalReceptorsFactor['childFactors']
            | keyof OtherLossesFactor['childFactors']
    ) => {
        const inputElement = event.target as HTMLInputElement;
        let newValue = parseInt(inputElement.value, 10) || 0;

        const excess = newValue - childExclusiveTotal(parentField, field);

        if (form.impactFactors[parentField]?.childFactors) {
            const childFactors = form.impactFactors[parentField]?.childFactors ?? {};
            if (childFactors[field]) {
                if (excess > 0) {
                    childFactors[field].value = newValue - excess;
                } else {
                    childFactors[field].value = newValue;
                }
            }
        }
    };

    const exclusiveTotal = (field: keyof ScenarioForm['impactFactors']) => {
        let sum = 0;
        for (const key in form.impactFactors) {
            if (key !== field) {
                if (form.impactFactors[key].selected) {
                    sum += form.impactFactors[key].value;
                }
            }
        }

        return 100 - sum;
    };

    const childExclusiveTotal = (
        parentField: keyof ScenarioForm['impactFactors'],
        field:
            | keyof LossesFactor['childFactors']
            | keyof SensitiveReceptorsFactor['childFactors']
            | keyof EnvironmentFactor['childFactors']
            | keyof AnnProductionVolumeFactor['childFactors']
            | keyof FiveYearProductionVolumeFactor['childFactors']
            | keyof LifelongProductionVolumeFactor['childFactors']
            | keyof SiteConsiderationsFactor['childFactors']
            | keyof EcologicalReceptorsFactor['childFactors']
            | keyof OtherLossesFactor['childFactors']
    ) => {
        let sum = 0;
        for (const key in form.impactFactors[parentField]?.childFactors) {
            const childFactors = form.impactFactors[parentField]?.childFactors ?? {};
            if (childFactors[field]) {
                if (key !== field) {
                    if (childFactors[key].selected) {
                        sum += childFactors[key].value;
                    }
                }
            }
        }

        return 100 - sum;
    };

    const sendEmail = () => {
        const recipient = import.meta.env.VITE_EMAIL_RECIPIENT;

        const mailtoLink = `mailto:${recipient}`;

        window.location.href = mailtoLink;
    };
</script>
<template>
    <div class="flex-auto">
        <CreateScenarioSubHeading :text="impactFactorsSubHeading" />

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

        <span v-if="orderedImpactFactorsLabels.length">
            <PCard
                class="mb-4 shadow-md shadow-slate-300"
                :pt="{
                    root: {
                        class: `input-card ${factorDisabled(label.field) ? 'bg-gray-200' : ''}`
                    },
                    body: { class: 'p-3' }
                }"
                v-for="(label, index) in orderedImpactFactorsLabels"
                :key="index"
            >
                <template #content>
                    <ImpactFactorInput
                        :label="label"
                        :disabled="
                            factorDisabled(label.field) ||
                            !scenarioFormStore.availableImpactFactors?.[label.field].selected
                        "
                        :remaining-total="exclusiveTotal(label.field)"
                    >
                        <InputNumber
                            :inputId="`${label.field}-percent`"
                            class="percentage-input-number"
                            v-model="form.impactFactors[label.field].value"
                            size="small"
                            @input="(event) => onInput(event.originalEvent, label.field.toString())"
                            :disabled="
                                factorDisabled(label.field) ||
                                !form.impactFactors[label.field].selected ||
                                !scenarioFormStore.availableImpactFactors?.[label.field].selected
                            "
                        />
                    </ImpactFactorInput>

                    <span
                        v-if="
                            (label.field === 'losses' ||
                                label.field === 'sensitiveReceptors' ||
                                label.field === 'environment' ||
                                label.field === 'annProductionVolume' ||
                                label.field === 'fiveYearProductionVolume' ||
                                label.field === 'lifelongProductionVolume' ||
                                label.field === 'siteConsiderations' ||
                                label.field === 'ecologicalReceptors' ||
                                label.field === 'otherLosses') &&
                            label.childFields
                        "
                    >
                        <Divider />
                        <div>
                            <span v-for="(child, index) in label.childFields" :key="index">
                                <ImpactFactorInput
                                    class="mb-1"
                                    :label="child"
                                    :parentFactor="form.impactFactors[label.field].childFactors[child.field]"
                                    :disabled="
                                        childFactorDisabled(label.field, child.field) ||
                                        !scenarioFormStore.availableImpactFactors?.[label.field].childFactors[
                                            child.field
                                        ].selected
                                    "
                                    :parentDisabled="
                                        factorDisabled(label.field) ||
                                        !form.impactFactors[label.field].selected ||
                                        !scenarioFormStore.availableImpactFactors?.[label.field].selected
                                    "
                                    :remaining-total="childExclusiveTotal(label.field, child.field.toString())"
                                >
                                    <InputNumber
                                        class="percentage-input-number"
                                        :inputId="`${child.field}-percent`"
                                        v-model="form.impactFactors[label.field].childFactors[child.field].value"
                                        @input="
                                            (event) =>
                                                onChildInput(event.originalEvent, label.field, child.field.toString())
                                        "
                                        size="small"
                                        :disabled="
                                            childFactorDisabled(label.field, child.field) ||
                                            !form.impactFactors[label.field].selected ||
                                            !scenarioFormStore.availableImpactFactors?.[label.field].childFactors[
                                                child.field
                                            ].selected
                                        "
                                    />
                                </ImpactFactorInput>
                            </span>
                        </div>
                    </span>
                </template>
            </PCard>
        </span>
        <ul class="requirements list-disc ml-8">
            <li
                key="parents-100"
                :class="
                    scenarioFormStore.sumsTo100(ScenarioFormTitle.ImpactFactors) ? 'text-green-500' : 'text-gray-400'
                "
            >
                Factors must add to 100%
            </li>
            <li
                key="children-100"
                :class="
                    !scenarioFormStore.nestedImpactFactorActive
                        ? 'text-gray-400 line-through'
                        : scenarioFormStore.childrenSumTo100('losses') &&
                            scenarioFormStore.childrenSumTo100('sensitiveReceptors') &&
                            scenarioFormStore.childrenSumTo100('environment') &&
                            scenarioFormStore.childrenSumTo100('annProductionVolume') &&
                            scenarioFormStore.childrenSumTo100('fiveYearProductionVolume') &&
                            scenarioFormStore.childrenSumTo100('lifelongProductionVolume') &&
                            scenarioFormStore.childrenSumTo100('siteConsiderations') &&
                            scenarioFormStore.childrenSumTo100('ecologicalReceptors') &&
                            scenarioFormStore.childrenSumTo100('otherLosses')
                          ? 'text-green-500'
                          : 'text-gray-400'
                "
            >
                Child factors must add to 100%
            </li>
        </ul>
        <div class="flex flex-col items-start">
            <span>Require additional impact factors? Email us to suggest a new field.</span>
            <PButton class="btn-secondary mt-4 bg-secondary-500 py-2 px-6" @click="sendEmail">
                <span class="font-bold">Contact Us</span>
            </PButton>
        </div>
    </div>
</template>
