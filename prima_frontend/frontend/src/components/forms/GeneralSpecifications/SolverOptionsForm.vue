<script setup lang="ts">
    import Message from 'primevue/message';
    import { useScenarioFormStore } from '@/stores/form/scenarioForm';
    const scenarioFormStore = useScenarioFormStore();
    const { form, v$ } = scenarioFormStore;

    // const modelOptions = [
    //     { label: 'Impact', value: 'impact' },
    //     { label: 'Impact & Efficiency', value: 'impact-and-efficiency' }
    // ];

    const modelOptions = [
        { label: 'Impact', value: 'impact', tooltip: 'Tooltip for Impact' },
        { label: 'Impact & Efficiency', value: 'impact-and-efficiency', tooltip: 'Tooltip for Impact & Efficiency' }
    ];

    const handleFieldChange = (fieldPath: string) => {
        scenarioFormStore.markFieldAsUserModified(fieldPath);

        // Touch the validation
        const pathParts = fieldPath.split('.');
        let validationRef = v$;
        pathParts.forEach((part) => {
            validationRef = validationRef[part];
        });
        validationRef.$touch();
    };
</script>

<template>
    <div>
        <Message
            :closable="false"
            :pt="{ text: { class: 'text-xs' } }"
            severity="warn"
            icon="pi pi-exclamation-triangle"
            class="mb-4"
        >
            Setting custom solver options may drastically alter the results of the optimization process. The default
            options should be used unless you are sure you will like to make modifications.</Message
        >

        <div class="flex flex-col">
            <div class="flex flex-row gap-auto justify-between mt-2">
                <div>
                    <LabelTooltip
                        containerClass="block text-sm whitespace-nowrap mr-4 mt-1 flex flex-row items-center"
                        labelFor="solver-time"
                        label="Solver Time:"
                        tooltip="The time limit for the optimization problem (seconds)"
                    />
                </div>
                <div class="flex flex-col w-full md:w-1/2 lg:mr-[26rem]">
                    <InputGroup>
                        <InputNumber
                            inputId="solver-time"
                            v-model="form.generalSpecifications.solver.solverTime"
                            @input="handleFieldChange('generalSpecifications.solver.solverTime')"
                            @blur="v$.generalSpecifications.solver.solverTime.$touch()"
                            :max-fraction-digits="0"
                            :disabled="scenarioFormStore.rankOnly"
                        />
                        <InputGroupAddon>sec.</InputGroupAddon>
                    </InputGroup>

                    <ValidationError :errors="scenarioFormStore.v$.generalSpecifications.solver.solverTime.$errors" />
                </div>
            </div>
        </div>

        <div class="flex flex-col mt-2">
            <div class="flex flex-row gap-auto mt-4 justify-between">
                <div>
                    <LabelTooltip
                        containerClass="block text-sm whitespace-nowrap mr-4 mt-1 flex flex-row items-center"
                        labelFor="absolute-gap"
                        label="Absolute Gap:"
                        tooltip="The maximum acceptable absolute gap for terminating the optimization algorithm"
                    />
                </div>
                <div class="flex flex-col w-full md:w-1/2 lg:mr-[26rem]">
                    <InputGroup>
                        <InputNumber
                            inputId="absolute-gap"
                            v-model="form.generalSpecifications.solver.absoluteGap"
                            @input="handleFieldChange('generalSpecifications.solver.absoluteGap')"
                            @blur="v$.generalSpecifications.solver.absoluteGap.$touch()"
                            :max-fraction-digits="2"
                            :disabled="scenarioFormStore.rankOnly"
                        />
                    </InputGroup>

                    <ValidationError :errors="scenarioFormStore.v$.generalSpecifications.solver.absoluteGap.$errors" />
                </div>
            </div>
        </div>

        <div class="flex flex-col mt-2">
            <div class="flex flex-row gap-auto mt-4 justify-between">
                <div>
                    <LabelTooltip
                        containerClass="block text-sm whitespace-nowrap mr-4 mt-1 flex flex-row items-center"
                        labelFor="relative-gap"
                        label="Relative Gap:"
                        tooltip="The maximum acceptable relative gap for terminating the optimization algorithm"
                    />
                </div>
                <div class="flex flex-col w-full md:w-1/2 ml-4 lg:mr-[26rem]">
                    <InputGroup>
                        <InputNumber
                            inputId="relative-gap"
                            v-model="form.generalSpecifications.solver.relativeGap"
                            @input="handleFieldChange('generalSpecifications.solver.relativeGap')"
                            @blur="v$.generalSpecifications.solver.relativeGap.$touch()"
                            :max-fraction-digits="5"
                            :disabled="scenarioFormStore.rankOnly"
                        />
                    </InputGroup>

                    <ValidationError :errors="scenarioFormStore.v$.generalSpecifications.solver.relativeGap.$errors" />
                </div>
            </div>
        </div>

        <div class="flex flex-col gap-2 mt-4">
            <div class="flex flex-row items-center text-sm">
                <LabelTooltip
                    containerClass="block text-sm whitespace-nowrap mr-4 mt-1 flex flex-row items-center"
                    label="Model:"
                    tooltip="What factors should be included in the objective function"
                />
                <SelectButton
                    inputId="model"
                    v-model="form.generalSpecifications.solver.model"
                    @input="handleFieldChange('generalSpecifications.solver.model')"
                    @blur="v$.generalSpecifications.solver.model.$touch()"
                    :options="modelOptions"
                    optionLabel="label"
                    optionValue="value"
                    :pt="{ label: { class: 'text-sm' } }"
                    :disabled="scenarioFormStore.rankOnly"
                />
                <ValidationError :errors="scenarioFormStore.v$.generalSpecifications.solver.model.$errors" />
            </div>
            <Message
                :closable="false"
                class="w-full my-2"
                :pt="{ text: { class: 'text-xs' } }"
                icon="pi pi-info-circle"
            >
                Impact: Only impact factors will be included in the objective function. PRIMO will optimize for
                high-impact plugging and abandonment projects, with efficiency scores calculated after solving the
                optimization problem. The computation time is expected to be shorter for this model.
            </Message>
            <Message
                :closable="false"
                class="w-full my-2"
                :pt="{ text: { class: 'text-xs' } }"
                icon="pi pi-info-circle"
            >
                Impact and Efficiency: Both impact and efficiency factors will be included in the objective function.
                PRIMO will optimize for high-impact and high-efficiency plugging and abandonment projects. The
                computation time is expected to be longer.
            </Message>
        </div>
    </div>
</template>
