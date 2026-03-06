<script setup lang="ts">
    import { Message } from 'primevue';
</script>

<template>
    <Message severity="warn">
        <div class="flex flex-col justify-center items-center gap-4">
            <p><i class="pi pi-exclamation-triangle"></i></p>
            <p>
                A Scenario configured for Well Ranking only does not include any P&A project recommendations, and
                therefore will not be shown.
            </p>

            <p>
                If you wish to obtain the corresponding P&A project recommendations, please use the "Copy and Edit
                Scenario Inputs" button. This will allow you to create a new scenario. When doing so, be sure to select
                the "P&A Project Recommendations" use case to access this functionality.
            </p>
        </div></Message
    >
</template>
