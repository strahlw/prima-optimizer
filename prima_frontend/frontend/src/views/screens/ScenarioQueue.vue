<script setup lang="ts">
    import { ref, onMounted } from 'vue';
    import { useRouter } from 'vue-router';
    import { useConfirm } from 'primevue/useconfirm';
    import TypePill from '@/components/scenario/TypePill.vue';
    import IconRename from '@/components/icons/IconRename.vue';
    import OrganizationScenarioDropdown from '@/components/organizations/SelectOrganizationScenarios.vue';
    import ScenarioRenameDialog from '@/components/scenario/ScenarioRenameDialog.vue';
    import ScenarioCopyAndEditDialog from '@/components/scenario/ScenarioCopyAndEditDialog.vue';

    import { useScenarioActions } from '@/composables/useScenarioActions';
    import { scenarioTableColumns } from '@/constants/scenarioTableColumns';
    import { createScenarioService } from '@/services/scenarioService';
    import { useAuthStore } from '@/stores/authStore';
    import { useScenarioStore } from '@/stores/scenarioStore';
    import type { ApiScenarioType, Scenario, ScenarioTableColumn } from '@/types/scenario';

    const authStore = useAuthStore();
    const scenarioStore = useScenarioStore();
    const scenarioService = createScenarioService();
    const confirm = useConfirm();

    const isLoading = ref<boolean>(false);
    const scenarios = ref<Scenario[]>([]);
    const router = useRouter();
    const error = ref<string | null>(null);
    const role = authStore.role;

    const fetchScenarios = async () => {
        try {
            scenarios.value = await scenarioStore.fetchScenarios();
            if (scenarios.value) {
                scenarios.value = formatScenariosWithTypes(scenarios.value);
            }
        } catch (err: any) {
            error.value = err.message || 'An error occurred';
        }
    };

    onMounted(async () => {
        await fetchScenarios();
    });

    const rowClass = (data: any) => {
        return {
            'bg-gray-300 italic': data.status === 'Processing',
            'bg-gray-300': data.status === 'Killed' || data.deletedAt != null,
            'bg-red-100': data.status === 'Failure'
        };
    };

    const goToScenarioReview = async (scenario: Scenario) => {
        try {
            if (scenario.isRankOnly) {
                router.push({
                    name: 'scenarios',
                    params: { scenarioId: scenario.id, organizationId: scenario.organizationId },
                    hash: '#ranking'
                });
            } else {
                router.push({
                    name: 'scenarios',
                    params: { scenarioId: scenario.id, organizationId: scenario.organizationId },
                    hash: '#recommendations'
                });
            }
        } catch (err: any) {
            error.value = err.message || 'An error occurred';
        }
    };

    const formatScenariosWithTypes = (scenarios: Scenario[]) => {
        return scenarios.map((scenario: Scenario) => {
            return {
                ...scenario,
                types: Array.isArray(scenario.types) ? scenario.types?.map((type: ApiScenarioType) => type.name) : []
            };
        });
    };

    const killScenarioOptimization = async (scenario: Scenario) => {
        confirm.require({
            message: "Are you sure you want to kill this scenario's optimization? This cannot be undone.",
            header: 'Confirmation',
            icon: 'pi pi-exclamation-triangle text-red-500',
            rejectClass: 'p-button-danger p-button-outlined',
            rejectLabel: 'Cancel',
            acceptLabel: 'Kill',
            accept: async () => {
                try {
                    isLoading.value = true;
                    await scenarioService.killScenarioOptimization(scenario.id);
                    fetchScenarios();
                } catch (error) {
                    console.error('Error killing scenario optimization:', error);
                } finally {
                    isLoading.value = false;
                }
            }
        });
    };

    const deleteScenario = async (scenario: Scenario) => {
        confirm.require({
            message: "Are you sure you want to delete this scenario's optimization?",
            header: 'Confirmation',
            icon: 'pi pi-exclamation-triangle text-red-500',
            rejectClass: 'p-button-danger p-button-outlined',
            rejectLabel: 'Cancel',
            acceptLabel: 'Delete',
            accept: async () => {
                try {
                    isLoading.value = true;
                    await scenarioService.deleteScenario(scenario.id);
                    fetchScenarios();
                } catch (error) {
                    console.error('Error deleting scenario:', error);
                } finally {
                    isLoading.value = false;
                }
            }
        });
    };

    const showDeleteButton = (data: any) => {
        return (
            (data.deletedAt === null && data.status !== 'Processing' && role !== 'User') ||
            data.id === authStore.user?.id
        );
    };

    const updateScenarios = (data: number) => {
        scenarios.value = scenarioStore.getScenariosByOrganizationId(data);
    };

    const handleScenarioRenamed = (scenarioId: number | null, newName: string) => {
        if (!scenarioId) return;
        scenarios.value = scenarios.value.map((scenario: Scenario) => {
            if (scenario.id === scenarioId) {
                return { ...scenario, name: newName };
            }
            return scenario;
        });
    };

    const {
        scenarioIdBeingRenamed,
        newScenarioName,
        scenarioToBeCopied,
        handleScenarioRename,
        handleScenarioCopy,
        canRenameScenario,
        scenarioRenameVisible,
        scenarioCopyVisible,
        handleCopyAndEditClick,
        handleRenameClick
    } = useScenarioActions(() => {
        handleScenarioRenamed(scenarioIdBeingRenamed.value, newScenarioName.value);
    });

    onMounted(async () => {
        isLoading.value = true;

        try {
            scenarios.value = await scenarioStore.fetchScenarios();
            if (scenarios.value) {
                scenarios.value = scenarios.value.map(function (scenario: Scenario) {
                    return {
                        ...scenario,
                        types: Array.isArray(scenario.types)
                            ? scenario.types?.map((type: ApiScenarioType) => type.name)
                            : []
                    };
                });
            }
        } finally {
            isLoading.value = false;
        }
    });
</script>

<template>
    <div class="flex flex-col h-auto mb-10">
        <ScenarioRenameDialog
            v-model:scenarioRenameVisible="scenarioRenameVisible"
            v-model:scenarioIdBeingRenamed="scenarioIdBeingRenamed"
            v-model:newScenarioName="newScenarioName"
            :handleScenarioRename="handleScenarioRename"
        />
        <ScenarioCopyAndEditDialog
            v-model:scenarioCopyVisible="scenarioCopyVisible"
            v-model:scenarioToBeCopied="scenarioToBeCopied"
            :handleScenarioCopy="handleScenarioCopy"
        />

        <PCard class="mt-10 grow" pt:body:class="mb-[-2.5rem]">
            <template #header>
                <div class="px-10 py-6 card-header text-2xl text-black font-bold flex justify-between items-center">
                    <div>Scenario Queue</div>
                    <div v-if="authStore.isSuperAdmin" class="flex items-center">
                        <OrganizationScenarioDropdown
                            @organization-selected="updateScenarios"
                        ></OrganizationScenarioDropdown>
                    </div>
                </div>
            </template>
            <template #content>
                <ConfirmDialog></ConfirmDialog>
                <div class="overflow pb-10">
                    <DataTable
                        :loading="isLoading"
                        :value="scenarios"
                        size="small"
                        showGridlines
                        :pt="{
                            headerRow: { class: 'bg-primary text-sm' },
                            thead: { class: 'bg-primary' },
                            column: { class: 'bg-primary-500' },
                            tableContainer: { class: 'rounded-t-lg' }
                        }"
                        :row-class="rowClass"
                        paginator
                        :rows="20"
                        :rowsPerPageOptions="[5, 10, 20, 50]"
                        paginatorTemplate="RowsPerPageDropdown FirstPageLink PrevPageLink CurrentPageReport NextPageLink LastPageLink"
                        currentPageReportTemplate="{first} to {last} of {totalRecords}"
                    >
                        <template #empty>No scenarios found.</template>
                        <PColumn
                            v-for="column in scenarioTableColumns.filter(
                                (col: ScenarioTableColumn) =>
                                    col.field !== 'status' && col.field !== 'user' && col.field !== 'wellCount'
                            )"
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
                        ></PColumn>
                        <PColumn
                            field="wellCount"
                            header="# of Wells"
                            :sortable="true"
                            key="scenario.id"
                            :pt="{
                                headerCell: { class: 'bg-primary border-l-0' },
                                headerTitle: {
                                    class: 'text-slate-50 w-auto whitespace-nowrap overflow-visible text-sm'
                                },
                                sortIcon: { class: 'text-slate-50' }
                            }"
                        >
                            <template #body="slotProps">
                                <span
                                    v-if="slotProps.data.status !== 'Processing' && slotProps.data.status !== 'Pending'"
                                    >{{ slotProps.data.wellCount }}</span
                                >
                            </template></PColumn
                        >
                        <PColumn
                            field="user"
                            header="Created By"
                            :sortable="true"
                            key="user.id"
                            :pt="{
                                headerCell: { class: 'bg-primary border-l-0' },
                                headerTitle: {
                                    class: 'text-slate-50 w-auto whitespace-nowrap overflow-visible text-sm'
                                },
                                sortIcon: { class: 'text-slate-50' }
                            }"
                        >
                            <template #body="slotProps">
                                <span>{{ slotProps.data.user.firstName }} {{ slotProps.data.user.lastName }}</span>
                            </template>
                        </PColumn>
                        <PColumn
                            field="types"
                            header="Scenario Type"
                            :sortable="true"
                            key="data.types"
                            :pt="{
                                headerCell: { class: 'bg-primary border-l-0' },
                                headerTitle: {
                                    class: 'text-slate-50 w-auto whitespace-nowrap overflow-visible text-sm'
                                },
                                sortIcon: { class: 'text-slate-50' }
                            }"
                        >
                            <template #body="slotProps">
                                <div
                                    class="flex gap-2"
                                    v-if="slotProps.data?.types && slotProps.data?.types.length > 0"
                                >
                                    <TypePill
                                        v-for="(type, index) in slotProps.data?.types || []"
                                        :key="index"
                                        :type="type"
                                        class="mb-1"
                                    />
                                </div>
                            </template>
                        </PColumn>
                        <PColumn
                            field="data.status"
                            header="Status"
                            :sortable="true"
                            key="status"
                            :pt="{
                                headerCell: { class: 'bg-primary border-l-0' },
                                headerTitle: {
                                    class: 'text-slate-50 w-auto whitespace-nowrap overflow-visible text-sm'
                                },
                                sortIcon: { class: 'text-slate-50' }
                            }"
                        >
                            <template #body="slotProps">
                                <div
                                    v-if="slotProps.data.status === 'Published' && slotProps.data.deletedAt === null"
                                    class="text-center"
                                >
                                    <PButton
                                        icon="pi pi-search"
                                        v-tooltip.top="{
                                            value: 'Review Scenario',
                                            pt: {
                                                text: '!bg-gray-100 !text-gray-500'
                                            }
                                        }"
                                        severity="secondary"
                                        @click="goToScenarioReview(slotProps.data)"
                                    ></PButton>
                                </div>
                                <div class="text-center" v-else-if="slotProps.data.status == 'Processing'">
                                    <i
                                        class="pi pi-hourglass"
                                        v-tooltip.top="{
                                            value: 'Processing',
                                            pt: {
                                                text: '!bg-gray-100 !text-gray-500'
                                            }
                                        }"
                                    >
                                    </i>
                                </div>
                                <span v-else>{{ slotProps.data.status }}</span>
                            </template>
                            ></PColumn
                        >
                        <PColumn
                            field="data.status"
                            header="Actions"
                            :sortable="false"
                            key="status"
                            :pt="{
                                headerCell: { class: 'bg-primary border-l-0' },
                                headerTitle: {
                                    class: 'text-slate-50 w-auto whitespace-nowrap overflow-visible text-sm'
                                },
                                sortIcon: { class: 'text-slate-50' }
                            }"
                        >
                            <template #body="slotProps">
                                <div class="flex flex-row items-center gap-2">
                                    <span v-if="slotProps.data.status === 'Processing'">
                                        <PButton
                                            icon="pi pi-times-circle"
                                            v-tooltip.top="{
                                                value: 'Kill process',
                                                pt: {
                                                    text: '!bg-gray-100 !text-gray-500'
                                                }
                                            }"
                                            severity="danger"
                                            @click="killScenarioOptimization(slotProps.data)"
                                        ></PButton>
                                    </span>
                                    <span v-if="showDeleteButton(slotProps.data)">
                                        <PButton
                                            icon="pi pi-trash"
                                            v-tooltip.top="{
                                                value: 'Delete Scenario',
                                                pt: {
                                                    text: '!bg-gray-100 !text-gray-500'
                                                }
                                            }"
                                            severity="secondary"
                                            @click="deleteScenario(slotProps.data)"
                                        ></PButton>
                                    </span>
                                    <span v-if="slotProps.data.status === 'Published'">
                                        <PButton
                                            icon="pi pi-file-edit"
                                            v-tooltip.top="{
                                                value: 'Copy & Edit Scenario',
                                                pt: {
                                                    text: '!bg-gray-100 !text-gray-500'
                                                }
                                            }"
                                            severity="secondary"
                                            @click="handleCopyAndEditClick(slotProps.data.id)"
                                        ></PButton>
                                    </span>
                                    <span
                                        v-if="
                                            slotProps.data.status === 'Published' && canRenameScenario(slotProps.data)
                                        "
                                        class="w-[2.5rem] h-[2.5rem] flex items-center justify-center"
                                    >
                                        <PButton
                                            id="rename-scenario-button"
                                            class="!pi-button-icon-only w-2.5rem"
                                            @click="handleRenameClick(slotProps.data.id)"
                                            v-tooltip.top="{
                                                value: 'Rename Scenario',
                                                pt: {
                                                    text: '!bg-gray-100 !text-gray-500'
                                                }
                                            }"
                                            severity="secondary"
                                        >
                                            <span class="p-button-icon flex items-center justifty-center"
                                                ><IconRename
                                            /></span>
                                        </PButton>
                                    </span>
                                </div>
                            </template>
                        </PColumn>
                    </DataTable>
                </div>
            </template>
        </PCard>
    </div>
</template>

<style scoped>
    #rename-scenario-button {
        width: 2.5rem;
        height: 2.5rem;
        padding-inline-start: 0;
        padding-inline-end: 0;
        gap: 0;
    }

    #rename-scenario-button .p-button-icon {
        box-sizing: border-box;
        border-width: 0;
    }
</style>
