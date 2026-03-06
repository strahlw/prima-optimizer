<script setup>
import { ref } from "vue";
const props = defineProps({
    name: String,
    label: String,
    type: {
        type: String,
        default: "text",
    },
    modelValue: String,
});

const inputValue = ref(props.modelValue);
</script>

<template>
    <InputGroup class="mb-3 mt-10">
        <InputGroupAddon>
            <i class="pi pi-envelope"></i>
        </InputGroupAddon>
        <InputText
            class="w-full"
            v-model="inputValue"
            :id="name"
            :type="type"
            :name="name"
            :placeholder="label"
        />
    </InputGroup>
</template>
