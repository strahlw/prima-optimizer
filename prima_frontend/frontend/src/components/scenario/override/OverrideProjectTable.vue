<script setup lang="ts">
    import { computed, ref, watch } from 'vue';
    import type { PropType } from 'vue';
    import MultiSelect from 'primevue/multiselect';

    import type { MinimalDetailsProject, ScenarioProject } from '@/types/projects';
    import type { Well } from '@/types/well';
    import { scenarioDetailsKeyLabelMap } from '@/constants/scenarioDetailsColumns';

    const emit = defineEmits([
        'filter-query',
        'navigate',
        'page',
        'sort',
        'toggle-project',
        'remove-well',
        'readd-well',
        'add-wells'
    ]);
    const props = defineProps({
        project: {
            type: Object as PropType<MinimalDetailsProject | null>,
            required: true
        },
        wells: {
            type: Array as PropType<Well[]>,
            required: true
        },
        totalRecords: {
            type: Number,
            required: true
        },
        parentLoading: {
            type: Boolean,
            required: true
        },
        searchableWells: {
            type: Array as PropType<Well[]>,
            required: true
        },
        removedWells: {
            type: Array as PropType<Well[]>,
            required: true
        },
        reassignedWells: {
            type: Array as PropType<Well[]>,
            required: true
        },
        removedProjectIds: {
            type: Array as PropType<number[]>,
            required: true
        },
        wellsJustAdded: {
            type: Array as PropType<Well[]>,
            required: true
        },
        sideBySide: {
            type: Boolean,
            required: false,
            default: false
        },
        rows: {
            type: Number,
            required: false,
            default: 20
        }
    });

    const selectedWells = ref<Well[]>([]);
    const multiSelect = ref<any>(null);

    watch(
        () => props.wellsJustAdded,
        (newWells) => {
            if (newWells.length > 0 && selectedWells.value.length > 0) {
                selectedWells.value = selectedWells.value.filter(
                    (well) => !newWells.some((newWell) => newWell.wellId === well.wellId)
                );
            }
        }
    );

    const getScoreClass = (score?: number) => {
        if (!score) return '';
        if (score >= 0) {
            return 'text-green-500';
        } else {
            return 'text-red-500';
        }
    };

    const getIconClass = (score?: number) => {
        if (!score) return '';
        if (score >= 0) {
            return ' pi-arrow-up';
        } else {
            return ' pi-arrow-down';
        }
    };

    const wasWellRemoved = (well: Well) => {
        return props.removedWells.some((removedWell: Well) => removedWell.wellId === well.wellId);
    };

    const rowClass = (data: Well) => {
        // TODO: Make this more about what is available in the well pool / disabled projects than the search results
        return {
            'bg-gray-300 italic': wasWellRemoved(data) || projectDisabled.value,
            'bg-secondary-100': !data.projects || data.projects?.length === 0 || data.projectId !== props.project?.id
        };
    };

    const readdEnabled = (data: Well) => {
        if (data.projects?.some((p: ScenarioProject) => p.id !== props.project?.id)) {
            return false;
        }

        if (props.reassignedWells.some((well: Well) => well.wellId === data.wellId)) {
            return false;
        }

        return true;
    };

    const columns = computed(() => {
        return Object.keys(scenarioDetailsKeyLabelMap).filter((key) => key !== 'wellRank');
    });

    const projectDisabled = computed(() => {
        if (props.project) {
            return props.removedProjectIds.includes(props.project.id);
        }

        return false;
    });

    function addSelectedWells() {
        emit('add-wells', selectedWells.value, props.project?.id);
        multiSelect.value.clearFilter();
        selectedWells.value = [];
    }

    function onFilter(event: any) {
        emit('filter-query', event.value, props.project?.id); // Send query up to parent
    }
</script>
<template>
    <PCard>
        <template #header>
            <div
                class="flex justify-between items-center py-5 px-4 h-auto card-header overflow-visible xl:text-lg text-sm space-x-4"
                :class="{ 'xl:text-xs': sideBySide }"
            >
                <p class="flex-shrink-0 font-bold mt-0 mb-1">Project {{ project?.id }}</p>

                <p
                    class="font-bold mt-0 mb-1 flex items-center whitespace-nowrap"
                    v-if="project?.impactScore || project?.impactScore == 0"
                >
                    Impact Score:
                    <span class="text-primary ml-1">
                        {{ project?.impactScore.toFixed(2) ?? '' }}
                    </span>
                    <span
                        v-if="project?.parentProjectDifferentials?.impactScore && !sideBySide"
                        :class="getScoreClass(project?.parentProjectDifferentials?.impactScore)"
                        class="text-xs ml-2"
                    >
                        <i
                            :class="'pi text-xs mr-1' + getIconClass(project?.parentProjectDifferentials?.impactScore)"
                        ></i
                        >{{ project?.parentProjectDifferentials?.impactScore.toFixed(2) ?? '' }}
                    </span>
                </p>

                <p
                    class="font-bold mt-0 mb-1 flex items-center whitespace-nowrap"
                    v-if="project?.efficiencyScore || project?.efficiencyScore == 0"
                >
                    Efficiency Score:
                    <span class="text-primary ml-1">
                        {{ project?.efficiencyScore.toFixed(2) ?? '' }}
                    </span>
                    <span
                        v-if="project?.parentProjectDifferentials?.efficiencyScore && !sideBySide"
                        :class="getScoreClass(project?.parentProjectDifferentials?.efficiencyScore)"
                        class="text-xs ml-2"
                    >
                        <i
                            :class="
                                'pi text-xs mr-1' + getIconClass(project?.parentProjectDifferentials?.efficiencyScore)
                            "
                        ></i
                        >{{ project?.parentProjectDifferentials?.efficiencyScore.toFixed(2) ?? '' }}</span
                    >
                </p>
            </div>
        </template>

        <template #content>
            <div class="container overflow transition-all duration-300 ease-in-out mb-1">
                <div v-if="wells.length !== 0" class="mb-3">
                    <DataTable
                        sortField="wellRank"
                        :sortOrder="1"
                        :value="wells"
                        lazy
                        paginator
                        :totalRecords="totalRecords"
                        :loading="parentLoading"
                        @page="$emit('page', $event, project?.id)"
                        @sort="$emit('sort', $event, project?.id)"
                        :rows="rows"
                        size="small"
                        showGridlines
                        :row-class="rowClass"
                        :pt="{
                            root: { class: sideBySide ? 'text-sm' : '' },
                            headerRow: { class: 'bg-primary' },
                            thead: { class: 'bg-primary' },
                            column: { class: 'bg-primary-500' },
                            tableContainer: { class: 'rounded-t-lg' }
                        }"
                    >
                        <PColumn
                            label="Toggle"
                            :pt="{
                                headerCell: { class: 'bg-primary border-l-0' },
                                headerTitle: { class: 'text-slate-50 text-sm' }
                            }"
                        >
                            <template #body="slotProps">
                                <i
                                    v-if="!wasWellRemoved(slotProps.data) && !projectDisabled"
                                    class="pi pi-minus-circle text-red-500 cursor-pointer"
                                    @click="$emit('remove-well', slotProps.data, project?.id)"
                                >
                                </i>
                                <!-- For now, disabling added a project back when the entire project is disabled. -->
                                <span
                                    v-else-if="
                                        slotProps.data.projects?.some((p: ScenarioProject) => p.id === project?.id) &&
                                        !projectDisabled
                                    "
                                >
                                    <i
                                        v-if="readdEnabled(slotProps.data)"
                                        class="pi pi-plus-circle text-secondary cursor-pointer"
                                        @click="$emit('readd-well', slotProps.data, project?.id)"
                                    ></i>
                                    <i v-else class="pi pi-plus-circle text-gray-400"></i>
                                </span>
                            </template>
                        </PColumn>
                        <PColumn
                            :pt="{
                                headerCell: { class: 'bg-primary' },
                                sort: { class: 'bg-primary' },
                                headerTitle: { class: 'text-slate-50 text-sm' },
                                sortIcon: { class: 'text-slate-50' }
                            }"
                            :header="scenarioDetailsKeyLabelMap['wellRank']"
                            :sortable="true"
                            :field="'wellRank'"
                        >
                            <template #body="slotProps">
                                <div class="text-black font-bold">
                                    {{ slotProps.data.wellRank }}
                                </div>
                            </template>
                        </PColumn>
                        <PColumn
                            label="Map"
                            :pt="{
                                headerCell: { class: 'bg-primary border-l-0' },
                                headerTitle: { class: 'text-slate-50 text-sm' }
                            }"
                        >
                            <template #body="slotProps">
                                <i
                                    class="pi pi-map text-secondary cursor-pointer"
                                    @click="$emit('navigate', slotProps.data)"
                                >
                                </i>
                            </template>
                        </PColumn>
                        <PColumn
                            v-for="column in columns"
                            :field="column"
                            :header="scenarioDetailsKeyLabelMap[column]"
                            :sortable="true"
                            :key="column"
                            :pt="{
                                headerCell: { class: 'bg-primary border-l-0' },
                                headerTitle: {
                                    class: 'text-slate-50 w-auto whitespace-nowrap overflow-visible text-sm'
                                },
                                sortIcon: { class: 'text-slate-50' }
                            }"
                        >
                            <template #body="slotProps">
                                <span v-if="column == 'priorityScore'">
                                    {{ slotProps.data[column] ? slotProps.data[column].toFixed(2) : '' }}
                                </span>
                                <span v-else>{{ slotProps.data[column] }}</span>
                            </template>
                        </PColumn>
                    </DataTable>
                    <div class="flex flex-row justify-between" :class="{ 'flex-col text-sm': sideBySide }">
                        <PButton
                            class="border border-red-500"
                            :class="{ 'w-1/3 p-2 text-sm': sideBySide }"
                            @click="$emit('toggle-project', project?.id)"
                            severity="danger"
                            outlined
                            v-if="!projectDisabled"
                        >
                            <span class="pi pi-minus-circle" />
                            <span class="ml-2">Remove Project</span>
                        </PButton>
                        <PButton
                            class="border border-secondary text-white btn-secondary"
                            @click="$emit('toggle-project', project?.id)"
                            severity="secondary"
                            v-else
                        >
                            <span class="pi pi-plus-circle" />
                            <span class="ml-2">Re-add Project</span>
                        </PButton>
                        <div class="flex items-center" :class="{ 'text-sm pt-4': sideBySide }">
                            <span :class="{ 'mr-2': sideBySide }">Add Well to Project:</span>
                            <MultiSelect
                                ref="multiSelect"
                                class="ml-4 w-52"
                                :class="{ 'ml-0 text-sm': sideBySide }"
                                id="wellSelect"
                                appendTo="self"
                                :maxSelectedLabels="1"
                                filter
                                @filter="onFilter"
                                name="wellSelect"
                                v-model="selectedWells"
                                :options="searchableWells"
                                optionLabel="wellId"
                                placeholder="Select Well"
                                :loading="false"
                                :disabled="projectDisabled"
                            ></MultiSelect>
                            <PButton
                                severity="primary"
                                label="Update"
                                class="btn-primary ml-4 h-full"
                                :class="{ 'text-sm': sideBySide }"
                                @click="addSelectedWells"
                                :disabled="projectDisabled"
                            />
                        </div>
                    </div>
                </div>
            </div>
        </template>
    </PCard>
</template>
