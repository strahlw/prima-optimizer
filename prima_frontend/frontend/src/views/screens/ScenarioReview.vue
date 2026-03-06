<script setup lang="ts">
    import { ref, onMounted } from 'vue';
    import ReviewProjectDetails from '../../components/projects/ReviewProjectDetails.vue';
    import { useRoute } from 'vue-router';
    import type { Scenario } from '@/types/scenario';
    import { useScenarioStore } from '@/stores/scenarioStore';
    import { createScenarioService } from '@/services/scenarioService';

    import Dialog from 'primevue/dialog';

    const scenarioService = createScenarioService();
    const scenarioStore = useScenarioStore();
    const error = ref<string | null>(null);
    const route = useRoute();
    const showVisible = ref(false);
    const scenarioId = Number(route.params.scenarioId);
    const scenarioData = ref<Scenario | null>(null);
    const actionMethod = ref<string | null>(null);
    const confirmAction = (action: string) => {
        actionMethod.value = action;
        showVisible.value = true;
    };

    const publishScenario = async () => {
        try {
            await scenarioService.publishScenario(scenarioId);
        } catch (err: any) {
            error.value = err.message || 'An error occurred';
        }
    };

    const deleteScenario = async () => {
        try {
            await scenarioService.deleteScenario(scenarioId);
        } catch (err: any) {
            error.value = err.message || 'An error occurred';
        }
    };

    onMounted(async () => {
        try {
            if (scenarioStore.scenarios.length === 0) {
                await scenarioStore.fetchScenarios();
            }
            scenarioData.value = scenarioStore.getScenarioById(scenarioId) ?? null;
            if (!scenarioData.value) {
                throw new Error('Scenario not found');
            }
        } catch (err: any) {
            error.value = err.message || 'An error occurred';
        }
    });
</script>

<template>
    <PCard class="mt-10">
        <template #header>
            <div class="flex flex-row justify-between items-center px-10 h-auto card-header">
                <h1>{{ scenarioData?.data.name }}</h1>
                <div class="flex flex-row gap-6 h-11">
                    <PButton severity="danger" class="font-bold" @click="confirmAction('delete')">Delete</PButton>
                    <PButton class="btn-secondary font-bold" @click="confirmAction('publish')"
                        >Publish Scenario <span class="text-2xl pb-0.5 ml-1">+</span></PButton
                    >
                </div>
            </div>
        </template>
        <template #content>
            <ReviewProjectDetails />
        </template>
    </PCard>
    <Dialog header="Confirm Action" v-model:visible="showVisible" :modal="true" :closable="false">
        <p>Are you sure you want to {{ actionMethod }} this scenario?</p>
        <div class="flex justify-end mt-4">
            <PButton
                label="No"
                icon="pi pi-times"
                class="font-bold mr-1"
                severity="danger"
                @click="showVisible = false"
            />
            <div v-if="actionMethod === 'publish'">
                <PButton label="Yes" icon="pi pi-check" class="btn-secondary font-bold" @click="publishScenario" />
            </div>
            <div v-if="actionMethod === 'delete'">
                <PButton label="Yes" icon="pi pi-check" class="btn-secondary font-bold" @click="deleteScenario" />
            </div>
        </div>
    </Dialog>
</template>
