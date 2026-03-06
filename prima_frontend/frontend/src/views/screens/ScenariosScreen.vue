<script setup lang="ts">
    import { Divider, Tab, Tabs, TabList, TabPanels, TabPanel, type PageState } from 'primevue';
    import { ref, onMounted, computed, watch } from 'vue';
    import { useRoute, useRouter } from 'vue-router';
    import { setupScenarioScreenServices, setupScenarioScreenVars } from '@/utils/scenarioScreenHelpers';
    const { scenarioService, apiService, toastService, scenarioStore, organizationStore, wellOverviewStore } =
        setupScenarioScreenServices();

    import KPISummary from '../scenario/KPISummary.vue';
    import ProjectSidebar from '@/components/projects/ProjectSidebar.vue';
    import ProjectMap from '@/components/maps/ProjectMap.vue';
    import ProjectDetails from '@/components/projects/ProjectDetails.vue';
    import ScenarioParameters from '@/components/scenario/ScenarioParameters.vue';
    import WellRanking from '@/components/scenario/WellRanking.vue';

    import type { Organization } from '@/types/organization';

    import type { ScenarioProject } from '@/types/projects';
    import type { PublishedScenario } from '@/types/scenario';
    import type { Well } from '@/types/well';

    const route = useRoute();
    const router = useRouter();
    const {
        tabKeys,
        view,
        viewOptions,
        filters,
        filterOptions,
        activeTab,
        currentPage,
        rowsPerPage,
        paginationMeta,
        downloadTrigger,
        downloadProcessing,
        loading,
        initialLoadComplete,
        totalRecords,
        first
    } = setupScenarioScreenVars();

    const selectedOrg = ref<Organization | null>(null);
    const selectScenarioId = ref<number | null>(null);
    const visibleProjects = ref<ScenarioProject[]>([]);
    const visibleScenarios = ref<PublishedScenario[]>([]);
    const publishedScenarios = ref<PublishedScenario[]>([]);
    const overrideActive = ref<boolean>(false);
    const singleWell = ref<Well | null>(null);

    const loadScenarios = async (page: number = 1, perPage: number = 10) => {
        loading.value = true;
        try {
            const response = await scenarioService.getPublishedScenarios(
                page,
                perPage,
                selectedOrg.value?.id,
                filters.value,
                selectScenarioId.value ?? null
            );
            publishedScenarios.value = response.data;
            paginationMeta.value = response.meta;
            currentPage.value = response.meta.current_page;
            first.value = response.meta.from;
            scenarioStore.setPublishedScenarios(publishedScenarios.value);

            // Handle setting org center point for selected scenario
            const selectedScenario = publishedScenarios.value.find(
                (s: PublishedScenario) => s.id === selectScenarioId.value
            );
            if (selectedScenario) {
                const coord = organizationStore.getOrganizationCoordinates(selectedScenario.organizationId);
                if (coord) {
                    wellOverviewStore.setOrgCoordinates({
                        latitude: coord[0],
                        longitude: coord[1]
                    });
                }
                selectScenarioId.value = null; // This only needs to be set once
            }
        } catch {
            toastService.toastError('Failed to load scenarios');
            console.error('Failed to load scenarios');
        } finally {
            loading.value = false;
        }
    };

    const onPageChange = (event: PageState) => {
        currentPage.value = event.page + 1; // PrimeVue Paginator is 0-indexed
        first.value = event.first;
        loadScenarios(currentPage.value, rowsPerPage.value);
    };

    const onRowsChange = (event: any) => {
        rowsPerPage.value = event.rows;
        currentPage.value = 1;
        loadScenarios(currentPage.value, rowsPerPage.value);
    };

    const onFilterChange = () => {
        currentPage.value = 1;
        loadScenarios(currentPage.value, rowsPerPage.value);
    };

    // TODO: Reassess all setting of active tab in conjunction with Phase 3 Task 2
    onMounted(async () => {
        const hash = route.hash.replace('#', '');
        const index = tabKeys.indexOf(hash);
        if (index !== -1) activeTab.value = index;

        const organizationId = route.params.organizationId as string;
        const scenarioId = route.params.scenarioId as string;
        if (scenarioId) {
            selectScenarioId.value = Number.parseInt(scenarioId);
        }

        if (organizationId) {
            selectedOrg.value =
                organizationStore.getOrganizations.find((org) => org.id === Number.parseInt(organizationId)) ?? null;

            const coord = organizationStore.getOrganizationCoordinates(Number.parseInt(organizationId));
            if (coord) {
                wellOverviewStore.setOrgCoordinates({
                    latitude: coord[0],
                    longitude: coord[1]
                });
            }

            await handleOrganizationSelected(Number.parseInt(organizationId));
        } else {
            await loadScenarios(currentPage.value, rowsPerPage.value);
        }

        initialLoadComplete.value = true;
    });

    watch(activeTab, (newIndex) => {
        const newHash = `#${tabKeys[newIndex]}`;
        if (route.hash !== newHash) {
            router.replace({ hash: newHash }); // Use replace to avoid pushing to history
        }
    });

    watch(selectedOrg, async (newOrg) => {
        if (!initialLoadComplete.value) return;
        visibleScenarios.value = [];
        visibleProjects.value = [];
        if (newOrg && selectedOrg.value) {
            await handleOrganizationSelected(selectedOrg.value.id);
        } else {
            selectedOrg.value = null;
            await loadScenarios(1, rowsPerPage.value);
        }
    });

    const detailsViewScenarios = computed(() => {
        const scenariosVisible = publishedScenarios.value.filter(
            (scenario) =>
                visibleScenarios.value.some((s: PublishedScenario) => s.id === scenario.id) ||
                visibleProjects.value.some((p: ScenarioProject) => p.scenarioId === scenario.id)
        );

        return formatScenariosForDetailsTable(scenariosVisible);
    });

    const displayOverrides = (scenarioId: number) => {
        router
            .push({
                name: 'scenarios',
                params: { scenarioId: scenarioId, organizationId: selectedOrg.value?.id ?? null },
                hash: '#recommendations'
            })
            .then(() => {
                window.location.reload();
            });
        return;
    };

    const getScenarioById = (id: number) => {
        return publishedScenarios.value.find((s) => s.id === id);
    };

    const allProjectsAreDeselected = (scenario: PublishedScenario) => {
        return !visibleProjects.value.some((p) => p.scenarioId === scenario.id);
    };

    const handleProjectToggled = (project: ScenarioProject, skipToggleScenario: boolean = false) => {
        const projectIndex = visibleProjects.value.findIndex((p) => p.id === project.id);

        // Remove the project if it's already active
        if (projectIndex !== -1) visibleProjects.value.splice(projectIndex, 1);

        const targetScenario = getScenarioById(project.scenarioId);
        if (!targetScenario) return;

        if (allProjectsAreDeselected(targetScenario)) {
            handleScenarioToggled(targetScenario, project);
            return;
        }

        const remainingUnselectedProjects = targetScenario.projects.filter(
            (p) =>
                p.id !== project.id && // Exclude the passed project
                !visibleProjects.value.some((ap) => ap.id === p.id || ap.scenarioId === p.scenarioId)
        );

        const activeContainsTargetProject = visibleProjects.value.some((p) => p.id === project.id);
        const scenarioProjectsActive = visibleProjects.value.filter((p) => p.scenarioId === targetScenario.id);

        if (scenarioProjectsActive.length === 0 && projectIndex !== -1) {
            handleScenarioToggled(targetScenario);
            return;
        }

        if (
            (remainingUnselectedProjects.length === targetScenario.projects.length ||
                (activeContainsTargetProject &&
                    visibleProjects.value.filter((p) => p.scenarioId === targetScenario.id).length === 1)) &&
            !skipToggleScenario
        ) {
            // If all projects are unselected, remove the scenario from visibleScenarios
            if (visibleScenarios.value.some((s) => s.id === targetScenario.id)) {
                handleScenarioToggled(targetScenario);
                return;
            }
        } else {
            if (projectIndex !== -1) return;
            if (visibleScenarios.value.some((s) => s.id === targetScenario.id)) {
                const targetProject = visibleScenarios.value
                    .find((s) => s.id === targetScenario.id)
                    ?.projects.find((p) => p.id === project.id);

                if (targetProject) {
                    const firstBiggerProjectIdIndex = visibleProjects.value
                        .filter((p) => p.scenarioId === targetScenario.id)
                        .findIndex((p) => p.id > project.id);
                    if (firstBiggerProjectIdIndex === -1) {
                        visibleProjects.value.push(targetProject);
                    } else {
                        visibleProjects.value.splice(firstBiggerProjectIdIndex, 0, targetProject);
                    }
                }
            } else {
                handleScenarioToggled(targetScenario, project);
            }
        }
    };

    const toggleScenarioLoaded = (
        scenario: PublishedScenario,
        first?: boolean,
        singleProjectToToggle?: ScenarioProject
    ) => {
        if (first) {
            visibleScenarios.value = [scenario];
        } else {
            visibleScenarios.value.push(scenario);
        }

        if (visibleScenarios.value.length === 2 && [0, 1, 3, 4].includes(activeTab.value)) {
            view.value = { name: 'sideBySide', label: 'Side-by-Side' };
        }

        if (!scenario) return;

        if (singleProjectToToggle) {
            const project = scenario.projects.find((p) => p.id === singleProjectToToggle.id);
            if (project) {
                visibleProjects.value.push(project);
            }
            loading.value = false;
            return;
        }

        for (const project of scenario.projects) {
            const projectExists = visibleProjects.value.some(
                (p) => p.id === project.id && p.scenarioId === scenario.id
            );
            if (!projectExists) {
                visibleProjects.value.push(project);
            }
        }

        loading.value = false;
    };

    const handleMapOnlyScenarioToggle = (
        scenario: PublishedScenario,
        scenarioIndex: number,
        singleProjectToToggle?: ScenarioProject
    ) => {
        if (scenarioIndex === -1) {
            // Only allow 2 scenarios to be active at a time
            if (visibleScenarios.value.length >= 2) {
                visibleScenarios.value[0].projects.forEach((project) => {
                    handleProjectToggled(project, true);
                });

                visibleScenarios.value.forEach((s) => {
                    s.projects.forEach((project) => {
                        handleProjectToggled(project, true);
                    });
                });

                apiService
                    .get(`api/scenario/projects/${scenario.id}`, { params: { mapOnly: true } })
                    .then((response) => {
                        toggleScenarioLoaded(response.data, true, singleProjectToToggle);
                    })
                    .catch((error) => {
                        loading.value = false;
                        toastService.toastError('Failed to load scenario projects');
                        console.error(error);
                    });
            } else {
                apiService
                    .get(`api/scenario/projects/${scenario.id}`, { params: { mapOnly: true } })
                    .then((response) => {
                        toggleScenarioLoaded(response.data, false, singleProjectToToggle);
                    })
                    .catch((error) => {
                        loading.value = false;
                        toastService.toastError('Failed to load scenario projects');
                        console.error(error);
                    });
            }
        } else {
            // Scenario is already in the array, remove it
            visibleScenarios.value.splice(scenarioIndex, 1);

            // Remove projects related to this scenario from visibleProjects
            visibleProjects.value = visibleProjects.value.filter((project) => project.scenarioId !== scenario.id);
            loading.value = false;
        }
    };

    const handleDataTableScenarioToggle = (
        scenario: PublishedScenario,
        scenarioIndex: number,
        singleProjectToToggle?: ScenarioProject
    ) => {
        if (scenarioIndex === -1) {
            // Only allow 2 scenarios to be active at a time
            if (visibleScenarios.value.length >= 2) {
                visibleScenarios.value[0].projects.forEach((project) => {
                    handleProjectToggled(project, true);
                });

                // TODO: Trim data down even further to include minimal data for loading
                apiService
                    .get(`api/scenario/projects/${scenario.id}`, { params: { mapOnly: true } })
                    .then((response) => {
                        toggleScenarioLoaded(response.data, true, singleProjectToToggle);
                    })
                    .catch((error) => {
                        loading.value = false;
                        toastService.toastError('Failed to load scenario projects');
                        console.error(error);
                    });
            } else {
                apiService
                    .get(`api/scenario/projects/${scenario.id}`, { params: { mapOnly: true } })
                    .then((response) => {
                        toggleScenarioLoaded(response.data, false, singleProjectToToggle);
                    })
                    .catch((error) => {
                        loading.value = false;
                        toastService.toastError('Failed to load scenario projects');
                        console.error(error);
                    });
            }
        } else {
            // Scenario is already in the array, remove it
            visibleScenarios.value.splice(scenarioIndex, 1);

            // Remove projects related to this scenario from visibleProjects
            visibleProjects.value = visibleProjects.value.filter((project) => project.scenarioId !== scenario.id);
            loading.value = false;
        }
    };

    const handleScenarioToggled = async (scenario: PublishedScenario, singleProjectToToggle?: ScenarioProject) => {
        const scenarioIndex = visibleScenarios.value.findIndex((s) => s.id === scenario.id);
        loading.value = true;
        const mapOnly = activeTab.value === 0;

        if (mapOnly) {
            handleMapOnlyScenarioToggle(scenario, scenarioIndex, singleProjectToToggle);
            return;
        } else {
            handleDataTableScenarioToggle(scenario, scenarioIndex, singleProjectToToggle);
            return;
        }
    };

    const handleOrganizationSelected = async (organizationId: number) => {
        await loadScenarios(1, rowsPerPage.value);
        const organization = organizationStore.getOrganizations.find((org) => org.id === organizationId);
        if (organization) {
            wellOverviewStore.setOrgName(organization.name);

            const coord = organizationStore.getOrganizationCoordinates(organizationId);
            if (coord) {
                wellOverviewStore.setOrgCoordinates({
                    latitude: coord[0],
                    longitude: coord[1]
                });
            }
        } else {
            console.error(`Organization with ID ${organizationId} not found`);
        }
    };

    const focusClickedWell = (rowData: Well) => {
        activeTab.value = 2;
        singleWell.value = rowData;
    };

    const triggerDownload = () => {
        const targetScenario = visibleScenarios.value[0];
        if (targetScenario.isRankOnly) {
            if (activeTab.value !== 1) {
                activeTab.value = 1;
            }
        } else {
            if (activeTab.value !== 2) {
                activeTab.value = 2;
            }
        }

        downloadProcessing.value = true;
        downloadTrigger.value++;
    };

    const triggerDownloadComplete = () => {
        setTimeout(() => {
            downloadProcessing.value = false;
            downloadTrigger.value = 0;
        }, 1000);
    };

    const formatScenariosForDetailsTable = (scenarios: PublishedScenario[]) => {
        return scenarios.map((scenario: PublishedScenario) => {
            return {
                id: scenario.id,
                user: scenario.user,
                name: scenario.data?.name || scenario.data?.generalSpecifications?.name || '',
                data: scenario.data,
                wellTypes: scenario.data.generalSpecifications?.wellType,
                parent: scenario.parent,
                copyParent: scenario.copyParent,
                isRankOnly: scenario.isRankOnly
            };
        });
    };

    const formatProjectForDetailsTable = (projects: ScenarioProject[]) => {
        return projects.map((project: ScenarioProject) => {
            return {
                id: project.id,
                projectId: project.id,
                scenarioId: project.scenarioId,
                impactScore: project.impactScore,
                efficiencyScore: project.efficiencyScore,
                parentProjectDifferentials: project.parentProjectDifferentials || {}
            };
        });
    };

    const handleScenarioRenamed = (scenarioId: number, newName: string) => {
        const scenario = publishedScenarios.value.find((s) => s.id === scenarioId);
        if (scenario) {
            scenario.data.name = newName;
            if (scenario.data.generalSpecifications) {
                scenario.data.generalSpecifications.name = newName;
            }
            scenarioStore.setPublishedScenarios(publishedScenarios.value);
        }

        const scenarioIndex = visibleScenarios.value.findIndex((s) => s.id === scenarioId);
        if (scenarioIndex !== -1) {
            const scenarioToUpdate = visibleScenarios.value[scenarioIndex];
            scenarioToUpdate.data.name = newName;
            if (scenarioToUpdate.data.generalSpecifications) {
                scenarioToUpdate.data.generalSpecifications.name = newName;
            }
            visibleScenarios.value.splice(scenarioIndex, 1, scenarioToUpdate);
        }
    };
</script>

<template>
    <div class="grid project-view h-full">
        <div class="w-[280px] h-full overflow-y-hidden">
            <ProjectSidebar
                v-model:view="view"
                v-model:selectedOrg="selectedOrg"
                v-model:filters="filters"
                @page-change="onPageChange"
                @rows-change="onRowsChange"
                @filter-change="onFilterChange"
                @project-toggled="handleProjectToggled"
                @scenario-toggled="handleScenarioToggled"
                @trigger-download="triggerDownload"
                :scenarios="scenarioStore.getPublishedScenarios"
                :visibleProjects="visibleProjects"
                :visibleScenarios="visibleScenarios"
                :total-records="totalRecords"
                :rows-per-page="rowsPerPage"
                :first="first"
                :reviewedScenarioId="route.params.scenarioId"
                :reviewedOrganizationId="route.params.organizationId"
                :organizations="organizationStore.getOrganizations"
                :viewOptions="viewOptions"
                :filterOptions="filterOptions"
                :download-processing="downloadProcessing"
                :loading="loading"
                :downloadDisabled="overrideActive"
            />
        </div>
        <Divider
            layout="vertical"
            class="outline-stone-300 outline-offset-[-0.50px] outline outline-1"
            pt:root:class="mx-0"
        />
        <div class="flex-1 h-full overflow-y-auto">
            <Tabs :value="`${activeTab}`" @update:value="activeTab = Number($event)" class="w-full">
                <TabList
                    class="flex-shrink-0"
                    :pt="{
                        activeBar: { class: 'bg-secondary border-b-4 border-secondary' },
                        tabList: { class: 'bg-bgDefault' }
                    }"
                >
                    <Tab value="0" :pt="{ root: { class: 'text-secondary-500 bg-bgDefault' } }">
                        <div :class="{ 'opacity-50': activeTab !== 0 }" class="flex items-center space-x-1">
                            <i class="p-2 pi pi-flag text-xl"></i>
                            <div class="text-black">KPI Summary</div>
                        </div>
                    </Tab>
                    <Tab value="1" :pt="{ root: { class: 'text-secondary-500 bg-bgDefault' } }">
                        <div :class="{ 'opacity-50': activeTab !== 1 }" class="flex items-center space-x-1">
                            <i class="p-2 pi pi-chart-scatter text-xl"></i>
                            <div class="text-black">Well Ranking</div>
                        </div>
                    </Tab>
                    <Tab value="2" :pt="{ root: { class: 'text-secondary-500 bg-bgDefault' } }">
                        <div :class="{ 'opacity-50': activeTab !== 2 }" class="flex items-center space-x-1">
                            <i class="p-2 pi pi-star-fill text-xl"></i>
                            <div class="text-black">P&A Project Recommendations</div>
                        </div>
                    </Tab>
                    <Tab value="3" :pt="{ root: { class: 'text-secondary-500 bg-bgDefault' } }"
                        ><div :class="{ 'opacity-50': activeTab !== 3 }" class="flex items-center space-x-1">
                            <i class="p-2 pi pi-search text-xl"></i>
                            <div class="text-black">P&A Project Details</div>
                        </div></Tab
                    >
                    <Tab value="4" :pt="{ root: { class: 'text-secondary-500 bg-bgDefault' } }"
                        ><div :class="{ 'opacity-50': activeTab !== 4 }" class="flex items-center space-x-1">
                            <i class="p-2 pi pi-sliders-h text-xl"></i>
                            <div class="text-black">Scenario Parameters</div>
                        </div></Tab
                    >
                </TabList>
                <TabPanels :pt="{ root: { class: 'bg-bgDefault' } }">
                    <TabPanel value="0">
                        <div class="h-full overflow-y-auto p-4" v-if="activeTab === 0">
                            <div v-if="visibleScenarios?.length === 0">
                                <h3>Choose a scenario to view KPI Summary</h3>
                            </div>
                            <div :class="view.name === 'sideBySide' ? 'grid grid-cols-2' : ''" v-else>
                                <template v-for="scenario of visibleScenarios" :key="scenario.id">
                                    <KPISummary
                                        class="m-3"
                                        :scenario="scenario"
                                        :scenarioScreenLoading="loading"
                                        :sideBySide="view.name === 'sideBySide'"
                                    />
                                </template>
                            </div>
                        </div>
                    </TabPanel>
                    <TabPanel
                        value="1"
                        class="h-full overflow-hidden"
                        :pt="{
                            headerAction: { class: 'text-secondary-500 bg-bgDefault' }
                        }"
                    >
                        <div class="h-full overflow-y-auto p-4" v-if="activeTab === 1">
                            <div v-if="visibleScenarios?.length === 0">
                                <h3>Choose a scenario to view parameters</h3>
                            </div>
                            <div :class="view.name === 'sideBySide' ? 'grid grid-cols-2' : ''" v-else>
                                <template v-for="scenario of visibleScenarios" :key="scenario.id">
                                    <WellRanking
                                        class="m-3"
                                        :scenario="scenario"
                                        :scenarioScreenLoading="loading"
                                        :triggerDownload="downloadTrigger"
                                        @download-complete="triggerDownloadComplete"
                                    />
                                </template>
                            </div></div
                    ></TabPanel>
                    <TabPanel value="2">
                        <template v-slot:default>
                            <keep-alive>
                                <div
                                    class="p-col-12 grid"
                                    :class="view.name === 'overlay' ? '' : 'grid grid-cols-2'"
                                    v-if="activeTab === 2"
                                >
                                    <template v-if="view.name === 'overlay'">
                                        <div class="ml-2 mt-2 mb-2 min-w-[200px] flex flex-grow">
                                            <ProjectMap
                                                :activeTab="activeTab"
                                                :visibleProjects="visibleProjects"
                                                :visibleScenarios="visibleScenarios"
                                                :mapKey="0"
                                                :singleWell="singleWell"
                                                :triggerDownload="downloadTrigger"
                                                @download-complete="triggerDownloadComplete"
                                                :loading="loading"
                                            /></div
                                    ></template>

                                    <template v-if="view.name === 'sideBySide'">
                                        <div
                                            class="ml-2 mt-2 mb-2"
                                            v-for="scenario in visibleScenarios"
                                            :key="scenario.id"
                                        >
                                            <ProjectMap
                                                :activeTab="activeTab"
                                                :visibleProjects="
                                                    visibleProjects.filter(
                                                        (p: ScenarioProject) => p.scenarioId === scenario.id
                                                    )
                                                "
                                                :visibleScenarios="visibleScenarios"
                                                :scenario="scenario"
                                                :mapKey="scenario.id"
                                                :singleWell="singleWell"
                                                :loading="loading"
                                            />
                                            <h2 class="font-bold text-center">{{ scenario.data.name }}</h2>
                                        </div>
                                    </template>
                                </div>
                            </keep-alive>
                        </template>
                    </TabPanel>
                    <TabPanel
                        value="3"
                        :pt="{
                            headerAction: { class: 'text-secondary-500 bg-bgDefault' }
                        }"
                    >
                        <div class="p-col-12" v-if="activeTab === 3">
                            <div class="m-2">
                                <ProjectDetails
                                    :scenarios="detailsViewScenarios"
                                    :visibleProjects="formatProjectForDetailsTable(visibleProjects)"
                                    :sideBySide="view.name === 'sideBySide'"
                                    :scenarioScreenLoading="loading"
                                    @change-tab="focusClickedWell"
                                    @display-overrides="displayOverrides"
                                    @overrideActive="overrideActive = true"
                                    @overrideInactive="overrideActive = false"
                                />
                            </div></div
                    ></TabPanel>
                    <TabPanel
                        value="4"
                        :pt="{
                            headerAction: { class: 'text-secondary-500 bg-bgDefault' }
                        }"
                    >
                        <div class="p-col-12" v-if="activeTab === 4">
                            <div v-if="visibleScenarios?.length === 0" class="m-2">
                                <h3>Choose a scenario to view parameters</h3>
                            </div>
                            <div class="container" :class="view.name === 'sideBySide' ? 'grid grid-cols-2' : ''" v-else>
                                <template v-for="scenario of visibleScenarios" :key="scenario.id">
                                    <ScenarioParameters
                                        class="m-3"
                                        :scenario="scenario"
                                        :scenarioScreenLoading="loading"
                                        :sideBySide="view.name === 'sideBySide'"
                                        @scenarioRenamed="handleScenarioRenamed"
                                    />
                                </template>
                            </div></div
                    ></TabPanel>
                </TabPanels>
            </Tabs>
        </div>
    </div>
</template>

<style scoped>
    .project-view {
        grid-template-columns: 280px auto 1fr;
        height: calc(100vh - var(--navbar-height)); /* Adjust based on your navbar height */
    }
</style>
