<script setup>
import { computed } from "vue";

const props = defineProps({
    password: {
        default: "",
    },
    passwordConfirmation: {
        default: "",
    },
});

const passwordRequirements = computed(() => [
    {
        name: "Must contain uppercase letters",
        predicate: props.password.toLowerCase() !== props.password,
    },
    {
        name: "Must contain lowercase letters",
        predicate: props.password.toUpperCase() !== props.password,
    },
    {
        name: "Must contain numbers",
        predicate: /\d/.test(props.password),
    },
    {
        name: "Must contain symbols",
        predicate: /\W/.test(props.password),
    },
    {
        name: "Must be at least 8 characters long",
        predicate: props.password.length >= 8,
    },
]);
</script>

<template>
    <ul class="requirements">
        <li
            v-for="(requirement, key) in passwordRequirements"
            :key="key"
            :class="requirement.predicate ? 'text-green-500' : 'text-red-500'"
        >
            {{ requirement.name }}
        </li>
    </ul>
</template>
