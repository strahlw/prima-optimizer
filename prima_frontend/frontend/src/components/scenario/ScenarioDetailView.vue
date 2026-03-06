<script setup lang="ts">
    import { ref, onMounted, watch, computed } from 'vue';
    import { type DataTablePageEvent, type DataTableSortEvent } from 'primevue/datatable';
    import ScenarioCopyAndEditDialog from '@/components/scenario/ScenarioCopyAndEditDialog.vue';
    import RankOnlyMessage from '@/components/scenario/RankOnlyMessage.vue';
    import Dialog from 'primevue/dialog';
    import IconCustomScenario from '../icons/IconCustomScenario.vue';
    import OverrideProjectTable from './override/OverrideProjectTable.vue';
    import { createScenarioService } from '@/services/scenarioService';
    import { createApiService } from '@/services/apiService';
    import { useCollapse } from '@/composables/collapse';
    import { createToastService } from '@/services/toastService';
    import { setupDatatablePaginationHelper } from '@/utils/datatablePaginationHelper';
    import { useScenarioActions } from '@/composables/useScenarioActions';

    import type { MinimalDetailsProject } from '@/types/projects';
    import type { MinimalDetailsScenario, OverrideData } from '@/types/scenario';
    import type { Well } from '@/types/well';

    const scenarioService = createScenarioService();
    const apiService = createApiService();
    const emit = defineEmits(['changeTab', 'displayOverrides', 'overrideActive', 'overrideInactive']);
    const { toastError } = createToastService();
    const { enter, leave } = useCollapse();
    const { first, loading, lazyParams, onPage, onSort } = setupDatatablePaginationHelper(loadLazyData);

    const collapsed = ref(true);
    const saving = ref<boolean>(false);
    const totalRecords = ref<Record<number, number>>({});
    const tableData = ref<Record<number, Well[]>>({});

    const props = defineProps({
        scenario: {
            type: Object as () => MinimalDetailsScenario,
            required: false
        },
        visibleProjects: {
            required: false,
            type: Array as () => MinimalDetailsProject[],
            default: () => []
        },
        scenarioScreenLoading: {
            required: false,
            type: Boolean,
            default: false
        },
        initialScenarioData: {
            type: Object as () => Record<number, { total: number; data: Well[] }> | null,
            default: () => null
        },
        postInitialLoad: {
            required: false,
            type: Boolean,
            default: false
        },
        sideBySide: {
            required: false,
            type: Boolean,
            default: false
        }
    });

    /**************************** Start override-specific items ************************************/
    const saveDialogVisible = ref<boolean>(false);
    const currentProjectSearched = ref<number>(0);
    const searchableWells = ref<Well[]>([]);
    const wellsJustAdded = ref<Well[]>([]); // Used to eliminate recently added wells from other projects that have them selected in the multi-select
    const overrideData = ref<OverrideData>({
        name: '',
        projectsRemove: [],
        wellsRemove: {},
        projectsLock: [],
        wellsLock: {},
        wellsReassignFrom: [],
        wellsReassignTo: {},
        newWellAdditions: []
    });

    watch(
        overrideData,
        (newVal) => {
            if (
                newVal.projectsRemove.length ||
                Object.entries(newVal.wellsRemove).length ||
                newVal.projectsLock.length ||
                Object.entries(newVal.wellsLock).length ||
                newVal.wellsReassignFrom.length ||
                Object.entries(newVal.wellsReassignTo).length ||
                newVal.newWellAdditions.length
            ) {
                emit('overrideActive');
            } else {
                emit('overrideInactive');
            }
        },
        { deep: true }
    );

    onMounted(async () => {
        if (props.postInitialLoad) {
            // Perform initial loading of scenario
            const scenarioId = props.scenario?.id;
            if (!scenarioId) return;
            const requestObj = { [scenarioId]: props.visibleProjects?.map((project) => project.id) };
            const result = await scenarioService.getInitialVisibleScenarioWells(requestObj);
            parseScenarioLevelDataToTable(result[scenarioId]);
            toggleCollapse();
        }
    });

    const wellPool = computed(() => {
        // Extract well IDs from wellsReassignTo
        const wellsToRemove = Object.values(overrideData.value.wellsReassignTo).flatMap((wells) =>
            wells.map((well: Well) => well.wellId)
        );

        // Flatten the wells from wellsRemove and filter out the wells that are being reassigned
        return Object.values(overrideData.value.wellsRemove)
            .flatMap((wells) => wells.map((well: Well) => well.wellId))
            .filter((wellId) => !wellsToRemove.includes(wellId)); // Exclude reassigned wells
    });

    // All well ids that have been reassigned to a new project, religns on wells being added to this once they are added to a different project
    const reassignedWellsPool = computed(() => {
        return Object.values(overrideData.value.wellsReassignTo).flatMap((wells) =>
            wells.map((well: Well) => well.wellId)
        );
    });

    function removeWell(well: Well, projectId: number) {
        if (well.projects && well.projects.some((p) => p.id === projectId)) {
            const projectWellMap = overrideData.value.wellsRemove[projectId] || [];
            overrideData.value.wellsRemove = {
                ...overrideData.value.wellsRemove,
                [projectId]: [...projectWellMap, well]
            };
        } else {
            // Remove a well that was added to a project from the overall dataset
            const projectWellMap = overrideData.value.wellsReassignTo[projectId] || [];
            overrideData.value.wellsReassignTo = {
                ...overrideData.value.wellsReassignTo,
                [projectId]: [...projectWellMap.filter((w: Well) => w.wellId !== well.wellId)]
            };

            overrideData.value.wellsReassignFrom = [
                ...overrideData.value.wellsReassignFrom.filter((w: Well) => w.wellId !== well.wellId)
            ];

            overrideData.value.newWellAdditions = overrideData.value.newWellAdditions.filter(
                (id) => id !== well.wellId
            );

            tableData.value[projectId] = tableData.value[projectId].filter((w: Well) => w.wellId !== well.wellId);
        }
    }

    function readdWell(well: Well, projectId: number) {
        const projectWellMap = overrideData.value.wellsRemove[projectId] || [];
        overrideData.value.wellsRemove = {
            ...overrideData.value.wellsRemove,
            [projectId]: projectWellMap.filter((w: Well) => w.wellId !== well.wellId)
        };
        if (overrideData.value.wellsRemove[projectId].length === 0) {
            delete overrideData.value.wellsRemove[projectId];
        }
        wellsJustAdded.value = [well];
    }

    function addWells(wells: Well[], projectId: number) {
        const projectWellMap = overrideData.value.wellsReassignTo[projectId] || [];
        const nonSameProjectWells = wells.filter(
            (well: Well) => !well.projects || well.projects?.some((p) => p.id !== projectId)
        );
        const sameProjectWells = wells.filter((well: Well) => well.projects?.some((p) => p.id === projectId));

        overrideData.value.wellsReassignFrom = [
            ...overrideData.value.wellsReassignFrom,
            ...nonSameProjectWells.filter(function (well: Well) {
                // Verify
                return 'projects' in well && well.projects?.length;
            })
        ];

        overrideData.value.newWellAdditions = [
            ...overrideData.value.newWellAdditions,
            ...nonSameProjectWells
                .filter(function (well: Well) {
                    // Verify
                    return !('projects' in well) || !well.projects?.filter((p) => p.id === projectId).length;
                })
                .map((well) => well.wellId)
        ];

        overrideData.value.wellsReassignTo = {
            ...overrideData.value.wellsReassignTo,
            [projectId]: [...projectWellMap, ...nonSameProjectWells.map((well) => well)]
        };

        // Handle wells that may be added back to the project via the update button
        if (sameProjectWells.length > 0) {
            sameProjectWells.forEach((well: Well) => readdWell(well, projectId));
            // overrideData.value.wellsRemove = {
            //     ...overrideData.value.wellsRemove,
            //     [projectId]: overrideData.value.wellsRemove[projectId].filter(
            //         (w: Well) => !sameProjectWells.some((well) => well.wellId === w.wellId)
            //     )
            // };
        }

        tableData.value[projectId] = [...nonSameProjectWells, ...tableData.value[projectId]];

        searchableWells.value = [];
        // Fire off the pseudo-event prop to remove any of the wells just added from other projects selections
        wellsJustAdded.value = wells;
    }

    async function createNewScenario() {
        saveDialogVisible.value = false;

        if (props.scenario) {
            saving.value = true;
            let timeoutId;

            try {
                // The timeout should align with the time limit
                const timeoutPromise = new Promise(
                    (_, reject) =>
                        (timeoutId = setTimeout(() => {
                            toastError(
                                'The request took too long to process. Please try again or contact an administrator.'
                            );
                            reject(new Error('Request timed out after 60 seconds'));
                        }, 60000))
                );

                const response = await Promise.race([
                    scenarioService.saveScenarioOverride(props.scenario?.id, overrideData.value),
                    timeoutPromise
                ]);

                saving.value = false;

                clearTimeout(timeoutId);

                if (response.scenarioId) {
                    emit('displayOverrides', response.scenarioId);
                }
            } catch (error) {
                console.error('Error saving scenario override', error);
                saving.value = false;

                clearTimeout(timeoutId);
            }
        }
    }

    function getProjectWellMixture(projectId: number, wells: Well[]) {
        if (!overrideData.value.wellsReassignTo[projectId] || !overrideData.value.wellsReassignTo[projectId].length) {
            return wells;
        }

        const newDatasetJsons = overrideData.value.wellsReassignTo[projectId].filter(function (oW) {
            return oW.dataset_id && !oW.projects;
        });

        return [...newDatasetJsons, ...wells];
    }

    const onSearch = async (event: any, projectId: number) => {
        const searchQuery = event;
        if (!event) return;
        currentProjectSearched.value = projectId;
        const inactiveProjectIds = overrideData.value.projectsRemove;

        try {
            const response = await apiService.post(`api/scenario/wells/${props.scenario?.id}/search`, {
                includedWellIds: wellPool.value || [],
                inactiveProjectIds: inactiveProjectIds || [],
                excludedDatasetWellIds: overrideData.value.newWellAdditions || [],
                reassignedWellIds: reassignedWellsPool.value || [],
                wellTypes: props.scenario?.wellTypes || [],
                query: searchQuery,
                page: 1
            });

            searchableWells.value = response.data;
        } catch (error) {
            console.error('Error searching for wells', error);
        }
    };

    const toggleProject = (projectId: number) => {
        if (overrideData.value.projectsRemove.includes(projectId)) {
            // Add the project back
            overrideData.value.projectsRemove = overrideData.value.projectsRemove.filter((id) => id !== projectId);

            // Check if the well has since been added to another project
            const wellsReassignedSinceRemoval = overrideData.value.wellsReassignFrom.filter((well: Well) =>
                well.projects?.some((p) => p.id === projectId)
            );

            if (wellsReassignedSinceRemoval.length) {
                overrideData.value.wellsRemove = {
                    ...overrideData.value.wellsRemove,
                    [projectId]: [...wellsReassignedSinceRemoval]
                };
            }
        } else {
            // Remove the project
            // Discard any wells/datasets that were added to the project
            overrideData.value.projectsRemove = [...overrideData.value.projectsRemove, projectId];
            const newProjectWells = overrideData.value.wellsReassignTo[projectId] || [];
            if (newProjectWells.length) {
                overrideData.value.newWellAdditions = overrideData.value.newWellAdditions.filter(
                    (id) => !newProjectWells.map((well) => well.wellId).includes(id)
                );

                delete overrideData.value.wellsReassignTo[projectId];
                overrideData.value.wellsReassignTo = { ...overrideData.value.wellsReassignTo };

                const wellsToKeep = overrideData.value.wellsReassignFrom.filter(function (w: Well) {
                    return w.projects?.some((p) => p.id === projectId);
                });
                overrideData.value.wellsReassignFrom = [...wellsToKeep];
            }
        }
    };

    function debounce(fn: any, delay: number) {
        let timeout: ReturnType<typeof setTimeout>;
        return function (...args: any[]) {
            clearTimeout(timeout);
            timeout = setTimeout(() => fn.apply(null, args), delay);
        };
    }

    // Debounced search function
    const debouncedSearch = debounce(onSearch, 300);

    // Event handler for child's emitted event
    function handleSearchQuery(query: string, projectId: number) {
        debouncedSearch(query, projectId);
    }

    /**************************** End override-specific items **************************************/

    const loadingNewProject = ref<boolean>(false);

    function projectIsVisible(projectId: number): MinimalDetailsProject | null {
        const p = props.visibleProjects.find((project: MinimalDetailsProject) => project.id == projectId) || null;
        return p;
    }

    function navigateToWell(rowData: Well) {
        emit('changeTab', rowData);
    }

    function toggleCollapse() {
        collapsed.value = !collapsed.value;
    }

    function parseScenarioLevelDataToTable(scenarioData: Record<number, { total: number; data: Well[] } | null>) {
        if (!scenarioData) return;
        Object.entries(scenarioData).forEach(([projectId, res]) => {
            if (!res) return;
            if ('total' in res) {
                totalRecords.value[Number(projectId)] = res.total;
            }

            if ('data' in res) {
                tableData.value[Number(projectId)] = res.data;
            }
        });
    }

    watch(
        () => props.visibleProjects,
        async (newVal: MinimalDetailsProject[], oldVal) => {
            loadingNewProject.value = true;
            // Find the project id that wasn't previously present
            const newProjectId = newVal.find((project) => !oldVal.some((p) => p.id === project.id))?.id;
            if (newProjectId) {
                toggleCollapse();
                loadingNewProject.value = true;
                loadLazyData(undefined, newProjectId);
            } else {
                loadingNewProject.value = false;
            }
        }
    );

    watch(
        () => props.initialScenarioData,
        () => {
            if (!props.scenarioScreenLoading && props.initialScenarioData) {
                parseScenarioLevelDataToTable(props.initialScenarioData);
                toggleCollapse();
            }
        }
    );

    watch(
        () => loading.value,
        (newVal) => {
            if (!newVal && collapsed.value) {
                toggleCollapse();
            }
        }
    );

    function loadLazyData(event?: DataTablePageEvent | DataTableSortEvent, projectId?: number) {
        loading.value = true;
        let activeRequests = 0;
        lazyParams.value = {
            ...lazyParams.value,
            addedWellIds: projectId
                ? overrideData.value.wellsReassignTo[projectId]
                      ?.filter((well) => 'projects' in well)
                      .map((well) => well.wellId) || []
                : [],
            addedDatasetWellIds: projectId
                ? overrideData.value.wellsReassignTo[projectId]
                      ?.filter((well) => !('projects' in well) || !well.projects?.length)
                      .map((well) => well.wellId) || []
                : [],
            first: event?.first || first.value
        };

        if (projectId) {
            activeRequests += 1;
            setTimeout(
                () => {
                    scenarioService
                        .getProjectWells(lazyParams.value, projectId)
                        .then((res) => {
                            const intProjectId =
                                props.visibleProjects.find((project: MinimalDetailsProject) => project.id === projectId)
                                    ?.id || projectId;
                            totalRecords.value[intProjectId] = res.total;
                            tableData.value[intProjectId] = res.data;
                            searchableWells.value = [...res.data];
                        })
                        .finally(() => {
                            activeRequests -= 1;
                            if (activeRequests === 0) loading.value = false;
                        });
                },
                Math.random() * 1000 + 250
            );
        } else {
            props.visibleProjects.forEach((project: MinimalDetailsProject) => {
                activeRequests += 1;
                setTimeout(
                    () => {
                        scenarioService
                            .getProjectWells(lazyParams.value, project.id)
                            .then((res) => {
                                totalRecords.value[project.id] = res.total;
                                tableData.value[project.id] = res.data;
                            })
                            .finally(() => {
                                activeRequests -= 1;
                                if (activeRequests === 0) loading.value = false;
                            });
                    },
                    Math.random() * 1000 + 250
                );
            });
        }
    }

    const { scenarioToBeCopied, handleScenarioCopy, scenarioCopyVisible, handleCopyAndEditClick } =
        useScenarioActions();
</script>
<template>
    <span>
        <ScenarioCopyAndEditDialog
            v-model:scenarioCopyVisible="scenarioCopyVisible"
            v-model:scenarioToBeCopied="scenarioToBeCopied"
            :handleScenarioCopy="handleScenarioCopy"
        />
        <div v-if="scenario" class="overflow-visible scenario-detail-view mb-4 p-4 rounded-lg max-w-full bg-white">
            <div class="flex">
                <Dialog
                    v-model:visible="saveDialogVisible"
                    modal
                    header="Confirm Scenario Override"
                    :style="{ width: '25rem' }"
                >
                    <span class="p-text-secondary block mb-5">Provide your new Scenario with a name to proceed.</span>
                    <div class="flex-auto">
                        <InputText id="name" v-model="overrideData.name" placeholder="Scenario Name" />
                    </div>

                    <br />

                    <div class="flex justify-end gap-2 w-100">
                        <PButton type="button" severity="secondary" @click="saveDialogVisible = false">Cancel</PButton>
                        <PButton type="button" @click="createNewScenario" :disabled="!overrideData.name">Save</PButton>
                    </div>
                </Dialog>
                <Dialog
                    v-model:visible="saving"
                    modal
                    :pt="{
                        root: 'border-none',
                        mask: {
                            style: 'backdrop-filter: blur(2px)'
                        }
                    }"
                    ><template #container>
                        <div class="flex flex-col px-5 pb-5 bg-white max-w-lg">
                            <h2>Override Submitting...</h2>
                            <p>
                                Submitting the override may take a minute. Please stay on this page. This modal will
                                close when the submission has completed.
                            </p>
                            <ProgressSpinner /></div></template
                ></Dialog>
            </div>
            <div
                class="flex flex-col py-0 h-auto relative mb-2"
                :class="!loading && !scenarioScreenLoading ? 'cursor-pointer' : ''"
                @click="loading || scenarioScreenLoading ? '' : toggleCollapse()"
            >
                <div
                    v-if="loading || scenarioScreenLoading"
                    class="absolute inset-0 flex items-center justify-center bg-white bg-opacity-75 rounded"
                >
                    <i class="pi pi-spin pi-spinner text-lg text-gray-500"></i>
                </div>
                <div class="grid grid-cols-3 gap-10 place-items-center text-xl">
                    <p class="justify-self-start text-sm" :class="{ 'text-xs': sideBySide }">
                        <span>Uploaded By: </span>
                        <br v-if="sideBySide" />
                        <span class="italic">{{ scenario.user.firstName }} {{ scenario.user.lastName }}</span>

                        <span v-if="scenario.parent?.data">
                            <br />
                            <span
                                >Child of:
                                <router-link
                                    :to="{ path: `/scenarios/${scenario.parent?.id}`, hash: '#projects' }"
                                    target="_blank"
                                    class="router-link"
                                    >{{ scenario.parent?.data.name }}</router-link
                                ></span
                            >
                        </span>

                        <span v-if="scenario.copyParent?.data">
                            <br />
                            <span
                                >Modified based on:
                                <router-link
                                    :to="{ path: `/scenarios/${scenario.copyParent?.id}`, hash: '#projects' }"
                                    target="_blank"
                                    class="router-link"
                                    >{{ scenario.copyParent?.data.name }}</router-link
                                ></span
                            >
                        </span>
                    </p>

                    <p class="font-bold text-xxl" :class="{ 'text-base': sideBySide }">{{ scenario.data.name }}</p>
                    <div class="justify-self-end items-center flex flex-row" v-if="!scenario.isRankOnly">
                        <PButton
                            class="btn-secondary mr-4"
                            :class="{ 'text-xs mr-2 p-1': sideBySide }"
                            @click.stop="saveDialogVisible = true"
                        >
                            <IconCustomScenario fillClass="fill-white" />
                            <span class="ml-2">Save New Scenario</span>
                        </PButton>
                        <i
                            class="justify-self-end mr-2"
                            :class="{
                                'pi pi-chevron-up': collapsed,
                                'pi pi-chevron-down': !collapsed,
                                'text-xs': sideBySide
                            }"
                        ></i>
                    </div>
                    <div class="justify-self-end items-center flex flex-row" v-if="scenario.isRankOnly">
                        <PButton
                            class="btn-secondary mr-4"
                            :class="{ 'text-xs mr-2 p-1': sideBySide }"
                            @click.stop="handleCopyAndEditClick(scenario.id)"
                        >
                            <span>Copy & Edit Scenario Inputs</span>
                        </PButton>
                    </div>
                </div>
                <div v-if="scenario.isRankOnly" class="w-full mt-6">
                    <RankOnlyMessage class="mx-auto" />
                </div>
            </div>
            <transition name="accordion" @enter="enter" @leave="leave">
                <div v-if="!collapsed">
                    <div v-for="project in visibleProjects" :key="project.id" class="mb-4">
                        <div v-if="projectIsVisible(project.id) && totalRecords[project.id]">
                            <OverrideProjectTable
                                :project="projectIsVisible(project.id)"
                                :searchableWells="searchableWells"
                                :wells="getProjectWellMixture(project.id, tableData[project.id] || [])"
                                :totalRecords="totalRecords[project.id]"
                                :parentLoading="loading"
                                @page="onPage"
                                @sort="onSort"
                                @navigate="navigateToWell"
                                @filter-query="handleSearchQuery"
                                @toggle-project="toggleProject"
                                @remove-well="removeWell"
                                @readd-well="readdWell"
                                @add-wells="addWells"
                                :wellsJustAdded="wellsJustAdded"
                                :removedWells="overrideData.wellsRemove[project.id] || []"
                                :reassignedWells="overrideData.wellsReassignFrom"
                                :removedProjectIds="overrideData.projectsRemove"
                                :sideBySide="sideBySide"
                                :rows="lazyParams.rows"
                            />
                        </div>
                    </div>
                </div>
            </transition>
        </div>
    </span>
</template>
<style scoped>
    .accordion-enter-active,
    .accordion-leave-active {
        transition: max-height 0.5s ease-in-out;
    }
    .accordion-enter,
    .accordion-leave-to {
        max-height: 0;
    }
</style>
