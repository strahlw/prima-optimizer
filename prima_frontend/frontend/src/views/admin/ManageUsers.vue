<script setup lang="ts">
    import { ref, onMounted, watch } from 'vue';

    import { useConfirm } from 'primevue/useconfirm';

    import { useOrganizationStore } from '@/stores/organizationStore';
    import { useAuthStore } from '@/stores/authStore';
    import { usePermissions } from '@/composables/usePermissions';
    import { useManageUsersStore } from '@/stores/manageUsersStore';
    import { createAuthService } from '../../services/authService';
    import { createDownloadService } from '@/services/downloadService';
    import { createUserManagementService } from '@/services/userManagementService';

    import type { Organization } from '@/types/organization';
    import CreateUser from '../../components/users/CreateUser.vue';
    import EditUser from '../../components/users/EditUser.vue';
    import type { User } from '@/types/user';

    const organizationStore = useOrganizationStore();
    const authStore = useAuthStore();
    const manageUsersStore = useManageUsersStore();
    const { hasRole, hasPermission } = usePermissions();
    const confirm = useConfirm();
    const authService = createAuthService();
    const downloadService = createDownloadService();
    const userManagementService = createUserManagementService();

    const orgs = ref<Organization[]>([]);
    const selectedOrg = ref<Organization | undefined>(undefined);
    const users = ref<User[]>([]);
    const loading = ref<boolean>(true);
    const downloadProcessing = ref<boolean>(false);
    const showCreateUserDialog = ref<boolean>(false);
    const userToEdit = ref<User | null>(null);

    const columns = ref([
        { field: 'firstName', header: 'First Name' },
        { field: 'lastName', header: 'Last Name' },
        { field: 'email', header: 'Email' }
    ]);

    onMounted(async () => {
        loading.value = true;

        await organizationStore.fetchOrganizations(true);
        orgs.value = organizationStore.getOrganizations;

        if (hasRole('org-admin')) {
            selectedOrg.value = orgs.value.find((org) => org.key === authStore.getOrganization.key) || orgs.value[0];
        } else {
            orgs.value = [
                {
                    id: 0,
                    key: 'ADMIN',
                    name: 'Super Admins',
                    availableFunding: 0,
                    wellCount: 0,
                    paTarget: 0,
                    latitude: 0,
                    longitude: 0
                },
                ...organizationStore.getOrganizations
            ];
            selectedOrg.value = orgs.value[0];
        }

        users.value = manageUsersStore.getUsers;

        loading.value = false;
    });

    const deleteUser = async (id: number) => {
        confirm.require({
            message: 'Are you sure you want to delete this user?',
            header: 'Confirmation',
            icon: 'pi pi-exclamation-triangle text-red-500',
            rejectClass: 'p-button-danger p-button-outlined',
            rejectLabel: 'Cancel',
            acceptLabel: 'Delete',
            accept: async () => {
                const response = await userManagementService.deleteUser(id);
                if (response.status === 200) {
                    users.value = users.value.filter((user) => user.id !== id);
                }
            }
        });
    };

    const editUser = (id: number) => {
        userToEdit.value = users.value.find((user) => user.id === id) || null;
    };

    const handleUserUpdated = (user: User) => {
        userToEdit.value = null;
        const index = users.value.findIndex((u) => u.id === user.id);
        if (index !== -1) {
            users.value[index] = user;
        }
    };

    const handleUserCreated = (user: User) => {
        if (user.organizationId === selectedOrg?.value?.id) users.value.push(user);
        showCreateUserDialog.value = false;
    };

    const resendPasswordCreationLink = async (id: number) => {
        confirm.require({
            message:
                'The selected user has not yet verified their account. Would you like to resend the account creation link?',
            header: 'Confirmation',
            icon: 'pi pi-exclamation-triangle',
            rejectClass: 'p-button-secondary p-button-outlined',
            rejectLabel: 'Cancel',
            acceptLabel: 'Save',
            accept: async () => {
                await authService.resendAccountCreationEmail(id);
            }
        });
    };

    const downloadUserList = async () => {
        downloadProcessing.value = true;

        try {
            await downloadService.downloadUserList();
        } catch (error) {
            console.error('Error downloading user list:', error);
        } finally {
            setTimeout(() => {
                downloadProcessing.value = false;
            }, 1000);
        }
    };

    watch(selectedOrg, async (newOrg) => {
        loading.value = true;

        if (newOrg && (newOrg.id || newOrg.id === 0)) {
            try {
                if (newOrg.id === 0) {
                    await manageUsersStore.fetchSuperAdmins();
                } else {
                    await manageUsersStore.fetchOrganizationUsers(newOrg.id);
                }

                users.value = manageUsersStore.getUsers;
            } catch (error) {
                console.error(error);
            }
        }

        loading.value = false;
    });
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
                <div :class="!hasRole('super-admin') ? 'w-56' : ''">
                    <PSelect
                        v-show="hasRole('super-admin')"
                        class="w-56"
                        v-model="selectedOrg"
                        :options="orgs"
                        optionLabel="name"
                        :disabled="loading || !hasRole('super-admin')"
                        :hidden="!hasRole('super-admin')"
                    />
                </div>
                <div class="text-center"><h1>Manage Users</h1></div>
                <div class="text-right">
                    <PButton class="btn-secondary font-bold" @click="showCreateUserDialog = true">Add User</PButton>
                    <PButton
                        class="btn-primary font-bold ml-3"
                        v-if="hasPermission('netl-admin')"
                        @click="downloadUserList"
                        :disabled="downloadProcessing"
                        >Download User List</PButton
                    >
                </div>
            </div>
        </template>

        <template #content>
            <ConfirmDialog></ConfirmDialog>
            <CreateUser
                :dialogVisible="showCreateUserDialog"
                @close-dialog="showCreateUserDialog = false"
                :selectedOrg="selectedOrg"
                @user-created="handleUserCreated"
            />
            <EditUser
                :dialogVisible="userToEdit !== null"
                @close-dialog="userToEdit = null"
                :user="userToEdit"
                @user-updated="handleUserUpdated"
            />
            <div v-if="loading" class="flex justify-center items-center h-full">
                <ProgressSpinner />
            </div>

            <span v-else>
                <div>
                    <DataTable
                        :value="users"
                        size="small"
                        showGridlines
                        :pt="{
                            headerRow: { class: 'bg-primary' },
                            thead: { class: 'bg-primary' },
                            column: { class: 'bg-primary-500' },
                            tableContainer: { class: 'rounded-t-lg' }
                        }"
                    >
                        <template #empty>No users found.</template>
                        <PColumn
                            v-for="column in columns.filter((col) => col.field !== 'id')"
                            :field="column.field"
                            :header="column.header"
                            :sortable="users.length > 0"
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
                            label="Role"
                            :pt="{
                                headerCell: { class: 'bg-primary border-l-0' },
                                headerTitle: { class: 'text-slate-50 text-sm' }
                            }"
                        >
                            <template #body="slotProps">
                                <div>
                                    {{
                                        authStore.getAvailableRoles.filter(
                                            (role) => role.id === slotProps.data.roleId
                                        )[0].label
                                    }}
                                </div>
                            </template>
                        </PColumn>
                        <PColumn
                            label="Actions"
                            :pt="{
                                headerCell: { class: 'bg-primary border-l-0' },
                                headerTitle: { class: 'text-slate-50 text-sm' }
                            }"
                        >
                            <template #body="slotProps">
                                <div
                                    class="flex action-buttons"
                                    v-if="
                                        (hasRole('super-admin') &&
                                            (slotProps.data.roleName !== 'super-admin' ||
                                                slotProps.data.id === authStore.getUser?.id)) ||
                                        hasPermission('edit-super-admins') ||
                                        (hasRole('org-admin') &&
                                            (slotProps.data.roleName === 'user' ||
                                                slotProps.data.id === authStore.getUser?.id))
                                    "
                                >
                                    <PButton
                                        icon="pi pi-pencil text-secondary"
                                        class="shadow-none"
                                        text
                                        rounded
                                        severity="secondary"
                                        aria-label="Edit"
                                        @click="editUser(slotProps.data.id)"
                                    ></PButton>
                                    <PButton
                                        v-if="authStore.getUser?.id !== slotProps.data.id"
                                        icon="pi pi-trash"
                                        class="shadow-none"
                                        text
                                        rounded
                                        severity="danger"
                                        aria-label="Edit"
                                        @click="deleteUser(slotProps.data.id)"
                                    ></PButton>
                                    <PButton
                                        v-if="
                                            !slotProps.data.accountVerified &&
                                            authStore.getUser?.id !== slotProps.data.id
                                        "
                                        icon="pi pi-key text-black"
                                        iconPos="right"
                                        label="Resend Creation Link"
                                        class="shadow-none text-xs"
                                        rounded
                                        aria-label="Resend Password Creation"
                                        @click="resendPasswordCreationLink(slotProps.data.id)"
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
