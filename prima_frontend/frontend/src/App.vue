<script setup lang="ts">
    import { RouterView } from 'vue-router';
    import { onMounted } from 'vue';
    import { useOrganizationStore } from './stores/organizationStore';
    import { useAuthStore } from './stores/authStore';
    import NavBar from './components/NavBar.vue';
    import Toast from 'primevue/toast';

    const organizationStore = useOrganizationStore();
    const authStore = useAuthStore();

    onMounted(() => {
        organizationStore.fetchOrganizations();
        authStore.fetchAvailableRoles();
    });
</script>

<template>
    <NavBar class="navbar" />
    <Toast ref="toast" />

    <div class="main-container" :class="{ 'has-sidebar': $route.name === 'scenarios' }">
        <RouterView style="width: 100%" />
    </div>
</template>

<style>
    .main-container {
        display: flex;
        justify-content: center;
        background-color: #f7f5f7;
        padding: 0 48px 48px;
        overflow-x: hidden;
    }

    .main-container:not(.has-sidebar) > * {
        max-width: 1600px;
        width: 100%;
    }

    .main-container.has-sidebar {
        padding: 0;
        justify-content: stretch;
    }

    .main-container.has-sidebar > * {
        width: 100%;
        max-width: none;
    }
</style>
