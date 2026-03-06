<script setup lang="ts">
    import { Message, Dialog } from 'primevue';

    defineProps<{
        handleScenarioCopy: () => void;
    }>();

    const scenarioCopyVisible = defineModel<boolean>('scenarioCopyVisible', {
        default: false
    });
</script>

<template>
    <Dialog
        v-model:visible="scenarioCopyVisible"
        modal
        header="Confirm Scenario Copy & Edit"
        :style="{ width: '35rem' }"
    >
        <Message clsss="mb-8" severity="warn" icon="pi pi-exclamation-triangle">
            <span class="text-sm font-bold">
                You will be redirected to the PRIMO Use Cases page, where a new scenario will be initialized with all
                the parameters of the <i>General Specifications</i>, <i>Impact Factors</i>, and
                <i>Efficiency Factors</i>
                pages pre-loaded.
            </span>
            <div class="text-sm mt-4 font-bold">To edit this scenario, modify the input fields as needed.</div>
        </Message>
        <template #footer>
            <PButton
                label="Cancel"
                class="p-button-secondary p-button-outlined"
                @click="scenarioCopyVisible = false"
            ></PButton>
            <PButton label="Continue" @click="handleScenarioCopy"></PButton>
        </template>
    </Dialog>
</template>
