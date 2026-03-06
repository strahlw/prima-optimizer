<script setup lang="ts">
    // TODO: Replace with real data, assess this when the review flow is reassessed
    import { ref, onMounted } from 'vue';
    import { useMockDataStore } from '@/stores/mockDataStore';
    import { projectTableColumns } from '../../constants/projectTableColumns';
    const projects = ref<any[]>([]); // TODO: Valid typing - #127 - Scenario Queue - Align with Python Output Data, address this when the review flow is reassessed

    const mockDataStore = useMockDataStore();

    onMounted(() => {
        projects.value = mockDataStore.getReviewProjects;
    });
</script>

<template>
    <div class="container">
        <div v-for="(project, i) in projects" :key="project" class="mb-6">
            <PCard>
                <template #header>
                    <div class="flex flex-row justify-between items-left py-2 px-10 h-auto card-header">
                        <h2>Project {{ i + 1 }}</h2>
                        <h2>
                            Impact Score:
                            <span class="text-secondary">{{ mockDataStore.getRandomNumber(70, 100, 2) }}</span>
                        </h2>
                        <h2>
                            Efficiency Score:
                            <span class="text-secondary">{{ mockDataStore.getRandomNumber(70, 100, 2) }}</span>
                        </h2>
                    </div>
                </template>
                <template #content>
                    <DataTable
                        :value="projects"
                        size="small"
                        showGridlines
                        :pt="{
                            headerRow: { class: 'bg-primary' },
                            thead: { class: 'bg-primary' },
                            column: { class: 'bg-primary-500' },
                            tableContainer: { class: 'rounded-t-lg' }
                        }"
                    >
                        <PColumn
                            :pt="{
                                headerCell: { class: 'bg-primary' },
                                sort: { class: 'bg-primary' },
                                headerTitle: { class: 'text-slate-50 text-sm' },
                                sortIcon: { class: 'text-slate-50' }
                            }"
                        >
                            <template #body="slotProps"
                                ><div class="text-black font-bold">{{ slotProps.index + 1 }}</div>
                            </template></PColumn
                        >

                        <PColumn
                            v-for="column in projectTableColumns"
                            :field="column.field"
                            :header="column.header"
                            :sortable="true"
                            :key="column.field"
                            :pt="{
                                headerCell: { class: 'bg-primary border-l-0' },
                                headerTitle: {
                                    class: 'text-slate-50 w-auto whitespace-nowrap overflow-visible text-sm'
                                },
                                sortIcon: { class: 'text-slate-50' }
                            }"
                        ></PColumn
                    ></DataTable>
                </template>
            </PCard>
        </div>
    </div>
</template>

<style scoped>
    .card-header {
        box-shadow: 0px 4px 4px 0px #00000040;
    }

    .p-card.p-component {
        border: 1px solid #e5e5e5;
        box-shadow: 0px 4px 4px 0px #00000040;
    }
</style>
