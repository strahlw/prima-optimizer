<script setup lang="ts">
    import { computed, ref, watch } from 'vue';
    import { RouterLink, useRouter } from 'vue-router';
    import type { MenuItem } from 'primevue/menuitem';
    import { Menubar } from 'primevue';
    import { useToast } from 'primevue/usetoast';
    import Dialog from 'primevue/dialog';

    import logo from '/prima_official_logo.png';
    import { createAuthService } from '@/services/authService';
    import { useAuthStore } from '../stores/authStore';
    import { usePermissions } from '@/composables/usePermissions';
    import { useCreateScenario } from '@/composables/createScenario';

    import IconDownloading from './icons/IconDownloading.vue';
    import IconCustomScenario from './icons/IconCustomScenario.vue';

    const authService = createAuthService();
    const authStore = useAuthStore();
    const loginWindow = ref<Window | null>(null);
    const toast = useToast();
    const { hasRole } = usePermissions();
    const router = useRouter();
    const { createScenarioNavigation } = useCreateScenario();
    const disclaimerVisible = ref<boolean>(false);
    const hideDisclaimer = ref<boolean>(false);

    const iconComponents: Record<string, any> = {
        'custom-downloading': IconDownloading,
        'custom-scenario': IconCustomScenario
    };

    const items: MenuItem[] = [
        { url: '/well-overview', label: 'Well Overview', icon: 'pi pi-map-marker', items: [] },
        {
            url: '/scenarios',
            label: 'Scenarios',
            icon: 'custom-scenario',
            iconProps: { size: 'md', fillClass: 'fill-primary', items: [] }
        },
        {
            url: '/scenario-queue',
            label: 'Scenario Queue',
            icon: 'custom-downloading',
            iconProps: { size: 'md', fillClass: 'fill-primary', items: [] }
        },
        { url: '/upload-data', label: 'Add Well Data', icon: 'pi pi-upload', items: [] },
        { url: '/manage-users', label: 'Manage Users', icon: 'pi pi-users', items: [] },
        { url: '/account-details', label: 'Account Details', icon: 'pi pi-users', items: [] },
        { url: '/manage-organizations', label: 'Manage Orgs', icon: 'pi pi-globe', items: [] }
    ];

    const getIconComponent = (icon: string) => {
        return iconComponents[icon] || null;
    };

    const messageEventListener = (event: MessageEvent) => {
        if (event.data.type === 'loginSuccess') {
            authService.login(event.data.loginData);
            if (event.data.loginData.user.showDisclaimer && import.meta.env.VITE_SHOW_DISCLAIMER === 'true') {
                disclaimerVisible.value = true;
            }
            window.removeEventListener('message', () => {});
        } else if (event.data.type === 'loginFailure') {
            toast.add({ severity: 'error', summary: 'Error', detail: 'Login failed, please try again.', life: 3000 });
            window.removeEventListener('message', () => {});
        } else {
            window.removeEventListener('message', () => {});
        }
    };

    const openLoginWindow = async () => {
        loginWindow.value = await authService.openLoginWindow();
        window.addEventListener('message', messageEventListener);
    };

    watch(disclaimerVisible, (newValue) => {
        if (newValue === false && hideDisclaimer.value === true) {
            authService.hideDisclaimer();
        }
    });

    const breakpoint = computed(() => {
        if (hasRole(['super-admin'])) {
            return '1150px';
        }

        return '1075px';
    });
</script>

<template>
    <Menubar
        :model="authStore.isAuthenticated ? items : []"
        orientation="horizontal"
        :breakpoint="breakpoint"
        class="whitespace-nowrap"
    >
        <template #start>
            <img :src="logo" alt="Home" class="logo cursor-pointer" @click="() => router.push('/')" />
            <Dialog
                header="PRIMO Web App Beta Version Disclaimer:"
                modal
                v-model:visible="disclaimerVisible"
                :style="{ width: '35rem' }"
            >
                <div class="font-bold mb-2 text-sm">PRIMO Web App Beta Version Disclaimer</div>
                <div class="text-sm mb-4">
                    This version of PRIMO is a developmental beta and is NOT the final/released version of the software.
                    As such, users may encounter bugs, incomplete features, or unexpected behavior.
                    <br /><br />
                    Access to PRIMO is granted for the explicit purpose of soliciting user feedback to facilitate
                    ongoing development. In this collaborative development capacity, users are encouraged to utilize
                    PRIMO for the assessment of its capabilities. Any inquiries, interpretations, or decisions
                    predicated upon results obtained using PRIMO are the exclusive responsibility of the user. The
                    National Energy Technology Laboratory (NETL) disclaims all responsibility for outcomes originating
                    from the application of this tool. Furthermore, this web application is not authorized for public
                    dissemination or demonstration.
                    <br /><br />
                    Please report any bugs or issues encountered to
                    <a href="mailto:primo@netl.doe.gov">primo@netl.doe.gov</a>. Thank you!
                </div>
                <hr />
                <div class="font-bold mb-2 text-sm">Sample Data Disclaimer:</div>
                <div class="text-sm mb-4">
                    The purpose of the dataset provided in the beta version of PRIMO is to allow prospective users of
                    the software to explore and test PRIMO’s capabilities using realistic well records.
                    <br /><br />
                    This data has been collected from publicly available sources only. It captures well attributes and
                    records from Pennsylvania, but neither the raw data nor any results derived thereof are verified or
                    endorsed by any Pennsylvania-based agencies or NETL. In particular, the data does not reflect which
                    information state agencies may use to plan or execute emissions mitigation or P&A campaigns.
                    <br /><br />
                    The data contained in this benchmark set may be outdated, incomplete or inaccurate and should
                    therefore only be used for testing purposes. As such, the authors assume no responsibility for any
                    errors, omissions, or misrepresentations in this dataset.
                </div>
                <div class="flex justify-end gap-2 mb-4">
                    <PCheckbox v-model="hideDisclaimer" :binary="true" inputId="hideDisclaimer" />
                    <label for="hideDisclaimer" class="text-sm">Do not show this disclaimer again</label>
                </div>
                <div class="flex justify-end gap-2">
                    <PButton type="button" label="I Understand" @click="disclaimerVisible = false"></PButton>
                </div>
            </Dialog>
        </template>
        <template #item="{ item }" v-if="authStore.isAuthenticated">
            <span v-if="item.label === 'Manage Orgs'">
                <RouterLink
                    v-if="hasRole(['super-admin'])"
                    :to="item.url || ''"
                    class="nav-item text-primary cursor-pointer"
                >
                    <div v-if="item.iconProps" class="flex -mt-1 -mb-1">
                        <component :is="getIconComponent(item.icon ?? '')" v-bind="item.iconProps" />
                    </div>
                    <span :class="item.icon" />
                    <span class="ml-2 primary text-xs">{{ item.label }}</span>
                </RouterLink>
            </span>

            <span v-else-if="item.label === 'Add Well Data' || item.label === 'Manage Users'">
                <RouterLink
                    v-if="hasRole(['super-admin', 'org-admin'])"
                    :to="item.url || ''"
                    class="nav-item text-primary cursor-pointer"
                >
                    <div v-if="item.iconProps" class="flex -mt-1 -mb-1">
                        <component :is="getIconComponent(item.icon ?? '')" v-bind="item.iconProps" />
                    </div>
                    <span :class="item.icon" />
                    <span class="ml-2 primary text-xs">{{ item.label }}</span>
                </RouterLink>
            </span>
            <span v-else-if="item.label === 'Account Details'">
                <RouterLink v-if="hasRole(['user'])" :to="item.url || ''" class="nav-item text-primary cursor-pointer">
                    <div v-if="item.iconProps" class="flex -mt-1 -mb-1">
                        <component :is="getIconComponent(item.icon ?? '')" v-bind="item.iconProps" />
                    </div>
                    <span :class="item.icon" />
                    <span class="ml-2 primary text-xs">{{ item.label }}</span>
                </RouterLink>
            </span>

            <RouterLink :to="item.url || ''" class="nav-item text-primary cursor-pointer" v-else>
                <div v-if="item.iconProps" class="flex -mt-1 -mb-1">
                    <component :is="getIconComponent(item.icon ?? '')" v-bind="item.iconProps" />
                </div>
                <span :class="item.icon" />
                <span class="ml-2 primary text-xs">{{ item.label }}</span>
            </RouterLink>
        </template>

        <template #end>
            <div class="end-container items-center justify-center">
                <PButton
                    class="btn-secondary h-10 text-sm whitespace-nowrap"
                    @click="createScenarioNavigation"
                    v-if="authStore.isAuthenticated"
                >
                    <span class="pi pi-replay" />
                    <span class="ml-2">Create New Scenario</span>
                </PButton>
                <PButton
                    severity="primary"
                    class="shadow-none"
                    id="logout-button"
                    text
                    v-if="authStore.isAuthenticated"
                    @click="authService.logoutUser"
                >
                    <div class="flex flex-col">
                        <span class="pi pi-sign-out"></span>
                        <span class="ml-2 text-xs text-primary font-bold">Logout</span>
                    </div>
                </PButton>
                <PButton severity="primary" class="shadow-none" text v-else @click="openLoginWindow" id="login-button">
                    <div class="flex flex-col">
                        <span class="pi pi-sign-in"></span>
                        <span class="ml-2 text-xs text-primary font-bold">Login</span>
                    </div>
                </PButton>
            </div>
        </template>
    </Menubar>
</template>

<style scoped>
    .nav-item {
        display: flex;
        flex-direction: column;
        align-items: center;
        margin: 0.25rem;
        text-decoration: none;
        @apply mx-1 2xl:mx-4;
    }

    .router-link-active {
        border-bottom: 6px solid #0092c3;
    }

    .logo {
        height: 3rem;
        margin-right: 1rem;
    }

    .end-container {
        display: flex;
        align-items: center;
    }

    #login-button,
    #logout-button {
        box-shadow: none;
    }
</style>
