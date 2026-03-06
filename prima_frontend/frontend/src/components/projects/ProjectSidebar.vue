<script setup lang="ts">
    import { ref, watch, computed, type PropType, onMounted, onUnmounted } from 'vue';

    import { MultiSelect, Divider, ScrollPanel, Paginator, type PageState } from 'primevue';
    import TypePill from '@/components/scenario/TypePill.vue';

    import { ScenarioType, ScenarioFormTitle } from '@/constants/scenarioEnums';
    import { useAuthStore } from '@/stores/authStore';
    import type { Organization } from '@/types/organization';
    import type { ScenarioProject } from '@/types/projects';
    import type { PublishedScenario } from '@/types/scenario';
    import { formatDate } from '@/utils/formatDate';

    const props = defineProps({
        scenarios: {
            type: Array as () => PublishedScenario[],
            default: () => []
        },
        totalRecords: {
            type: Number,
            default: 0
        },
        rowsPerPage: {
            type: Number,
            default: 10
        },
        first: {
            type: Number,
            default: 0
        },
        visibleProjects: {
            type: Array as () => ScenarioProject[],
            default: () => []
        },
        visibleScenarios: {
            type: Array as () => PublishedScenario[],
            default: () => []
        },
        reviewedScenarioId: {
            required: false,
            type: [String, Array] as PropType<string | string[]>,
            default: null
        },
        reviewedOrganizationId: {
            required: false,
            type: [String, Array] as PropType<string | string[]>,
            default: null
        },
        viewOptions: {
            type: Array as () => { name: string; label: string }[],
            default: () => [
                { name: 'overlay', label: 'Overlay' },
                { name: 'sideBySide', label: 'Side-by-Side' }
            ]
        },
        filterOptions: {
            type: Array as () => { name: ScenarioFormTitle; label: ScenarioType }[],
            default: () => []
        },
        downloadProcessing: {
            type: Boolean,
            default: false
        },
        organizations: {
            type: Array as () => Organization[],
            default: () => []
        },
        loading: {
            type: Boolean,
            default: false
        },
        downloadDisabled: {
            type: Boolean,
            default: false
        }
    });

    const view = defineModel<{ name: string; label: string }>('view', { required: true });
    const filters = defineModel<ScenarioFormTitle[]>('filters', { required: false });
    const selectedOrg = defineModel<Organization | null>('selectedOrg');
    const authStore = useAuthStore();

    const initialToggleSatisfied = ref(false);

    const expandedScenario = ref<PublishedScenario | null>(null);
    const buttonTitle = computed(() => {
        return view?.value?.name !== 'overlay'
            ? 'Project Download only available in overlay view'
            : 'Download Projects';
    });
    const downloadDisabled = computed(() => {
        return (
            view?.value?.name !== 'overlay' ||
            props.downloadProcessing ||
            props.downloadDisabled ||
            props.visibleScenarios.length !== 1
        );
    });
    const buttonToolTip = computed(() => {
        return props.visibleScenarios.length > 1 ? 'Only 1 scenario may be enabled when downloading' : '';
    });

    const emit = defineEmits([
        'scenario-toggled',
        'project-toggled',
        'trigger-download',
        'page-change',
        'rows-change',
        'filter-change'
    ]);

    // Expand the Scenario drop-down
    const expandScenario = (scenario: PublishedScenario) => {
        expandedScenario.value = expandedScenario.value === scenario ? null : scenario;
    };

    const scenarioIsVisible = (scenario: PublishedScenario) => {
        return props.visibleScenarios.findIndex((s) => s.id === scenario.id) !== -1;
    };

    const projectVisible = (project: ScenarioProject) => {
        return props.visibleProjects.findIndex((p: ScenarioProject) => p.id === project.id) !== -1;
    };

    watch(props.visibleScenarios, () => {
        if (props.visibleScenarios.length !== 2) {
            view.value = { name: 'overlay', label: 'Overlay' };
        }
    });

    watch(
        () => props.scenarios,
        (newScenarios) => {
            if (newScenarios.length && !initialToggleSatisfied.value) {
                // TODO: Phase 2 - This is a temporary phase 1 measure, that should work in conjuction with the mapService in Phase 2.
                setTimeout(() => {
                    handleInitialSelection();
                }, 500);
            }
        },
        { deep: true }
    );

    const handleInitialSelection = () => {
        const scenarioId = Array.isArray(props.reviewedScenarioId)
            ? Number.parseInt(props.reviewedScenarioId[0])
            : Number.parseInt(props.reviewedScenarioId);
        if (
            props.reviewedScenarioId &&
            props.visibleScenarios.findIndex((s: PublishedScenario) => s.id === scenarioId) === -1 &&
            props.scenarios.length > 0 &&
            !initialToggleSatisfied.value
        ) {
            const scenario = props.scenarios?.find((s: PublishedScenario) => s.id === scenarioId);
            if (scenario) {
                initialToggleSatisfied.value = true;
                emit('scenario-toggled', scenario);

                if (props.reviewedOrganizationId) {
                    const orgId = Array.isArray(props.reviewedOrganizationId)
                        ? Number.parseInt(props.reviewedOrganizationId[0])
                        : Number.parseInt(props.reviewedOrganizationId);

                    const org = props.organizations.find((o: Organization) => o.id === orgId);

                    if (org) {
                        selectedOrg.value = org;
                    }
                }
                expandScenario(scenario);
            }
        }
    };

    onMounted(async () => {
        if (!props.reviewedOrganizationId && !props.reviewedScenarioId) {
            initialToggleSatisfied.value = true;
        }
    });

    onUnmounted(() => {
        if (authStore.isSuperAdmin) {
            selectedOrg.value = null;
        }
    });
</script>

<template>
    <div class="flex flex-col h-full top-16" id="scenario-sidebar-container">
        <div class="flex-shrink-0">
            <div class="mt-2">
                <label>View Type:</label>
                <PSelect
                    v-model="view.name"
                    :options="viewOptions"
                    optionLabel="label"
                    optionValue="name"
                    placeholder="Select a view"
                    class="sidebar-select"
                    :disabled="visibleScenarios.length !== 2"
                >
                    <template #option="slotProps">
                        <div class="flex items-center">
                            <div class="text-xs">{{ slotProps.option.label }}</div>
                        </div>
                    </template>
                </PSelect>
            </div>

            <div class="mt-2" v-if="authStore.isSuperAdmin">
                <label>Select Organization:</label>
                <PSelect
                    v-model="selectedOrg"
                    :options="organizations"
                    optionLabel="key"
                    placeholder="Select an Organization"
                    class="sidebar-select"
                    :disabled="!initialToggleSatisfied || loading"
                    ><template #option="slotProps">
                        <div class="flex items-center">
                            <div class="text-xs">{{ slotProps.option.key }}</div>
                        </div>
                    </template></PSelect
                >
            </div>

            <div class="mt-2">
                <label>Filter by Category:</label>
                <MultiSelect
                    v-model="filters"
                    display="chip"
                    optionLabel="label"
                    optionValue="name"
                    :options="filterOptions"
                    @change="emit('filter-change')"
                    placeholder="Select Categories"
                    class="sidebar-select text-[8px]"
                    pt:paChip:class="rounded-[30px] text-[8px]"
                    pt:pcHeaderCheckbox:class="h-2"
                >
                    <template #value="slotProps">
                        <div v-if="slotProps.value && slotProps.value.length" class="flex gap-1 max-w-[65px]">
                            <TypePill
                                :type="selectedType"
                                v-for="selectedType in slotProps.value"
                                :key="selectedType"
                            />
                        </div>
                        <div v-else><div class="text-xs">Select Categories</div></div>
                    </template>
                    <template #option="slotProps">
                        <TypePill :type="slotProps.option.label" class="h-2 p-2 brightness-125 max-w-[65px]" />
                    </template>
                </MultiSelect>
            </div>

            <div>
                <PButton
                    class="mt-3 text-xs justify-center rounded-[10px]"
                    v-tooltip="buttonToolTip"
                    icon="pi pi-download"
                    iconPos="right"
                    label="Download Results"
                    @click="() => emit('trigger-download')"
                    :disabled="downloadDisabled"
                    :title="buttonTitle"
                    :aria-label="buttonTitle"
                    :loading="downloadProcessing"
                    :class="downloadDisabled ? 'bg-gray-500 ' : 'bg-primary-500 hover:bg-primary-700'"
                    pt:root:class="py-4 h-4"
                    pt:label:class="font-bold"
                />
            </div>
        </div>

        <Divider class="outline-stone-300 outline-offset-[-0.50px] outline outline-1"></Divider>

        <div class="flex-1 min-h-0 !px-0">
            <ul class="list-none w-full organization-list-container h-full">
                <ScrollPanel class="h-full" :dt="{ bar: { background: '{primary.color}' } }" v-if="scenarios.length">
                    <li v-for="(scenario, index) in scenarios" :key="index" class="mr-2">
                        <div class="flex flex-row items-center justify-between px-4 h-4">
                            <PButton
                                :icon="scenarioIsVisible(scenario) ? 'pi pi-eye' : 'pi pi-eye-slash'"
                                iconPos="center"
                                pt:root:class="bg-transparent border-0 shadow-white"
                                :class="[scenarioIsVisible(scenario) ? 'text-primary' : 'text-zinc-300']"
                                class="w-3.5 h-3.5 border-none shadow-none"
                                pt:icon:class="text-[14px]"
                                aria-label="Toggle Scenario"
                                :disabled="!initialToggleSatisfied || loading"
                                @click="emit('scenario-toggled', scenario)"
                            />
                            <div
                                class="w-44 h-7 text-sm flex items-center cursor-pointer"
                                :class="expandedScenario === scenario ? 'font-bold' : 'font-normal'"
                                @click="expandScenario(scenario)"
                                aria-label="Toggle scenario dropdown"
                                v-tooltip.right="{
                                    value: scenario.name,
                                    pt: {
                                        text: '!bg-gray-200 !text-gray-900'
                                    }
                                }"
                            >
                                <span class="truncate">{{ scenario.name }}</span>
                            </div>
                            <i
                                class="w-3.5 h-3.5 pi pi-chevron-right text-stone-300 cursor-pointer left-[15px] text-sm"
                                v-show="expandedScenario !== scenario"
                                @click="expandScenario(scenario)"
                                aria-label="Toggle scenario dropdown"
                                :disabled="loading"
                            ></i>
                            <i
                                class="w-3.5 h-3.5 pi pi-chevron-down text-primary cursor-pointer left-[13.75px] text-sm"
                                v-show="expandedScenario === scenario"
                                @click="expandScenario(scenario)"
                                aria-label="Toggle scenario dropdown"
                                :disabled="loading"
                            ></i>
                        </div>
                        <div class="flex flex-row items-center justify-center px-4 w-65 mt-1">
                            <div class="w-48 pl-2 h-auto">
                                <TypePill
                                    v-for="(type, typeIndex) in scenario.types"
                                    :key="typeIndex"
                                    :type="typeof type === 'string' ? type : type.name"
                                    class="mr-1 text-[9px]"
                                />
                            </div>
                        </div>
                        <div v-show="expandedScenario === scenario" class="px-4 mb-2">
                            <div class="flex flex-col items-center justify-center">
                                <div class="w-48 text-xs text-neutral-800 pl-2 mt-2">
                                    <p class="w-52 truncate">
                                        {{ scenario.user.firstName }} {{ scenario.user.lastName }}
                                    </p>
                                    <p class="w-52 truncate">{{ scenario.user.email }}</p>
                                    <p>Created on: {{ formatDate(scenario.createdAt) }}</p>
                                </div>
                            </div>
                        </div>
                        <div class="w-full" v-if="scenario.projects.length > 0 && expandedScenario === scenario">
                            <PCard
                                v-for="(project, projectIndex) in scenario.projects"
                                :key="projectIndex"
                                pt:root:class="mb-1 rounded-[5px] shadow-[0px_4px_4px_0px_rgba(0,0,0,0.25)] h-7"
                                pt:body:class="h-7 p-2 flex flex-row items-center"
                                pt:content:class="w-full"
                                class="mx-4 h-7"
                            >
                                <template #content>
                                    <div class="flex flex-row items-center text-xs w-full">
                                        <PButton
                                            iconPos="center"
                                            :icon="projectVisible(project) ? 'pi pi-eye' : 'pi pi-eye-slash'"
                                            pt:root:class="bg-transparent border-0 shadow-white w-3.5 h-3.5"
                                            @click="emit('project-toggled', project)"
                                            :class="[projectVisible(project) ? ' text-primary ' : ' text-zinc-300']"
                                            class="mr-2"
                                            :disabled="loading"
                                            pt:icon:class="text-[14px]"
                                        />
                                        <div>Project {{ project.id }}</div>
                                        <div class="font-bold ml-auto">{{ project.wellCount ?? 0 }}</div>
                                    </div>
                                </template>
                            </PCard>
                        </div>
                        <Divider class="outline-stone-300 outline-offset-[-0.50px] outline outline-1"></Divider>
                    </li>
                </ScrollPanel>
            </ul>
        </div>
        <Paginator
            :template="{ default: 'FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink JumpToPageDropdown' }"
            pt:root:class="p-0 bg-transparent"
            :first="first"
            :pt="{
                paginatorContainer: { class: '!gap-[20px] py-4' },
                first: { class: 'h-[12px] w-[12px] min-w-[24px]' },
                firstIcon: { class: 'h-[12px] w-[12px] min-w-[24px]' },
                prev: { class: 'h-[12px] w-[12px] min-w-[24px]' },
                prevIcon: { class: 'h-[12px] w-[12px] min-w-[24px]' },
                pages: { class: 'text-xs px-0' },
                last: { class: 'h-[12px] w-[12px] min-w-[24px]' },
                lastIcon: { class: 'h-[12px] w-[12px] min-w-[24px]' },
                next: { class: 'h-[12px] w-[12px] min-w-[24px]' },
                nextIcon: { class: 'h-[12px] w-[12px] min-w-[24px]' },
                page: { class: 'min-w-[20px] h-[20px] text-black' },
                pagebutton: { class: 'w-[20px] h-[20px] text-black' },
                pcJumpToPageDropdown: {
                    root: {
                        class: 'text-xs rounded-[10px] w-[60px]'
                    },
                    input: {
                        class: 'text-xs h-2 bg-green-500'
                    },
                    dropdownIcon: {
                        class: 'text-xs h-3'
                    },
                    option: { class: 'text-xs' },
                    label: { class: 'text-xs' }
                }
            }"
            pt:firsticon:class="!text-green-500 font-bold bg-green-500"
            :rows="rowsPerPage"
            :total-records="totalRecords"
            @page="(event: PageState) => emit('page-change', event)"
        />
    </div>
</template>

<style scoped>
    .sidebarIcon {
        font-size: large;
    }

    .organization-list-container .p-button {
        border: none;
        box-shadow: none;
    }

    .p-paginator-selected {
        @apply !bg-primary-500;
    }
</style>
