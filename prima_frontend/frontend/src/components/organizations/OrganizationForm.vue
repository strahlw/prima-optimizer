<script setup lang="ts">
    import { onMounted } from 'vue';

    import { useOrganizationFormStore } from '@/stores/form/organizationForm';
    import type { FileUploadSelectEvent } from 'primevue/fileupload';

    const organizationFormStore = useOrganizationFormStore();
    const { form, v$, resetForm } = organizationFormStore;

    const props = defineProps({
        edit: {
            type: Boolean,
            default: false
        }
    });

    const handleFileChange = (event: FileUploadSelectEvent) => {
        form.logo = event.files[0];
        v$.logo.$touch();
    };

    onMounted(() => {
        if (!props.edit) {
            resetForm();
        }
    });
</script>

<template>
    <div>
        <div>
            <label for="key" class="block mb-2 text-xs">Key:</label>
            <InputText
                v-model="form.key"
                inputId="key"
                id="key"
                placeholder="Key"
                class="w-full"
                type="text"
                @input="v$.key.$touch()"
                @blur="v$.key.$touch()"
            />
            <ValidationError :errors="organizationFormStore.v$.key.$errors" />
        </div>

        <div class="mt-4">
            <label for="name" class="block mb-2 text-xs">Name:</label>
            <InputText
                v-model="form.name"
                inputId="name"
                id="name"
                placeholder="Name"
                class="w-full"
                type="text"
                @input="v$.name.$touch()"
                @blur="v$.name.$touch()"
            />
            <ValidationError :errors="organizationFormStore.v$.name.$errors" />
        </div>

        <div class="mt-4">
            <label for="longitude" class="block mb-2 text-xs">Longitude:</label>
            <InputNumber
                v-model="form.longitude"
                inputId="longitude"
                id="longitude"
                class="w-full"
                placeholder="0"
                type="number"
                mode="decimal"
                @input="v$.longitude.$touch()"
                @blur="v$.longitude.$touch()"
                :minFractionDigits="2"
                :maxFractionDigits="7"
            />
            <ValidationError :errors="organizationFormStore.v$.longitude.$errors" />
        </div>

        <div class="mt-4">
            <label for="latitude" class="block mb-2 text-xs">Latitude:</label>
            <InputNumber
                v-model="form.latitude"
                inputId="latitude"
                id="latitude"
                class="w-full"
                placeholder="0"
                type="number"
                mode="decimal"
                @input="v$.latitude.$touch()"
                @blur="v$.latitude.$touch()"
                :minFractionDigits="2"
                :maxFractionDigits="7"
            />
            <ValidationError :errors="organizationFormStore.v$.latitude.$errors" />
        </div>

        <div class="mt-4">
            <label for="availableFunding" class="block mb-2 text-xs">Available Funding:</label>
            <InputNumber
                v-model="form.availableFunding"
                inputId="availableFunding"
                id="availableFunding"
                placeholder="$"
                class="w-full"
                mode="currency"
                currency="USD"
                locale="en-US"
                @input="v$.availableFunding.$touch()"
                @blur="v$.availableFunding.$touch()"
            />
            <ValidationError :errors="organizationFormStore.v$.availableFunding.$errors" />
        </div>

        <div class="mt-4">
            <label for="wellCount" class="block mb-2 text-xs">Well Count:</label>
            <InputNumber
                v-model="form.wellCount"
                inputId="wellCount"
                id="wellCount"
                class="w-full"
                placeholder="0"
                type="number"
                @input="v$.wellCount.$touch()"
                @blur="v$.wellCount.$touch()"
            />
            <ValidationError :errors="organizationFormStore.v$.wellCount.$errors" />
        </div>

        <div class="mt-4">
            <label for="paTarget" class="block mb-2 text-xs">PA Target</label>
            <InputNumber
                v-model="form.paTarget"
                inputId="paTarget"
                id="paTarget"
                placeholder="0"
                class="w-full"
                type="number"
                @input="v$.paTarget.$touch()"
                @blur="v$.paTarget.$touch()"
            />
            <ValidationError :errors="organizationFormStore.v$.paTarget.$errors" />
        </div>

        <div class="mt-4">
            <label for="name" class="block mb-2 text-xs">Logo:</label>
            <img v-if="form.logoUrl && edit" :src="form.logoUrl" />
            <FileUpload
                ref="fileUploadRef"
                mode="basic"
                name="logo"
                :customUpload="true"
                v-model="form.logo"
                :auto="false"
                inputId="logo"
                id="logo"
                @input="v$.logo.$touch()"
                @blur="v$.logo.$touch()"
                :maxFileSize="1000000"
                @select="handleFileChange"
            />
        </div>
    </div>
</template>
