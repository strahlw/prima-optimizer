<script setup>
import { ref } from "vue";
import Password from "primevue/password";
const props = defineProps({
    name: String,
    label: String,
    type: {
        type: String,
        default: "password",
    },
    modelValue: String,
    feedback: {
        type: Boolean,
        default: false,
    },
});

const inputValue = ref(props.modelValue);
</script>

<template>
    <InputGroup class="mb-3">
        <InputGroupAddon>
            <i class="pi pi-unlock"></i>
        </InputGroupAddon>
        <Password
            class="w-full"
            v-model="inputValue"
            toggleMask
            :id="name"
            :type="type"
            :name="name"
            :placeholder="label"
            inputId="password"
            inputName="password"
            :inputProps="{ name: 'password' }"
            :pt="{
                input: { type: 'password', name: 'password', id: 'password' },
            }"
            :feedback="props.feedback"
        />
    </InputGroup>
</template>
