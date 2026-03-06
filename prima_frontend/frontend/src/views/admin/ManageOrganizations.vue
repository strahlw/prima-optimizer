<script setup lang="ts">
    import { ref, onMounted } from 'vue';
    import { useConfirm } from 'primevue/useconfirm';
    import { usePermissions } from '@/composables/usePermissions';

    import { useOrganizationStore } from '@/stores/organizationStore';
    import { createOrganizationManagementService } from '@/services/organizationManagementService';

    import type { Organization } from '@/types/organization';
    import CreateOrganization from '@/components/organizations/CreateOrganization.vue';
    import EditOrganization from '@/components/organizations/EditOrganization.vue';

    const organizationStore = useOrganizationStore();
    const organizationManagementService = createOrganizationManagementService();
    const confirm = useConfirm();
    const { hasPermission } = usePermissions();

    const orgs = ref<Organization[]>([]);
    const loading = ref<boolean>(true);
    const showCreateOrgDialog = ref<boolean>(false);
    const orgToEdit = ref<Organization | null>(null);

    const columns = ref([
        { field: 'id', header: 'ID' },
        { field: 'key', header: 'Key' },
        { field: 'name', header: 'Name' },
        { field: 'longitude', header: 'Longitude' },
        { field: 'latitude', header: 'Latitude' },
        { field: 'availableFunding', header: 'Available Funding' },
        { field: 'wellCount', header: 'Well Count' },
        { field: 'paTarget', header: 'P&A Target' }
    ]);

    onMounted(async () => {
        loading.value = true;

        await organizationStore.fetchOrganizations(true);
        orgs.value = organizationStore.getOrganizations;

        loading.value = false;
    });

    const deleteOrg = (id: number) => {
        confirm.require({
            message: 'Are you sure you want to delete this organization?',
            header: 'Confirmation',
            icon: 'pi pi-exclamation-triangle text-red-500',
            rejectClass: 'p-button-danger p-button-outlined',
            rejectLabel: 'Cancel',
            acceptLabel: 'Delete',
            accept: async () => {
                const response = await organizationManagementService.deleteOrganization(id);
                if (response) {
                    orgs.value = orgs.value.filter((org) => org.id !== id);
                }
            }
        });
    };

    const editOrg = (id: number) => {
        orgToEdit.value = orgs.value.find((org) => org.id === id) || null;
    };

    const handleOrgUpdated = (org: Organization) => {
        const index = orgs.value.findIndex((o) => o.id === org.id);
        orgs.value[index] = org;
        orgToEdit.value = null;
    };

    const handleOrgCreated = (org: Organization) => {
        orgs.value.push(org);
        showCreateOrgDialog.value = false;
    };
</script>

<template>
    <PCard
        :pt="{
            root: { class: 'mt-10 flex flex-grow px-20' },
            body: { class: 'px-20' }
        }"
        :loading="loading"
    >
        <template #header>
            <div class="grid grid-cols-3 w-full items-center my-6">
                <div></div>
                <div><h1>Manage Organizations</h1></div>
                <div class="text-right justify-self-end ml-auto">
                    <PButton
                        class="btn-secondary font-bold"
                        @click="showCreateOrgDialog = true"
                        v-if="hasPermission('add-organizations')"
                        >Add Organization</PButton
                    >
                </div>
            </div>
        </template>

        <template #content>
            <ConfirmDialog></ConfirmDialog>
            <CreateOrganization
                :dialogVisible="showCreateOrgDialog"
                @close-dialog="showCreateOrgDialog = false"
                @organization-created="handleOrgCreated"
            />
            <EditOrganization
                :dialogVisible="orgToEdit !== null"
                @close-dialog="orgToEdit = null"
                :organization="orgToEdit"
                @organization-updated="handleOrgUpdated"
            />
            <div v-if="loading" class="flex justify-center items-center h-full">
                <ProgressSpinner />
            </div>

            <span v-else>
                <div>
                    <DataTable
                        :value="orgs"
                        size="small"
                        showGridlines
                        :pt="{
                            headerRow: { class: 'bg-primary' },
                            thead: { class: 'bg-primary' },
                            column: { class: 'bg-primary-500' },
                            tableContainer: { class: 'rounded-t-lg' }
                        }"
                    >
                        <template #empty>No organizations found.</template>
                        <PColumn
                            v-for="column in columns"
                            :field="column.field"
                            :header="column.header"
                            :sortable="orgs.length > 0"
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
                            field="logoPath"
                            header="Logo"
                            :pt="{
                                headerCell: { class: 'bg-primary border-l-0' },
                                headerTitle: {
                                    class: 'text-slate-50 w-auto whitespace-nowrap overflow-visible text-sm'
                                }
                            }"
                        >
                            <template #body="{ data }">
                                <img :src="data.logoUrl" alt="Organization Logo" v-if="data.logoUrl" /> </template
                        ></PColumn>
                        <PColumn
                            label="Actions"
                            :pt="{
                                headerCell: { class: 'bg-primary border-l-0' },
                                headerTitle: { class: 'text-slate-50 text-sm' }
                            }"
                        >
                            <template #body="slotProps">
                                <div class="flex action-buttons">
                                    <PButton
                                        v-if="hasPermission('edit-organizations')"
                                        icon="pi pi-pencil text-secondary"
                                        class="shadow-none"
                                        text
                                        rounded
                                        severity="secondary"
                                        aria-label="Edit"
                                        @click="editOrg(slotProps.data.id)"
                                    ></PButton>
                                    <PButton
                                        v-if="hasPermission('delete-organizations')"
                                        icon="pi pi-trash"
                                        class="shadow-none"
                                        text
                                        rounded
                                        severity="danger"
                                        aria-label="Edit"
                                        @click="deleteOrg(slotProps.data.id)"
                                    ></PButton>
                                </div>
                            </template>
                        </PColumn>
                    </DataTable>
                </div>
            </span>
        </template>
    </PCard>
</template>

<style scoped>
    .action-buttons .p-button {
        box-shadow: none;
    }
</style>
