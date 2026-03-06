<script setup>
import Button from "primevue/button";

const props = defineProps({
    label: String,
});
</script>

<template>
    <Button
        class="w-full btn-primary text-white font-bold py-2 px-4 rounded justify-center"
        type="submit"
        >{{ props.label }}</Button
    >
</template>
