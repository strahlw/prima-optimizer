<script setup lang="ts">
    import { onMounted, computed } from 'vue';
    import { createAuthService } from '../../services/authService';
    import { useToast } from 'primevue/usetoast';
    import { useAuthStore } from '@/stores/authStore';
    import { useRouter } from 'vue-router';
    import homepageImage from '@/assets/homepage_well_2.jpg';
    import IconFunding from '@/components/icons/IconFunding.vue';
    import IconTarget from '@/components/icons/IconTarget.vue';
    import IconWellCount from '@/components/icons/IconWellCount.vue';
    import Image from 'primevue/image';

    const toast = useToast();
    const authStore = useAuthStore();
    const authService = createAuthService();
    const router = useRouter();

    const isAuthenticated = computed(() => authStore.user !== null);
    const user = computed(() => authStore.getUser);
    const organization = computed(() => authStore.getOrganization);

    const props = defineProps({
        reset: {
            type: Boolean,
            required: false,
            default: false
        },
        creation: {
            type: Boolean,
            required: false,
            default: false
        }
    });

    const messageEventListener = (event: MessageEvent) => {
        if (event.data.type === 'loginSuccess') {
            authService.login(event.data.loginData);
            window.removeEventListener('message', () => {});
            router.push({ name: 'home' });
        } else if (event.data.type === 'loginFailure') {
            toast.add({ severity: 'error', summary: 'Error', detail: 'Login failed, please try again.', life: 3000 });
            window.removeEventListener('message', () => {});
        }
    };

    onMounted(() => {
        if (props.reset) {
            toast.add({
                severity: 'success',
                summary: 'Password Reset',
                detail: 'Your password was successfully reset. Please log in using your new password.',
                life: 7000
            });
            authService.openLoginWindow();
            window.addEventListener('message', messageEventListener);
        } else if (props.creation) {
            toast.add({
                severity: 'success',
                summary: 'Account Registration Completed',
                detail: 'Your account has been created. Please log in using your new password.',
                life: 7000
            });
            authService.openLoginWindow();
            window.addEventListener('message', messageEventListener);
        }
    });

    const sendEmail = () => {
        const recipient = import.meta.env.VITE_EMAIL_RECIPIENT;

        const mailtoLink = `mailto:${recipient}`;

        window.location.href = mailtoLink;
    };
</script>
<!-- NOTE: If height is too high, the cause is the main-container class -->
<template>
    <PCard
        :pt="{
            root: { class: 'mt-10 flex flex-grow px-12' },
            body: { class: 'px-2 pb-0' }
        }"
    >
        <template #header>
            <div class="grid grid-cols-3 w-full items-center mt-4" v-if="isAuthenticated">
                <div class="">
                    <span class="text-2xl font-bold">{{ organization?.name || '' }}</span>
                </div>
                <div class="text-center">
                    <span class="text-2xl font-bold">Welcome Back, {{ user?.firstName }}</span>
                </div>
                <div class="text-center justify-self-end">
                    <img v-if="organization?.logoUrl" :src="organization.logoUrl" alt="Logo" />
                </div>
            </div>
            <div class="flex flex-col w-full mt-4 items-center justify-center" v-else>
                <h2>PRIMA: The UOW Characterization Optimizer</h2>
                <p class="w-3/4">
                    PRIMA is a free and open-source software decision-support tool developed and released by the
                    Department of Energy’s National Energy Technology Laboratory (NETL). PRIMA is a well-plugging
                    optimizer that allows users to identify <b>impactful</b> and <b>efficient</b> P&A projects. "PRIMA
                    uses plugging priorities to guide its characterization recommendations. By factoring in
                    undocumented, uninspected orphaned wells, PRIMA can identify sites where characterization resources
                    will have the greatest impact and improve the efficiency of P&A efforts.
                    <!-- PRIMA is a well-plugging -->
                    <!-- optimizer that supports users in making <b>transparent, defensible and articulable</b> decisions by
                    recommending <b>impactful</b> and <b>efficient</b> plugging projects. -->
                </p>
            </div>
        </template>

        <template #content>
            <div class="grid grid-cols-3 w-full gap-8">
                <div class="flex flex-col col-span-1" style="max-height: 200px">
                    <!-- <PCard>
                        <template #title>
                            <div class="ml-2 font-bold" v-if="isAuthenticated">Program Overview</div>
                            <div class="ml-2 font-bold" v-else>UOW Overview</div>
                        </template>
                        <template #content>
                            <div class="flex flex-col text-black">
                                <div class="flex items-center w-full">
                                    <IconFunding fillClass="fill-secondary" size="xl" />
                                    <div class="flex flex-col justify-center ml-6" v-if="isAuthenticated">
                                        <div class="w-full">Available Funding:</div>
                                        <div class="font-bold" v-if="organization && organization.availableFunding">
                                            {{
                                                Intl.NumberFormat('en-US', {
                                                    style: 'currency',
                                                    currency: 'USD',
                                                    minimumFractionDigits: 0,
                                                    maximumFractionDigits: 0
                                                }).format(organization.availableFunding)
                                            }}
                                        </div>
                                        <div class="font-bold" v-else>Not Specified</div>
                                    </div>
                                    <div class="flex flex-col justify-center ml-6" v-else>
                                        <div class="w-full">Total Budget:</div>
                                        <div class="font-bold">$350 million</div>
                                    </div>
                                </div>

                                <div class="flex items-center w-full mt-4">
                                    <IconWellCount fillClass="fill-secondary" size="xl" />
                                    <div class="flex flex-col justify-center ml-6" v-if="isAuthenticated">
                                        <div class="w-full">Well Count:</div>
                                        <div class="font-bold" v-if="organization && organization.wellCount">
                                            {{ Intl.NumberFormat().format(organization.wellCount) }}
                                        </div>
                                        <div class="font-bold" v-else>Not Specified</div>
                                    </div>
                                    <div class="flex flex-col justify-center ml-6" v-else>
                                        <div class="w-full">Participating States:</div>
                                        <div class="font-bold">14</div>
                                    </div>
                                </div>

                                <div class="flex items-center w-full mt-4">
                                    <IconTarget fillClass="fill-secondary" size="xl" />
                                    <div class="flex flex-col justify-center ml-6" v-if="isAuthenticated">
                                        <div class="w-full">P&A Target:</div>
                                        <div class="font-bold" v-if="organization && organization.paTarget">
                                            {{ Intl.NumberFormat().format(organization.paTarget) }}
                                        </div>
                                        <div class="font-bold" v-else>TBD</div>
                                    </div>
                                    <div class="flex flex-col justify-center ml-6" v-else>
                                        <div class="w-full">Goal:</div>
                                        <div class="font-bold">Impactful and Efficient P&A Campaigns</div>
                                    </div>
                                </div>
                            </div>
                        </template>
                    </PCard> -->
                    <PCard
                        :pt="{
                            root: { class: 'mt-10 flex flex-grow p-2 ' },
                            body: { class: 'px-4 ml-2' }
                        }"
                    >
                        <template #title> <div class="mx-auto">Questions?</div></template>
                        <template #content>
                            <div class="flex flex-col items-start">
                                <span>Our team is here to assist you.</span>
                                <PButton class="btn-secondary mt-6 bg-secondary-500 py-4 px-10" @click="sendEmail">
                                    <span class="font-bold">Email Us</span>
                                </PButton>
                            </div>
                        </template>
                    </PCard>
                </div>

                <div class="col-span-2 w-full h-full flex justify-end rounded-lg" style="max-height: 550px">
                    <Image
                        :src="homepageImage"
                        alt="homepageImage"
                        class="w-3/4 h-full object-cover"
                        :pt="{ image: 'h-full w-full rounded-lg' }"
                    />
                </div>
            </div>
        </template>
    </PCard>
</template>
