<script setup lang="ts">
    import { onMounted, ref } from 'vue';
    import EditUser from '@/components/users/EditUser.vue';
    import { useAuthStore } from '@/stores/authStore';
    import type { User } from '@/types/user';

    const loading = ref<boolean>(false);
    const authStore = useAuthStore();
    const editing = ref<boolean>(false);
    const user = ref<User | null>(null);

    const handleUserUpdated = (updatedUser: User) => {
        editing.value = false;
        const updatedData = { firstName: updatedUser.firstName, lastName: updatedUser.lastName };
        user.value = { ...user.value, ...updatedData } as User;
        authStore.setUser(user.value);
    };

    onMounted(() => {
        loading.value = true;
        // Fetch user details
        user.value = authStore.getUser;
        loading.value = false;
    });
</script>

<template>
    <PCard
        :pt="{
            root: { class: 'mt-10 flex flex-grow px-20' },
            body: { class: 'px-20' }
        }"
    >
        <template #header>
            <div class="w-full items-center">
                <div class="text-center"><h1>Account Details</h1></div>
            </div>
        </template>
        <template #content>
            <ConfirmDialog></ConfirmDialog>
            <EditUser
                :dialogVisible="editing === true"
                @close-dialog="editing = false"
                :user="user"
                @user-updated="handleUserUpdated"
            />
            <div v-if="loading" class="flex justify-center items-center h-full">
                <ProgressSpinner />
            </div>

            <div v-else class="flex flex-col">
                <div>
                    <div><span class="font-bold">First Name: </span>{{ user?.firstName }}</div>
                    <div><span class="font-bold">Last Name: </span>{{ user?.lastName }}</div>
                    <div><span class="font-bold">Email: </span>{{ user?.email }}</div>
                </div>
                <PButton class="btn-secondary w-24 mt-2" @click="editing = true">
                    <span class="pi pi-pencil" />
                    <span class="ml-2">Edit</span>
                </PButton>
            </div>
        </template>
    </PCard>
</template>
