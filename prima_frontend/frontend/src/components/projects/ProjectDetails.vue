<script setup lang="ts">
    import { onMounted, ref, watch, nextTick } from 'vue';
    import type { MinimalDetailsScenario } from '@/types/scenario';
    import type { MinimalDetailsProject } from '@/types/projects';
    import type { Well } from '@/types/well';
    import { createScenarioService } from '@/services/scenarioService';
    import ScenarioDetailView from '../scenario/ScenarioDetailView.vue';

    const props = defineProps({
        scenarios: {
            required: false,
            type: Array as () => MinimalDetailsScenario[]
        },
        visibleProjects: {
            required: false,
            type: Array as () => MinimalDetailsProject[]
        },
        sideBySide: {
            required: false,
            type: Boolean,
            default: false
        },
        scenarioScreenLoading: {
            // Triggered when toggling projects / scenarios on the sidebar
            required: false,
            type: Boolean,
            default: false
        }
    });
    const visibleScenariosLoading = ref(false);
    const postInitialScreenLoaded = ref(false);
    const initialScenarioData = ref<Record<string, Record<string, { total: number; data: Well[] }>> | null>({});

    watch(
        () => visibleScenariosLoading.value,
        async (newVal) => {
            if (!newVal) {
                await nextTick();
                postInitialScreenLoaded.value = true;
            }
        },
        { immediate: true }
    );

    onMounted(async () => {
        visibleScenariosLoading.value = true;

        if (props.scenarios?.length === 0) {
            initialScenarioData.value = null;
            visibleScenariosLoading.value = false;
            return;
        }

        try {
            const scenarioService = createScenarioService();
            const result = props.visibleProjects?.reduce(
                (acc, item: MinimalDetailsProject) => {
                    const { scenarioId, id } = item;

                    // If the scenarioId key doesn't exist, create an empty array for it
                    if (!acc[scenarioId]) {
                        acc[scenarioId] = [];
                    }

                    // Push the id to the array for the corresponding scenarioId
                    acc[scenarioId].push(id);

                    return acc;
                },
                {} as { [key: number]: number[] }
            );

            initialScenarioData.value = await scenarioService.getInitialVisibleScenarioWells(result);
        } catch (error) {
            console.error(error);
        } finally {
            visibleScenariosLoading.value = false;
        }
    });
</script>
<template>
    <div class="container" :class="sideBySide ? 'grid grid-cols-2' : ''">
        <div v-if="scenarios?.length === 0"><h3>Choose a scenario to view details</h3></div>
        <template v-for="scenario in scenarios" :key="scenario.id">
            <template v-if="scenario">
                <ScenarioDetailView
                    class="m-3"
                    :scenario="scenario"
                    :visibleProjects="visibleProjects?.filter((project) => project.scenarioId === scenario.id)"
                    :scenarioScreenLoading="scenarioScreenLoading || visibleScenariosLoading"
                    :initialScenarioData="initialScenarioData ? initialScenarioData[scenario.id] : null"
                    :postInitialLoad="postInitialScreenLoaded"
                    @changeTab="($event) => $emit('changeTab', $event)"
                    @displayOverrides="($event) => $emit('displayOverrides', $event)"
                    :sideBySide="sideBySide"
                    @overrideActive="($event) => $emit('overrideActive')"
                    @overrideInactive="($event) => $emit('overrideInactive')"
                />
            </template>
        </template>
        <br /><br /><br />
    </div>
</template>
