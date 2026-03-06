<script setup lang="ts">
    import Message from 'primevue/message';
    import { useScenarioFormStore } from '@/stores/form/scenarioForm';
    const scenarioFormStore = useScenarioFormStore();
    const { form, v$ } = scenarioFormStore;

    const basicDataChecksOptions = [
        { label: 'True', value: true },
        { label: 'False', value: false }
    ];

    const dataReplacementOptions = [
        { label: 'Specify Value', value: 'specify-value' },
        { label: 'Remove Wells', value: 'remove-wells' }
    ];

    const typeOptions = [
        { label: 'DOW', value: 'oil' },
        { label: 'LUOW', value: 'gas' }
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
            class="mb-4"
            icon="pi pi-exclamation-triangle"
        >
            The following inputs may be optionally used to modify the underlying well dataset.
        </Message>
        <div class="flex flex-col gap-2">
            <div class="flex flex-row items-center text-sm">
                <LabelTooltip
                    containerClass="block mb-2 mr-2 flex flex-row items-center"
                    label="Basic Data Checks*: "
                    tooltip="Whether to perform checks on the input data to verify if:
                        1. The Well IDs are unique. 
                        2. The latitude, longitude, operator name, age, and depth information are available for all wells (required for Well ranking and P&A project recommendations).
                        3. The latitude, longitude, age, and depth information are valid within a reasonable range.

                        Additionally,
                        4. Classify the wells into shallow wells and deep wells based on the depth information in the input data file."
                />
                <SelectButton
                    inputId="basic-data-checks"
                    v-model="form.generalSpecifications.dataQuality.basicDataChecks"
                    @input="handleFieldChange('generalSpecifications.dataQuality.basicDataChecks')"
                    @blur="v$.generalSpecifications.dataQuality.basicDataChecks.$touch()"
                    :options="basicDataChecksOptions"
                    optionLabel="label"
                    optionValue="value"
                    :pt="{ label: { class: 'text-sm' } }"
                />
            </div>
        </div>

        <div class="flex flex-col gap-2 mt-8">
            <div class="flex flex-row items-center text-sm">
                <LabelTooltip
                    containerClass="block mb-1 mr-2 flex flex-row items-center"
                    label="Handle Missing Well Age*:"
                    labelClass="underline"
                    tooltip="What action to take when age information is missing for wells"
                />
                <SelectButton
                    inputId="missing-well-age"
                    v-model="form.generalSpecifications.dataQuality.handleMissingWellAge"
                    @input="handleFieldChange('generalSpecifications.dataQuality.handleMissingWellAge')"
                    @blur="v$.generalSpecifications.dataQuality.handleMissingWellAge.$touch()"
                    :options="dataReplacementOptions"
                    optionLabel="label"
                    optionValue="value"
                    :pt="{ label: { class: 'text-sm' } }"
                />
                <ValidationError
                    :errors="scenarioFormStore.v$.generalSpecifications.dataQuality.handleMissingWellAge.$errors"
                />
            </div>
            <Message
                :closable="false"
                class="w-2/3"
                :pt="{ text: { class: 'text-xs' } }"
                v-if="form.generalSpecifications.dataQuality.handleMissingWellAge === 'specify-value'"
                icon="pi pi-info-circle"
            >
                Specify Value: Fill missing age data with a user-defined, specific age for wells
            </Message>
            <Message
                :closable="false"
                severity="warn"
                class="w-2/3"
                :pt="{ text: { class: 'text-xs' } }"
                v-if="form.generalSpecifications.dataQuality.handleMissingWellAge === 'remove-wells'"
                icon="pi pi-exclamation-triangle"
            >
                Remove Wells: Exclude wells with missing age information from the analysis
            </Message>
            <div class="flex flex-row gap-auto mt-2 ml-10 justify-between">
                <div>
                    <LabelTooltip
                        containerClass="block mb-2 mr-2 text-sm flex flex-row items-center"
                        labelFor="specified-age"
                        label="Specify Age*:"
                        tooltip="User-defined assumed age value for wells with missing age information"
                    />
                </div>
                <div class="flex flex-col w-1/3 mr-64">
                    <InputGroup>
                        <InputNumber
                            inputId="specified-age"
                            v-model="form.generalSpecifications.dataQuality.specifiedAge"
                            @input="handleFieldChange('generalSpecifications.dataQuality.specifiedAge')"
                            @blur="v$.generalSpecifications.dataQuality.specifiedAge.$touch()"
                            :max-fraction-digits="0"
                            :disabled="form.generalSpecifications.dataQuality.handleMissingWellAge === 'remove-wells'"
                        />
                        <InputGroupAddon>years</InputGroupAddon>
                    </InputGroup>

                    <ValidationError
                        :errors="scenarioFormStore.v$.generalSpecifications.dataQuality.specifiedAge.$errors"
                    />
                </div>
            </div>
        </div>

        <div class="flex flex-col gap-2 mt-8">
            <div class="flex flex-row items-center text-sm">
                <LabelTooltip
                    containerClass="block mb-2 mr-2 text-sm flex flex-row items-center"
                    labelClass="underline"
                    label="Handle Missing Well Depth*:"
                    tooltip="What action to take when depth information is missing for wells"
                />
                <SelectButton
                    inputId="handle-missing-depth"
                    v-model="form.generalSpecifications.dataQuality.handleMissingDepth"
                    @input="handleFieldChange('generalSpecifications.dataQuality.handleMissingDepth')"
                    @blur="v$.generalSpecifications.dataQuality.handleMissingDepth.$touch()"
                    :options="dataReplacementOptions"
                    optionLabel="label"
                    optionValue="value"
                    :pt="{ label: { class: 'text-sm' } }"
                />
                <ValidationError
                    :errors="scenarioFormStore.v$.generalSpecifications.dataQuality.handleMissingDepth.$errors"
                />
            </div>
            <Message
                :closable="false"
                class="w-2/3"
                :pt="{ text: { class: 'text-xs' } }"
                v-if="form.generalSpecifications.dataQuality.handleMissingDepth === 'specify-value'"
                icon="pi pi-info-circle"
            >
                Specify Value: Fill missing depth data with a user-defined, specific depth value for wells
            </Message>
            <Message
                :closable="false"
                severity="warn"
                class="w-2/3"
                :pt="{ text: { class: 'text-xs' } }"
                v-if="form.generalSpecifications.dataQuality.handleMissingDepth === 'remove-wells'"
                icon="pi pi-exclamation-triangle"
            >
                Remove Wells: Exclude wells with missing depth information from the analysis
            </Message>
            <div class="flex flex-row gap-auto mt-2 ml-10 justify-between">
                <div>
                    <LabelTooltip
                        containerClass="block mb-2 mr-2 text-sm flex flex-row items-center"
                        labelFor="specified-depth"
                        label="Specify Depth*:"
                        tooltip="User-defined assumed depth value for wells with missing depth information"
                    />
                </div>
                <div class="flex flex-col w-1/3 mr-64">
                    <InputGroup>
                        <InputNumber
                            inputId="specified-depth"
                            v-model="form.generalSpecifications.dataQuality.specifiedDepth"
                            @input="handleFieldChange('generalSpecifications.dataQuality.specifiedDepth')"
                            @blur="v$.generalSpecifications.dataQuality.specifiedDepth.$touch()"
                            :max-fraction-digits="0"
                            :disabled="form.generalSpecifications.dataQuality.handleMissingDepth === 'remove-wells'"
                        />
                        <InputGroupAddon>ft.</InputGroupAddon>
                    </InputGroup>

                    <ValidationError
                        :errors="scenarioFormStore.v$.generalSpecifications.dataQuality.specifiedDepth.$errors"
                    />
                </div>
            </div>
        </div>

        <div class="flex flex-col gap-2 mt-8">
            <div class="flex flex-row items-center text-sm">
                <LabelTooltip
                    containerClass="block mb-2 mr-2 text-sm flex flex-row items-center"
                    label="Handle Missing Production*:"
                    labelClass="underline"
                    tooltip="What actions to take when production information is missing for wells"
                />
                <SelectButton
                    inputId="handle-missing-production"
                    v-model="form.generalSpecifications.dataQuality.handleMissingProduction"
                    @input="handleFieldChange('generalSpecifications.dataQuality.handleMissingProduction')"
                    @blur="v$.generalSpecifications.dataQuality.handleMissingProduction.$touch()"
                    :options="dataReplacementOptions"
                    optionLabel="label"
                    optionValue="value"
                    :pt="{ label: { class: 'text-sm' } }"
                />
            </div>
            <Message
                :closable="false"
                class="w-2/3"
                :pt="{ text: { class: 'text-xs' } }"
                v-if="form.generalSpecifications.dataQuality.handleMissingProduction === 'specify-value'"
                icon="pi pi-info-circle"
            >
                Specify Value: Assume a user-defined, specific production volume for wells with missing production data
            </Message>
            <Message
                :closable="false"
                class="w-2/3"
                severity="warn"
                :pt="{ text: { class: 'text-xs' } }"
                v-if="form.generalSpecifications.dataQuality.handleMissingProduction === 'remove-wells'"
                icon="pi pi-exclamation-triangle"
            >
                Remove Wells: Exclude wells with missing production information from the analysis
            </Message>

            <div class="flex flex-row gap-auto mt-2 ml-10 justify-between">
                <div>
                    <LabelTooltip
                        containerClass="block mb-2 mr-2 text-sm flex flex-row items-center"
                        labelFor="specified-annual-oil-production"
                        label="Specify Annual Oil Production*:"
                        tooltip="User-defined assumed annual oil production value for wells with missing information (Bbl)."
                    />
                </div>
                <div class="flex flex-col w-1/3 mr-64">
                    <InputGroup>
                        <InputNumber
                            inputId="specified-annual-oil-production"
                            v-model="form.generalSpecifications.dataQuality.specifiedAnnualOilProduction"
                            @input="handleFieldChange('generalSpecifications.dataQuality.specifiedAnnualOilProduction')"
                            @blur="v$.generalSpecifications.dataQuality.specifiedAnnualOilProduction.$touch()"
                            :max-fraction-digits="2"
                            :disabled="
                                form.generalSpecifications.dataQuality.handleMissingProduction === 'remove-wells'
                            "
                        />
                        <InputGroupAddon>Bbl</InputGroupAddon>
                    </InputGroup>
                    <ValidationError
                        :errors="
                            scenarioFormStore.v$.generalSpecifications.dataQuality.specifiedAnnualOilProduction.$errors
                        "
                    />
                </div>
            </div>

            <div class="flex flex-row gap-auto mt-2 ml-10 justify-between">
                <div>
                    <LabelTooltip
                        containerClass="block  mb-2 mr-2 text-sm flex flex-row items-center"
                        labelFor="specified-annual-gas-production"
                        label="Specify Annual Gas Production*:"
                        tooltip="User-defined assumed annual gas production value for wells with missing information (Mcf)"
                    />
                </div>
                <div class="flex flex-col w-1/3 mr-64">
                    <InputGroup>
                        <InputNumber
                            inputId="specified-annual-gas-production"
                            v-model="form.generalSpecifications.dataQuality.specifiedAnnualGasProduction"
                            @input="handleFieldChange('generalSpecifications.dataQuality.specifiedAnnualGasProduction')"
                            @blur="v$.generalSpecifications.dataQuality.specifiedAnnualGasProduction.$touch()"
                            :max-fraction-digits="2"
                            :disabled="
                                form.generalSpecifications.dataQuality.handleMissingProduction === 'remove-wells'
                            "
                        />
                        <InputGroupAddon>Mcf</InputGroupAddon>
                    </InputGroup>
                    <ValidationError
                        :errors="
                            scenarioFormStore.v$.generalSpecifications.dataQuality.specifiedAnnualGasProduction.$errors
                        "
                    />
                </div>
            </div>

            <div class="flex flex-row gap-auto mt-2 ml-10 justify-between">
                <div>
                    <LabelTooltip
                        containerClass="block mb-2 mr-2 text-sm flex flex-row items-center"
                        labelFor="specified-lifetime-oil-production"
                        label="Specify Lifetime Oil Production*:"
                        tooltip="User-defined assumed lifetime oil production value for wells with missing information (Bbl)"
                    />
                </div>
                <div class="flex flex-col w-1/3 mr-64">
                    <InputGroup>
                        <InputNumber
                            inputId="specified-lifetime-oil-production"
                            v-model="form.generalSpecifications.dataQuality.specifiedLifetimeOilProduction"
                            @input="
                                handleFieldChange('generalSpecifications.dataQuality.specifiedLifetimeOilProduction')
                            "
                            @blur="v$.generalSpecifications.dataQuality.specifiedLifetimeOilProduction.$touch()"
                            :max-fraction-digits="2"
                            :disabled="
                                form.generalSpecifications.dataQuality.handleMissingProduction === 'remove-wells'
                            "
                        />
                        <InputGroupAddon>Bbl</InputGroupAddon>
                    </InputGroup>
                    <ValidationError
                        :errors="
                            scenarioFormStore.v$.generalSpecifications.dataQuality.specifiedLifetimeOilProduction
                                .$errors
                        "
                    />
                </div>
            </div>

            <div class="flex flex-row gap-auto mt-2 ml-10 justify-between">
                <div>
                    <LabelTooltip
                        containerClass="block mb-2 mr-2 text-sm flex flex-row items-center"
                        labelFor="specified-lifetime-gas-production"
                        label="Specify Lifetime Gas Production*:"
                        tooltip="User-defined assumed lifetime gas production value for wells with missing information (Mcf)"
                    />
                </div>
                <div class="flex flex-col w-1/3 mr-64">
                    <InputGroup>
                        <InputNumber
                            inputId="specified-lifetime-gas-production"
                            v-model="form.generalSpecifications.dataQuality.specifiedLifetimeGasProduction"
                            @input="
                                handleFieldChange('generalSpecifications.dataQuality.specifiedLifetimeGasProduction')
                            "
                            @blur="v$.generalSpecifications.dataQuality.specifiedLifetimeGasProduction.$touch()"
                            :max-fraction-digits="2"
                            :disabled="
                                form.generalSpecifications.dataQuality.handleMissingProduction === 'remove-wells'
                            "
                        />
                        <InputGroupAddon>Mcf</InputGroupAddon>
                    </InputGroup>
                    <ValidationError
                        :errors="
                            scenarioFormStore.v$.generalSpecifications.dataQuality.specifiedLifetimeGasProduction
                                .$errors
                        "
                    />
                </div>
            </div>
        </div>

        <div class="flex flex-col gap-2 mt-8">
            <div class="flex flex-row items-center text-sm">
                <LabelTooltip
                    containerClass="block mb-2 mr-2 text-sm flex flex-row items-center"
                    labelClass="underline"
                    label="Handle Missing Well Type*:"
                    tooltip="What action to take when the well type information is missing for wells"
                />
                <SelectButton
                    inputId="handle-missing-type"
                    v-model="form.generalSpecifications.dataQuality.handleMissingType"
                    @input="handleFieldChange('generalSpecifications.dataQuality.handleMissingType')"
                    @blur="v$.generalSpecifications.dataQuality.handleMissingType.$touch()"
                    :options="dataReplacementOptions"
                    optionLabel="label"
                    optionValue="value"
                    :pt="{ label: { class: 'text-sm' } }"
                />
                <ValidationError
                    :errors="scenarioFormStore.v$.generalSpecifications.dataQuality.handleMissingType.$errors"
                />
            </div>
            <Message
                :closable="false"
                class="w-2/3"
                :pt="{ text: { class: 'text-xs' } }"
                v-if="form.generalSpecifications.dataQuality.handleMissingType === 'specify-value'"
                icon="pi pi-info-circle"
            >
                Specify Value: Assume a user-defined, specific type for wells missing type information
            </Message>
            <Message
                :closable="false"
                class="w-2/3"
                severity="warn"
                :pt="{ text: { class: 'text-xs' } }"
                v-if="form.generalSpecifications.dataQuality.handleMissingType === 'remove-wells'"
                icon="pi pi-exclamation-triangle"
            >
                Remove Wells: Exclude wells for which the well type information is missing from the analysis
            </Message>
            <div class="flex flex-row gap-auto mt-2 ml-10 justify-between">
                <div>
                    <LabelTooltip
                        containerClass="block mb-2 mr-2 text-sm flex flex-row items-center"
                        label="Specify Type*:"
                        tooltip="User-defined assumed type for wells missing a type"
                    />
                </div>
                <div class="flex flex-col w-1/3 mr-64">
                    <SelectButton
                        inputId="specified-type"
                        v-model="form.generalSpecifications.dataQuality.specifiedType"
                        @input="handleFieldChange('generalSpecifications.dataQuality.specifiedType')"
                        @blur="v$.generalSpecifications.dataQuality.specifiedType.$touch()"
                        :options="typeOptions"
                        optionLabel="label"
                        optionValue="value"
                        :pt="{ label: { class: 'text-sm' } }"
                        :disabled="form.generalSpecifications.dataQuality.handleMissingType === 'remove-wells'"
                    />
                    <ValidationError
                        :errors="scenarioFormStore.v$.generalSpecifications.dataQuality.specifiedType.$errors"
                    />
                </div>
            </div>
        </div>
    </div>
</template>
