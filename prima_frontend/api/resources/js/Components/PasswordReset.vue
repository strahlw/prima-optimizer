<script setup>
import { ref, watch } from "vue";
import Password from "primevue/password";
import PasswordRequirements from "./PasswordRequirements.vue";

const matching = ref(true);
const password = ref("");
const passwordConfirmation = ref("");

const validatePassword = () => {
    if (password.value !== passwordConfirmation.value) {
        matching.value = false;
    } else {
        matching.value = true;
    }
};

watch([passwordConfirmation], () => {
    validatePassword();
});
</script>

<template>
    <div class="flex flex-col">
        <InputGroup class="mb-3">
            <InputGroupAddon>
                <i class="pi pi-unlock"></i>
            </InputGroupAddon>
            <Password
                class="w-full"
                v-model="password"
                toggleMask
                id="password"
                type="password"
                name="password"
                placeholder="Type new password"
                inputId="password"
                inputName="password"
                :inputProps="{ name: 'password' }"
                :pt="{
                    input: {
                        type: 'password',
                        name: 'password',
                        id: 'password',
                    },
                }"
                :feedback="false"
            />
        </InputGroup>

        <InputGroup class="mb-3">
            <InputGroupAddon>
                <i class="pi pi-unlock"></i>
            </InputGroupAddon>
            <Password
                class="w-full"
                v-model="passwordConfirmation"
                toggleMask
                id="password_confirmation"
                type="password"
                name="password_confirmation"
                placeholder="Confirm Password"
                inputId="password_confirmation"
                inputName="password_confirmation"
                :inputProps="{ name: 'password_confirmation' }"
                :pt="{
                    input: {
                        type: 'password',
                        name: 'password_confirmation',
                        id: 'password_confirmation',
                    },
                }"
                :feedback="false"
                :invalid="!matching"
            />
        </InputGroup>
        <div v-if="!matching" class="text-red-500">
            Password confirmation does not match.
        </div>
        <PasswordRequirements
            :password="password"
            :password-confirmation="passwordConfirmation"
        />
    </div>
</template>
