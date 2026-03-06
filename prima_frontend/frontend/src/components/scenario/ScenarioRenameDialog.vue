<script setup lang="ts">
    import { Dialog } from 'primevue';

    defineProps<{
        handleScenarioRename: () => void;
    }>();

    const scenarioRenameVisible = defineModel<boolean>('scenarioRenameVisible', {
        default: false
    });

    const newScenarioName = defineModel<string>('newScenarioName', {
        default: ''
    });
</script>

<template>
    <Dialog v-model:visible="scenarioRenameVisible" modal header="Confirm Scenario Rename" :style="{ width: '30rem' }">
        <span class="mb-8">Provide your new Scenario name to proceed:</span>
        <div class="mt-4">
            <InputText
                inputId="scenarioName"
                v-model="newScenarioName"
                :pt="{ root: { class: 'p-1 text-sm' } }"
                :placeholder="'Scenario Name'"
                :class="{ 'w-2/3': true }"
            ></InputText>
        </div>

        <template #footer>
            <PButton
                label="Cancel"
                class="p-button-secondary p-button-outlined"
                @click="scenarioRenameVisible = false"
            ></PButton>
            <PButton label="Save" :disabled="!newScenarioName" @click="handleScenarioRename"></PButton>
        </template>
    </Dialog>
</template>
