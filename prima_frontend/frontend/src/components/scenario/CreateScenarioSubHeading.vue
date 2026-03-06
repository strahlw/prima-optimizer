<script setup lang="ts">
    const props = defineProps<{
        text: String;
    }>();
</script>

<template>
    <div class="flex justify-center mr-auto ml-auto bg-gray-100 rounded-lg p-3 w-full mb-8">
        <span class="text-black ml-auto mr-auto text-center text-sm">{{ props.text }}</span>
    </div>
</template>
