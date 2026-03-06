<script setup lang="ts">
    import { onMounted } from 'vue';
    import { createAuthService } from '@/services/authService';
    import { useRoute } from 'vue-router';

    const authService = createAuthService();
    const route = useRoute();

    onMounted(async () => {
        if (typeof route.params.token === 'string') {
            await authService.openPasswordResetWindow(route.params.token);
        }
    });
</script>

<template>
    <div>Complete resetting password</div>
</template>
