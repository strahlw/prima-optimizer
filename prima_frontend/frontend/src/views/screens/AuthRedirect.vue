<script setup lang="ts">
    import { onMounted } from 'vue';
    import { useRouter } from 'vue-router';
    import { createAuthService } from '@/services/authService';

    const router = useRouter();
    const authService = createAuthService();

    onMounted(async () => {
        await authService.handleRedirect();
        // Redirect the user after successful login
        router.push({ name: 'map' });
    });
</script>

<template>
    <div class="mt-10"><h1>Logging in...</h1></div>
</template>
