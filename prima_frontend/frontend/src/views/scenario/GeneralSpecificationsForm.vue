<script setup lang="ts">
    import { onMounted } from 'vue';
    import { useScenarioFormStore } from '@/stores/form/scenarioForm';
    import GeneralForm from '@/components/forms/GeneralSpecifications/GeneralForm.vue';
    import PluggingCostForm from '@/components/forms/GeneralSpecifications/PluggingCostForm.vue';
    import DataQualityFactorsForm from '@/components/forms/GeneralSpecifications/DataQualityFactorsForm.vue';
    import SolverOptionsForm from '@/components/forms/GeneralSpecifications/SolverOptionsForm.vue';
    import { AccordionPanel, AccordionHeader, AccordionContent } from 'primevue';

    const scenarioFormStore = useScenarioFormStore();

    onMounted(() => {
        // TODO: Verify how this will work with copying scenarios, rank only and full
        scenarioFormStore.initializeGeneralSpecifications();
    });
</script>

<template>
    <div>
        <PAccordion :value="0" id="general-specifications-accordion">
            <AccordionPanel :value="0">
                <AccordionHeader>General*</AccordionHeader>
                <AccordionContent>
                    <GeneralForm />
                </AccordionContent>
            </AccordionPanel>
            <AccordionPanel :value="1">
                <AccordionHeader>Plugging Costs*</AccordionHeader>
                <AccordionContent>
                    <PluggingCostForm />
                </AccordionContent>
            </AccordionPanel>
            <AccordionPanel :value="2">
                <AccordionHeader>Data Quality Factors*</AccordionHeader>
                <AccordionContent>
                    <DataQualityFactorsForm />
                </AccordionContent>
            </AccordionPanel>
            <AccordionPanel :value="3" class="border-none mb-2">
                <AccordionHeader>Solver Options - (optional)</AccordionHeader>
                <AccordionContent>
                    <SolverOptionsForm />
                </AccordionContent>
            </AccordionPanel>
        </PAccordion>
        <ul class="requirements text-sm list-disc ml-8">
            <li
                key="general"
                :class="scenarioFormStore.v$.generalSpecifications.basic.$invalid ? 'text-gray-400' : 'text-green-500'"
            >
                Required General fields are complete
            </li>
            <li
                key="general"
                :class="
                    scenarioFormStore.v$.generalSpecifications.plugging.$invalid ? 'text-gray-400' : 'text-green-500'
                "
            >
                Required Plugging Cost fields are complete
            </li>
            <li
                key="general"
                :class="
                    scenarioFormStore.v$.generalSpecifications.dataQuality.$invalid ? 'text-gray-400' : 'text-green-500'
                "
            >
                Required Data Quality Factor fields are complete
            </li>
        </ul>
    </div>
</template>

<style scoped>
    label {
        font-weight: bold;
    }
</style>

<style>
    #general-specifications-accordion #budget,
    #cost,
    #scenario-name,
    #well-count-max,
    #min-wells-in-project,
    #max-wells-in-project,
    #well-depth-limit,
    #max-distance-between-wells,
    #min-lifetime-gas-production,
    #max-lifetime-gas-production,
    #max-lifetime-oil-production,
    #min-lifetime-oil-production,
    #shallow-gas-well,
    #shallow-oil-well,
    #deep-gas-well,
    #deep-oil-well,
    #cost-efficiency,
    #basic-data-checks,
    #specified-age,
    #specified-depth,
    #specified-type,
    #solver-time,
    #absolute-gap,
    #relative-gap,
    #model,
    #use-lazy-constraints {
        height: 2rem;
        font-size: 0.875rem;
    }

    #general-specifications-accordion .p-inputgroup {
        height: 2rem;
        font-size: 0.875rem;
    }
</style>
