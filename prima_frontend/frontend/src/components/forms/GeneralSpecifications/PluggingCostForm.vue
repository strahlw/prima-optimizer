<script setup lang="ts">
    import Message from 'primevue/message';
    import { useScenarioFormStore } from '@/stores/form/scenarioForm';
    const scenarioFormStore = useScenarioFormStore();
    const { form, v$ } = scenarioFormStore;

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
    <div class="flex flex-col text-sm">
        <div class="w-1/2 mb-5">
            <Message :closable="false" :pt="{ text: { class: 'text-xs' } }" icon="pi pi-info-circle">
                Specify single-well cost by well type.</Message
            >
        </div>
        <h3 class="font-bold underline">Shallow Wells:</h3>
        <div class="grid grid-cols-2 gap-10">
            <div class="flex flex-col w-3/4">
                <label for="shallow-gas-well" class="block mb-2">Shallow DOW *:</label>
                <InputGroup>
                    <InputGroupAddon>$</InputGroupAddon>
                    <InputNumber
                        inputId="shallow-gas-well"
                        currency="USD"
                        locale="en-US"
                        v-model="form.generalSpecifications.plugging.shallowGasWellCost"
                        @input="handleFieldChange('generalSpecifications.plugging.shallowGasWellCost')"
                        @blur="v$.generalSpecifications.plugging.shallowGasWellCost.$touch()"
                        :max-fraction-digits="0"
                        :disabled="scenarioFormStore.rankOnly"
                    />
                </InputGroup>

                <ValidationError
                    :errors="scenarioFormStore.v$.generalSpecifications.plugging.shallowGasWellCost.$errors"
                />
            </div>
            <div class="flex flex-col w-3/4">
                <label for="shallow-oil-well" class="block mb-2">Shallow LUOW *:</label>
                <InputGroup>
                    <InputGroupAddon>$</InputGroupAddon>
                    <InputNumber
                        inputId="shallow-oil-well"
                        currency="USD"
                        locale="en-US"
                        v-model="form.generalSpecifications.plugging.shallowOilWellCost"
                        @input="handleFieldChange('generalSpecifications.plugging.shallowOilWellCost')"
                        @blur="v$.generalSpecifications.plugging.shallowOilWellCost.$touch()"
                        :max-fraction-digits="0"
                        :disabled="scenarioFormStore.rankOnly"
                    />
                </InputGroup>

                <ValidationError
                    :errors="scenarioFormStore.v$.generalSpecifications.plugging.shallowOilWellCost.$errors"
                />
            </div>
        </div>
        <h3 class="font-bold underline">Deep Wells:</h3>
        <div class="grid grid-cols-2 gap-10">
            <div class="flex flex-col w-3/4">
                <label for="deep-gas-well" class="block mb-2">Deep DOW *:</label>
                <InputGroup>
                    <InputGroupAddon>$</InputGroupAddon>
                    <InputNumber
                        inputId="deep-gas-well"
                        currency="USD"
                        locale="en-US"
                        v-model="form.generalSpecifications.plugging.deepGasWellCost"
                        @input="handleFieldChange('generalSpecifications.plugging.deepGasWellCost')"
                        @blur="v$.generalSpecifications.plugging.deepGasWellCost.$touch()"
                        :max-fraction-digits="0"
                        :disabled="scenarioFormStore.rankOnly"
                    />
                </InputGroup>

                <ValidationError
                    :errors="scenarioFormStore.v$.generalSpecifications.plugging.deepGasWellCost.$errors"
                />
            </div>
            <div class="flex flex-col w-3/4">
                <label for="deep-oil-well" class="block mb-2">Deep LUOW *:</label>
                <InputGroup>
                    <InputGroupAddon>$</InputGroupAddon>
                    <InputNumber
                        inputId="deep-oil-well"
                        currency="USD"
                        locale="en-US"
                        v-model="form.generalSpecifications.plugging.deepOilWellCost"
                        @input="handleFieldChange('generalSpecifications.plugging.deepOilWellCost')"
                        @blur="v$.generalSpecifications.plugging.deepOilWellCost.$touch()"
                        :max-fraction-digits="0"
                        :disabled="scenarioFormStore.rankOnly"
                    />
                </InputGroup>

                <ValidationError
                    :errors="scenarioFormStore.v$.generalSpecifications.plugging.deepOilWellCost.$errors"
                />
            </div>
        </div>
        <h3 class="font-bold underline">Cost Efficiency:</h3>
        <div class="flex flex-col w-1/4">
            <LabelTooltip
                containerClass="block mb-2 flex flex-row items-center"
                labelFor="cost-efficiency"
                label="Beta*: "
                tooltip="The cost efficiency exponent - β"
            />
            <InputNumber
                inputId="cost-efficiency"
                v-model="form.generalSpecifications.plugging.costEfficiency"
                @input="handleFieldChange('generalSpecifications.plugging.costEfficiency')"
                @blur="v$.generalSpecifications.plugging.costEfficiency.$touch()"
                :max-fraction-digits="2"
                :disabled="scenarioFormStore.rankOnly"
            />

            <ValidationError :errors="scenarioFormStore.v$.generalSpecifications.plugging.costEfficiency.$errors" />
        </div>
    </div>
</template>
