<script setup lang="ts">
    import { computed, onMounted, ref } from 'vue';
    import { faFire, faDroplet, faCircle, faX } from '@fortawesome/free-solid-svg-icons';
    import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';
    import { MultiSelect, Message } from 'primevue';
    import { useOrganizationStore } from '@/stores/organizationStore';
    import { useAuthStore } from '@/stores/authStore';
    import { useScenarioFormStore } from '@/stores/form/scenarioForm';
    import { useWellOverviewStore } from '@/stores/wellOverviewStore';
    import type { DatasetChangeEvent } from '@/types/dataset';
    import type { Organization } from '@/types/organization';
    import { faker } from '@faker-js/faker';

    const orgStore = useOrganizationStore();
    const authStore = useAuthStore();
    const organizations = ref<Organization[]>([]);
    const scenarioFormStore = useScenarioFormStore();
    const wellOverviewStore = useWellOverviewStore();
    const { form, v$ } = scenarioFormStore;
    const selectedOrg = ref<number | null>(null);
    const loading = ref(false);

    const additionalDatasets = computed(() => orgStore.getOrganizationAdditionalDatasets);
    const datasets = computed(() => orgStore.getOrganizationDatasets);

    const handleDatasetChange = (datasetId: DatasetChangeEvent) => {
        // Call a method on the other store to set the dataset based on the ID
        const dataset = orgStore.getDatasetById(datasetId.value);
        if (dataset) {
            wellOverviewStore.setDataset(dataset);
        }
    };

    onMounted(async () => {
        if (authStore.isSuperAdmin) {
            organizations.value = orgStore.getOrganizations;
            selectedOrg.value = form.generalSpecifications.basic.organizationId;
        } else if (authStore.getUser) {
            selectedOrg.value = authStore.getUser.organizationId;
            form.generalSpecifications.basic.organizationId = selectedOrg.value;
        }
    });

    const fillerEnabled = computed(() => import.meta.env.VITE_APP_ENV === 'local');

    function fakeData() {
        if (!fillerEnabled.value) return;

        if (!scenarioFormStore.rankOnly) {
            form.generalSpecifications.basic.budget = faker.number.int({ min: 200000, max: 2000000 });
            form.generalSpecifications.basic.maxWellsPerOwner = faker.number.int({ min: 0, max: 10000 });
            form.generalSpecifications.plugging.shallowGasWellCost = faker.number.int({ min: 1000, max: 5000 });
            form.generalSpecifications.plugging.shallowOilWellCost = faker.number.int({ min: 1000, max: 5000 });
            form.generalSpecifications.plugging.deepGasWellCost = faker.number.int({ min: 6000, max: 10000 });
            form.generalSpecifications.plugging.deepOilWellCost = faker.number.int({ min: 6000, max: 10000 });
        }

        form.generalSpecifications.basic.name = faker.lorem.words(2);
        form.generalSpecifications.basic.wellType = ['Gas', 'Oil'];

        form.generalSpecifications.dataQuality.specifiedAge = faker.number.int({ min: 0, max: 300 });
        form.generalSpecifications.dataQuality.specifiedDepth = faker.number.int({ min: 0, max: 20000 });
        form.generalSpecifications.dataQuality.specifiedAnnualGasProduction = faker.number.float({
            min: 100,
            max: 1000,
            fractionDigits: 2
        });
        form.generalSpecifications.dataQuality.specifiedAnnualOilProduction = faker.number.float({
            min: 100,
            max: 1000,
            fractionDigits: 2
        });
        form.generalSpecifications.dataQuality.specifiedLifetimeGasProduction = faker.number.float({
            min: 100000,
            max: 1000000,
            fractionDigits: 2
        });
        form.generalSpecifications.dataQuality.specifiedLifetimeOilProduction = faker.number.float({
            min: 100000,
            max: 1000000,
            fractionDigits: 2
        });
        form.generalSpecifications.dataQuality.specifiedType = faker.helpers.arrayElement(['gas', 'oil']);

        form.generalSpecifications.dataQuality.handleMissingWellAge = 'remove-wells';
        form.generalSpecifications.dataQuality.handleMissingDepth = 'remove-wells';
        form.generalSpecifications.dataQuality.handleMissingProduction = 'remove-wells';
        form.generalSpecifications.dataQuality.handleMissingType = 'remove-wells';

        form.generalSpecifications.solver.solverTime = 3600;
        form.generalSpecifications.solver.absoluteGap = 1;
        form.generalSpecifications.solver.relativeGap = 0.001;
        form.generalSpecifications.solver.model = 'impact';

        v$.generalSpecifications.basic.budget.$touch();
        v$.generalSpecifications.basic.name.$touch();
        v$.generalSpecifications.basic.wellType.$touch();
        v$.generalSpecifications.basic.maxWellsPerOwner.$touch();
        v$.generalSpecifications.plugging.shallowGasWellCost.$touch();
        v$.generalSpecifications.plugging.shallowOilWellCost.$touch();
        v$.generalSpecifications.plugging.deepGasWellCost.$touch();
        v$.generalSpecifications.plugging.deepOilWellCost.$touch();
        v$.generalSpecifications.dataQuality.specifiedAge.$touch();
        v$.generalSpecifications.dataQuality.specifiedDepth.$touch();
        v$.generalSpecifications.dataQuality.specifiedAnnualGasProduction.$touch();
        v$.generalSpecifications.dataQuality.specifiedAnnualOilProduction.$touch();
        v$.generalSpecifications.dataQuality.specifiedLifetimeGasProduction.$touch();
        v$.generalSpecifications.dataQuality.specifiedLifetimeOilProduction.$touch();
        v$.generalSpecifications.dataQuality.specifiedType.$touch();
        v$.generalSpecifications.solver.solverTime.$touch();
        v$.generalSpecifications.solver.absoluteGap.$touch();
        v$.generalSpecifications.solver.relativeGap.$touch();
        v$.generalSpecifications.solver.model.$touch();
    }

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
        <div class="flex flex-col my-4">
            <PButton v-if="fillerEnabled" class="p-3 w-fit" @click="fakeData">Fake Data</PButton>
        </div>
        <div class="grid grid-cols-2 text-sm gap-28">
            <div class="flex flex-col gap-2 col-start-1">
                <h3 class="font-bold underline">Basic Information:</h3>
                <div class="w-full flex flex-col" v-if="authStore.isSuperAdmin">
                    <LabelTooltip
                        containerClass="block mb-2 flex flex-row items-center"
                        label="Organization*: "
                        tooltip="Select your organization"
                    />
                    <PSelect
                        v-model="form.generalSpecifications.basic.organizationId"
                        :options="organizations"
                        optionLabel="key"
                        inputId="organization"
                        placeholder="Select an organization"
                        optionValue="id"
                        @input="handleFieldChange('generalSpecifications.basic.organizationId')"
                        @blur="v$.generalSpecifications.basic.organizationId.$touch()"
                        class="w-3/4 h-8 flex items-center"
                        :pt="{ input: { class: 'text-sm' }, wrapper: { class: 'text-sm' } }"
                    ></PSelect>
                    <ValidationError
                        :errors="scenarioFormStore.v$.generalSpecifications.basic.organizationId.$errors"
                    />
                </div>
                <div class="w-full flex flex-col">
                    <LabelTooltip
                        containerClass="block mb-2 flex flex-row items-center"
                        label="Well Dataset*: "
                        tooltip="Select the specific dataset to use for analysis"
                    />
                    <Message v-if="scenarioFormStore.optimizationOnly" icon="pi pi-info-circle" class="mb-3 mt-1"
                        ><span class="text-xs items-center flex"
                            >Please choose a dataset with ranking scores</span
                        ></Message
                    >
                    <PSelect
                        v-model="form.generalSpecifications.basic.datasetId"
                        :options="datasets"
                        optionLabel="name"
                        inputId="datasetId"
                        placeholder="Select a dataset"
                        optionValue="id"
                        @input="handleFieldChange('generalSpecifications.basic.datasetId')"
                        @blur="v$.generalSpecifications.basic.datasetId.$touch()"
                        :disabled="authStore.isSuperAdmin && selectedOrg === null && datasets.length === 0"
                        :loading="loading"
                        emptyMessage="There are no datasets available for this organization."
                        @change="handleDatasetChange"
                        class="w-3/4 h-8 flex items-center"
                        :pt="{ input: { class: 'text-sm' }, wrapper: { class: 'text-sm' } }"
                    ></PSelect>
                    <p
                        class="text-xs text-gray-500"
                        v-if="
                            (datasets.length === 0 || !datasets) &&
                            form.generalSpecifications.basic.organizationId !== null &&
                            !loading
                        "
                    >
                        There are no datasets available for this organization.
                    </p>
                    <ValidationError :errors="scenarioFormStore.v$.generalSpecifications.basic.datasetId.$errors" />
                </div>

                <div class="w-full flex flex-col overflow-scroll mt-2">
                    <LabelTooltip
                        containerClass="block mb-2 flex flex-row items-center"
                        label="Additional Datasets: "
                        tooltip="Select any supplementary datasets required for the analysis (currently under development)"
                    />
                    <MultiSelect
                        filter
                        :maxSelectedLabels="3"
                        class="md:w-20rem w-3/4 h-8 flex items-center"
                        v-model="form.generalSpecifications.basic.additionalDatasets"
                        :options="additionalDatasets"
                        optionLabel="name"
                        inputId="well-additional-datasets"
                        placeholder="Select additional data"
                        @input="handleFieldChange('generalSpecifications.basic.additionalDatasets')"
                        @blur="v$.generalSpecifications.basic.additionalDatasets.$touch()"
                        :disabled="authStore.isSuperAdmin && selectedOrg === null && datasets.length === 0"
                        :loading="loading"
                        :pt="{
                            root: { class: 'text-sm' },
                            filterInput: { class: 'text-sm h-8' },
                            filterContainer: { class: 'h-8' },
                            emptyMessage: { class: 'text-sm' },
                            option: { class: 'text-sm' },
                            item: { class: 'text-sm' }
                        }"
                    ></MultiSelect>
                    <ul v-if="form.generalSpecifications.basic.additionalDatasets">
                        <li
                            v-for="(set, index) in form.generalSpecifications.basic.additionalDatasets"
                            :key="`${index}-additional`"
                        >
                            {{ set.name }}
                        </li>
                    </ul>
                </div>

                <div class="flex flex-col">
                    <LabelTooltip
                        containerClass="block mb-2 flex flex-row items-center"
                        labelFor="scenario-name"
                        label="Scenario Name*: "
                        tooltip="Provide a name for the scenario"
                    />
                    <InputText
                        id="scenario-name"
                        v-model="form.generalSpecifications.basic.name"
                        @input="handleFieldChange('generalSpecifications.basic.name')"
                        @blur="v$.generalSpecifications.basic.name.$touch()"
                        :disabled="!form.generalSpecifications.basic.organizationId"
                    />
                    <small v-if="!form.generalSpecifications.basic.organizationId">Please select an Organization</small>
                    <ValidationError :errors="v$.generalSpecifications.basic.name.$errors" />
                </div>
            </div>
            <div class="flex flex-col gap-2 col-span-1">
                <h3 class="font-bold underline">Financial:</h3>
                <div class="flex flex-col">
                    <LabelTooltip
                        containerClass="block mb-2 flex flex-row items-center"
                        labelFor="budget"
                        label="P&A Budget*: "
                        tooltip="The total available budget for plugging wells (for a given scenario)"
                    />
                    <InputGroup>
                        <InputGroupAddon>$</InputGroupAddon>
                        <InputNumber
                            inputId="budget"
                            currency="USD"
                            locale="en-US"
                            v-model="form.generalSpecifications.basic.budget"
                            @input="handleFieldChange('generalSpecifications.basic.budget')"
                            @blur="v$.generalSpecifications.basic.budget.$touch()"
                            :max-fraction-digits="0"
                            :disabled="scenarioFormStore.rankOnly"
                        />
                    </InputGroup>

                    <ValidationError :errors="scenarioFormStore.v$.generalSpecifications.basic.budget.$errors" />
                </div>
            </div>
        </div>

        <div class="grid grid-cols-2 text-sm gap-28 mt-4">
            <div class="flex flex-col gap-2 col-start-1">
                <h3 class="font-bold underline">Project Configuration:</h3>
                <div class="w-full flex flex-col gap-3">
                    <LabelTooltip
                        containerClass="block mb-2 flex flex-row items-center"
                        label="Types Of Wells* "
                        tooltip="Select the type of wells to include in the analysis"
                    />
                    <div class="flex flex-row items-center gap-4">
                        <div class="flex flex-row items-center">
                            <PCheckbox
                                inputId="gas-wells"
                                value="Gas"
                                name="well-type"
                                v-model="form.generalSpecifications.basic.wellType"
                                @input="handleFieldChange('generalSpecifications.basic.wellType')"
                            />
                            <FontAwesomeIcon :icon="faCircle" class="ml-2" />
                            <LabelTooltip
                                containerClass="block ml-2 flex flex-row items-center"
                                labelFor="gas-wells"
                                label="DOWs "
                                tooltip="Documented Orphaned Wells"
                            />
                        </div>

                        <div class="flex items-center">
                            <PCheckbox
                                inputId="oil-wells"
                                value="Oil"
                                name="well-type"
                                v-model="form.generalSpecifications.basic.wellType"
                                @input="handleFieldChange('generalSpecifications.basic.wellType')"
                            />
                            <FontAwesomeIcon :icon="faX" class="ml-2" />
                            <LabelTooltip
                                containerClass="block ml-2 flex flex-row items-center"
                                labelFor="oil-wells"
                                label="LUOWs "
                                tooltip="Located Undocumented Orphaned Wells"
                            />
                        </div>
                    </div>
                </div>
                <!-- <div class="w-full flex flex-col mt-4">
                    <LabelTooltip
                        containerClass="mb-2 flex flex-row items-center"
                        label="Maximum Wells Per Owner:"
                        tooltip="The maximum number of wells an owner can have recommended for plugging across all plugging and abandonment projects for a given well type"
                    />
                    <InputNumber
                        inputId="well-count-max"
                        :pt="{ root: { class: 'w-1/4' } }"
                        v-model="form.generalSpecifications.basic.maxWellsPerOwner"
                        ref="wellCountRef"
                        @input="handleFieldChange('generalSpecifications.basic.maxWellsPerOwner')"
                        @blur="v$.generalSpecifications.basic.maxWellsPerOwner.$touch()"
                        :disabled="scenarioFormStore.rankOnly"
                    />
                    <ValidationError
                        :errors="scenarioFormStore.v$.generalSpecifications.basic.maxWellsPerOwner.$errors"
                    />
                </div> -->
                <div class="flex flex-col mt-2">
                    <LabelTooltip
                        containerClass="mb-2 flex flex-row items-center"
                        labelFor="min-wells-in-project"
                        label="Minimum # of project wells:"
                        tooltip="The minimum number of wells required in a plugging and abandonment project"
                    />
                    <InputNumber
                        inputId="min-wells-in-project"
                        :pt="{ root: { class: 'w-1/4' } }"
                        v-model="form.generalSpecifications.basic.minWellsInProject"
                        ref="minWellsInProjectRef"
                        @input="handleFieldChange('generalSpecifications.basic.minWellsInProject')"
                        @blur="v$.generalSpecifications.basic.minWellsInProject.$touch()"
                        :disabled="scenarioFormStore.rankOnly"
                    />
                    <ValidationError
                        :errors="scenarioFormStore.v$.generalSpecifications.basic.minWellsInProject.$errors"
                    />
                </div>
                <div class="flex flex-col mt-2">
                    <LabelTooltip
                        containerClass="mb-2 flex flex-row items-center"
                        labelFor="max-wells-in-project"
                        label="Maximum # of project wells:"
                        tooltip="The maximum number of wells allowed in a plugging and abandonment project "
                    />

                    <InputNumber
                        inputId="max-wells-in-project"
                        :pt="{ root: { class: 'w-1/4' } }"
                        v-model="form.generalSpecifications.basic.maxWellsInProject"
                        ref="maxWellsInProjectRef"
                        @input="handleFieldChange('generalSpecifications.basic.maxWellsInProject')"
                        @blur="v$.generalSpecifications.basic.maxWellsInProject.$touch()"
                        :disabled="scenarioFormStore.rankOnly"
                    />
                    <ValidationError
                        :errors="scenarioFormStore.v$.generalSpecifications.basic.maxWellsInProject.$errors"
                    />
                </div>
                <div class="flex flex-col mt-2">
                    <LabelTooltip
                        containerClass="block mb-2 flex flex-row items-center"
                        labelFor="well-depth-limit"
                        label="Shallow/Deep well depth limit "
                        tooltip="The depth value used to distinguish shallow from deep wells. Wells with depths below this value are considered “shallow wells”; otherwise, they are considered “deep wells”."
                    />
                    <InputGroup :pt="{ root: { class: 'w-1/2' } }">
                        <InputNumber
                            inputId="well-depth-limit"
                            :pt="{ root: { class: 'w-1/4' } }"
                            v-model="form.generalSpecifications.basic.wellDepthLimit"
                            ref="maxWellsInProjectRef"
                            @input="handleFieldChange('generalSpecifications.basic.wellDepthLimit')"
                            @blur="v$.generalSpecifications.basic.wellDepthLimit.$touch()"
                            :disabled="scenarioFormStore.rankOnly"
                        />
                        <InputGroupAddon>ft.</InputGroupAddon>
                    </InputGroup>

                    <ValidationError
                        :errors="scenarioFormStore.v$.generalSpecifications.basic.wellDepthLimit.$errors"
                    />
                </div>
                <div class="flex flex-col mt-2">
                    <LabelTooltip
                        containerClass="block mb-2 flex flex-row items-center"
                        label="Maximum distance between wells in project:"
                        tooltip="The maximum distance between any two wells in a plugging and abandonment project"
                    />
                    <InputGroup :pt="{ root: { class: 'w-1/2' } }">
                        <InputNumber
                            inputId="max-distance-between-wells"
                            :pt="{ root: { class: 'w-1/4' } }"
                            v-model="form.generalSpecifications.basic.maxDistanceBetweenProjectWells"
                            ref="maxDistanceBetweenProjectWellsRef"
                            @input="handleFieldChange('generalSpecifications.basic.maxDistanceBetweenProjectWells')"
                            @blur="v$.generalSpecifications.basic.maxDistanceBetweenProjectWells.$touch()"
                            :disabled="scenarioFormStore.rankOnly"
                        />
                        <InputGroupAddon>miles</InputGroupAddon>
                    </InputGroup>

                    <ValidationError
                        :errors="
                            scenarioFormStore.v$.generalSpecifications.basic.maxDistanceBetweenProjectWells.$errors
                        "
                    />
                </div>
            </div>
            <div class="flex flex-col gap-2 col-span-1">
                <h3 class="font-bold underline">Production Details:</h3>
                <div class="flex flex-col">
                    <LabelTooltip
                        containerClass="mb-2 flex flex-row items-center"
                        labelFor="min-lifetime-gas-production"
                        label="Minimum lifetime gas production:"
                        tooltip="Wells that produce less than this amount of gas (Mcf) over their entire lifetime will not be considered"
                    />

                    <InputGroup :pt="{ root: { class: 'w-3/4' } }">
                        <InputNumber
                            inputId="min-lifetime-gas-production"
                            :pt="{ root: { class: 'w-1/4' } }"
                            v-model="form.generalSpecifications.basic.minLifetimeGasProduction"
                            ref="minLifetimeGasProductionRef"
                            @input="handleFieldChange('generalSpecifications.basic.minLifetimeGasProduction')"
                            @blur="v$.generalSpecifications.basic.minLifetimeGasProduction.$touch()"
                        />
                        <InputGroupAddon>Mcf</InputGroupAddon>
                    </InputGroup>

                    <ValidationError
                        :errors="scenarioFormStore.v$.generalSpecifications.basic.minLifetimeGasProduction.$errors"
                    />
                </div>
                <div class="flex flex-col mt-2">
                    <LabelTooltip
                        containerClass="mb-2 flex flex-row items-center"
                        labelFor="max-lifetime-gas-production"
                        label="Maximum lifetime gas production:"
                        tooltip="Wells that produce more than this amount of gas (Mcf) over their entire lifetime will not be considered"
                    />
                    <InputGroup :pt="{ root: { class: 'w-3/4' } }">
                        <InputNumber
                            inputId="max-lifetime-gas-production"
                            :pt="{ root: { class: 'w-1/4' } }"
                            v-model="form.generalSpecifications.basic.maxLifetimeGasProduction"
                            ref="maxLifetimeGasProductionRef"
                            @input="handleFieldChange('generalSpecifications.basic.maxLifetimeGasProduction')"
                            @blur="v$.generalSpecifications.basic.maxLifetimeGasProduction.$touch()"
                        />
                        <InputGroupAddon>Mcf</InputGroupAddon>
                    </InputGroup>

                    <ValidationError
                        :errors="scenarioFormStore.v$.generalSpecifications.basic.maxLifetimeGasProduction.$errors"
                    />
                </div>
                <div class="flex flex-col mt-2">
                    <LabelTooltip
                        containerClass="mb-2 flex flex-row items-center"
                        labelFor="min-lifetime-oil-production"
                        label="Minimum lifetime oil production:"
                        tooltip="Wells that produce less than this amount of oil (Bbl) over their entire lifetime will not be considered"
                    />
                    <InputGroup :pt="{ root: { class: 'w-3/4' } }">
                        <InputNumber
                            inputId="min-lifetime-oil-production"
                            :pt="{ root: { class: 'w-1/4' } }"
                            v-model="form.generalSpecifications.basic.minLifetimeOilProduction"
                            ref="minLifetimeOilProductionRef"
                            @input="handleFieldChange('generalSpecifications.basic.minLifetimeOilProduction')"
                            @blur="v$.generalSpecifications.basic.minLifetimeOilProduction.$touch()"
                        />
                        <InputGroupAddon>Bbl</InputGroupAddon>
                    </InputGroup>
                    <ValidationError
                        :errors="scenarioFormStore.v$.generalSpecifications.basic.minLifetimeOilProduction.$errors"
                    />
                </div>
                <div class="flex flex-col mt-2">
                    <LabelTooltip
                        containerClass="mb-2 flex flex-row items-center"
                        labelFor="max-lifetime-oil-production"
                        label="Maximum lifetime oil production:"
                        tooltip="Wells that produce more than this amount of oil (Bbl) over their entire lifetime will not be considered"
                    />
                    <InputGroup :pt="{ root: { class: 'w-3/4' } }">
                        <InputNumber
                            inputId="max-lifetime-oil-production"
                            :pt="{ root: { class: 'w-1/4' } }"
                            v-model="form.generalSpecifications.basic.maxLifetimeOilProduction"
                            ref="maxLifetimeOilProductionRef"
                            @input="handleFieldChange('generalSpecifications.basic.maxLifetimeOilProduction')"
                            @blur="v$.generalSpecifications.basic.maxLifetimeOilProduction.$touch()"
                        />
                        <InputGroupAddon>Bbl</InputGroupAddon>
                    </InputGroup>
                    <ValidationError
                        :errors="scenarioFormStore.v$.generalSpecifications.basic.maxLifetimeOilProduction.$errors"
                    />
                </div>
            </div>
        </div>
    </div>
</template>
