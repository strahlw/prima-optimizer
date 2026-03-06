<script setup lang="ts">
    // Use: https://primevue.org/fileupload/
    import { ref, onMounted } from 'vue';
    import { usePrimeVue } from 'primevue/config';
    import { createDatasetService } from '@/services/datasetService';
    import { useAuthStore } from '../../stores/authStore';
    import { useOrganizationStore } from '../../stores/organizationStore';
    import type { FileUploadSelectEvent } from 'primevue/fileupload';
    import Message from 'primevue/message';
    import Dialog from 'primevue/dialog';
    import ProgressSpinner from 'primevue/progressspinner';
    import Divider from 'primevue/divider';

    const $primevue = usePrimeVue();
    const totalSize = ref(0);
    const totalSizePercent = ref(0);
    const files = ref<any>([]);
    const datasetService = createDatasetService();
    const fileErrors = ref<any>({});
    const uploadErrors = ref<any>({});
    const uploadedFiles = ref<string[]>([]);
    const authStore = useAuthStore();
    const organizationStore = useOrganizationStore();
    const organizationId = ref<number | null>(null);
    const missingOrganizationError = ref(false);
    const loading = ref(false);
    const additionalData = ref(false);

    /** START: Finalized methods */
    const onClearFiles = () => {
        files.value = [];
        totalSize.value = 0;
    };

    const onRemoveFile = (file: any) => {
        files.value = files.value.filter((f: File) => f !== file);
        totalSize.value -= parseInt(formatSize(file.size));
        totalSizePercent.value = totalSize.value / 10;
    };

    const resetErrors = () => {
        fileErrors.value = {};
        uploadErrors.value = {};
        uploadedFiles.value = [];
        missingOrganizationError.value = false;
    };

    const uploadEvent = async () => {
        // TODO: Handle multiple files (?)
        loading.value = true;
        resetErrors();
        if (files.value.length > 0 && organizationId.value) {
            const response = await datasetService.uploadFile(
                files.value[0],
                organizationId.value,
                additionalData.value
            );

            if (response.status === 403) {
                fileErrors.value = response.data.errors;
            }

            if (response.status === 422) {
                uploadErrors.value = response.data.errors;
            }

            if (response.status === 500) {
                uploadErrors.value = response.data.errors;
            }

            if (response.status === 201) {
                uploadedFiles.value = response.data.files;
                if (uploadedFiles.value.length > 0) {
                    const newFileList = files.value.filter((file: any) => !uploadedFiles.value.includes(file.name));
                    files.value = newFileList;
                }
            }

            if (response.status === 202) {
                uploadedFiles.value = response.data.files;
                if (uploadedFiles.value.length > 0) {
                    const newFileList = files.value.filter((file: any) => !uploadedFiles.value.includes(file.name));
                    files.value = newFileList;
                }
            }

            loading.value = false;
        }
    };

    const onSelectedFiles = async (event: FileUploadSelectEvent) => {
        resetErrors();

        if (!organizationId.value) {
            missingOrganizationError.value = true;
        }

        files.value = event.files;
        files.value.forEach(async (file: any) => {
            totalSize.value += parseInt(formatSize(file.size));
        });
    };

    const getImportTemplate = async () => {
        await datasetService.getImportTemplate();
    };
    /** END: Finalized methods */

    const formatSize = (bytes: number) => {
        const k = 1024;
        const dm = 3;
        const sizes = $primevue.config.locale?.fileSizeTypes || [];

        if (bytes === 0) {
            return `0 ${sizes[0]}`;
        }

        const i = Math.floor(Math.log(bytes) / Math.log(k));
        const formattedSize = parseFloat((bytes / Math.pow(k, i)).toFixed(dm));

        return `${formattedSize} ${sizes[i]}`;
    };

    onMounted(() => {
        if (!authStore.isSuperAdmin) {
            organizationId.value =
                organizationStore.getOrganizations.find((org) => org.key === authStore.getOrganization.key)?.id || null;
        }
    });
</script>

<template>
    <div>
        <div class="flex flex-col w-100 mt-10 items-center">
            <div class="flex justify-center flex-col w-[75%] self-center">
                <h1 class="text-center mb-8">Upload Well Data</h1>
                <div v-if="authStore.isSuperAdmin" class="flex flex-col w-[50%] justify-center mx-auto mb-4">
                    <p class="mb-4">Choose an organization to associate the file with*:</p>
                    <PSelect
                        :disabled="!authStore.isSuperAdmin"
                        :options="organizationStore.getOrganizations"
                        optionLabel="key"
                        optionValue="id"
                        v-model="organizationId"
                    ></PSelect>
                    <p v-if="missingOrganizationError" class="text-sm text-red-500">Organization is required</p>
                </div>

                <div class="flex justify-between items-center mt-6 mb-4">
                    <h2>Upload Well Data Files</h2>
                    <PButton class="btn-primary h-10" @click="getImportTemplate">
                        <span class="pi pi-download" />
                        <span class="ml-2">Excel Template</span>
                    </PButton>
                </div>
                <div class="flex w-100 mt-2 mb-4">
                    <p class="">
                        Upload a csv or excel file of your <strong>Well Data</strong> for you and your team to access.
                        You may also upload additional files to add conditional constraints.
                    </p>
                </div>
                <div class="flex justify-start items-center space-x-2 mb-4">
                    <PCheckbox v-model="additionalData" :binary="true" />
                    <label class="text">Additional Data for uploaded file</label>
                </div>
            </div>

            <div class="flex justify-center flex-col w-[75%] self-center">
                <FileUpload
                    name="file[]"
                    :auto="true"
                    customUpload
                    :multiple="false"
                    accept=".csv,.xlsx"
                    @select="onSelectedFiles"
                    :pt="{
                        chooseButton: { class: 'btn-primary' },
                        removeButton: { class: 'bg-red-500' },
                        fileName: { class: 'font-bold' },
                        uploadCallback: { class: 'btn-primary' }
                    }"
                    :previewWidth="0"
                >
                    <template #header="{ chooseCallback }">
                        <div class="flex flex-wrap justify-content-between align-items-center flex-1 gap-2">
                            <div class="flex gap-2">
                                <PButton
                                    @click="chooseCallback()"
                                    icon="pi pi-plus"
                                    severity="success"
                                    label="Choose"
                                ></PButton>
                                <PButton
                                    @click="uploadEvent()"
                                    :disabled="!files || files.length === 0 || !organizationId"
                                    icon="pi pi-cloud-upload"
                                    label="Upload Datasets"
                                    severity="primary"
                                ></PButton>
                                <PButton severity="danger" label="Clear" @click="onClearFiles()"></PButton>
                                <!-- <PButton
                                @click="clearCallback()"
                                icon="pi pi-times"
                                rounded
                                outlined
                                severity="danger"
                                :disabled="!files || files.length === 0"
                            ></PButton> -->
                            </div>
                            <!-- <ProgressBar
                            :value="totalSizePercent"
                            :showValue="false"
                            :class="[
                                'md:w-20rem h-1rem w-full md:ml-auto',
                                { 'exceeded-progress-bar': totalSizePercent > 100 }
                            ]"
                        >
                            <span class="white-space-nowrap">{{ totalSize }}B / 1Mb</span></ProgressBar
                        > -->
                        </div>
                    </template>
                    <template #content>
                        <div class="flex flex-col align-items-center text-center" v-if="files.length > 0"></div>

                        <div v-if="files.length > 0" class="flex flex-col items-center">
                            <div class="flex flex-wrap p-0 sm:p-5 gap-5">
                                <div
                                    v-for="file of files"
                                    :key="file.name + file.type + file.size"
                                    class="card m-0 px-6 flex flex-column border-1 surface-border align-items-center gap-3 justify-center items-center"
                                >
                                    <span class="font-bold">{{ file.name }}</span>
                                    <div>{{ formatSize(file.size) }}</div>
                                    <PButton
                                        icon="pi pi-times"
                                        @click="onRemoveFile(file)"
                                        outlined
                                        rounded
                                        severity="danger"
                                    />
                                </div>
                            </div>
                            <Divider />
                        </div>
                    </template>
                    <template #empty>
                        <div
                            class="flex flex-col align-items-center text-center justify-content-center flex-column mb-10"
                            v-if="files.length === 0"
                        >
                            <i
                                class="pi pi-cloud-upload border-2 border-circle p-2 text-8xl text-400 border-400 text-primary"
                            />
                            <p class="my-4">Drag and drop a dataset to add.</p>
                        </div>
                    </template>
                </FileUpload>
            </div>

            <div v-if="uploadedFiles.length > 0" class="flex flex-col w-[50%] self-center mt-6">
                <Message severity="success" :closable="false" :pt="{ icon: { style: 'display:none;' } }">
                    <h3>Dataset files uploaded:</h3>
                    <ul>
                        <li v-for="file in uploadedFiles" :key="file">
                            <span>{{ file }}</span>
                        </li>
                    </ul>
                </Message>
            </div>

            <div v-if="fileErrors && Object.keys(fileErrors).length" class="flex flex-col w-[50%] self-center mt-6">
                <Message severity="error" :closable="false" :pt="{ icon: { style: 'display:none;' } }">
                    <h3 class="text-red-500">Errors occurred during the upload</h3>
                    <p class="text-red-500 text-sm">
                        Please review and correct the following fields, and try uploading again:
                    </p>
                    <ul>
                        <li v-for="error in fileErrors" :key="error">
                            <span class="text-red-500">{{ error }}</span>
                        </li>
                    </ul>
                </Message>
            </div>

            <div v-if="uploadErrors && Object.keys(uploadErrors).length" class="flex flex-col w-[50%] self-center mt-6">
                <Message severity="error" :closable="false" :pt="{ icon: { style: 'display:none;' } }">
                    <ul>
                        <li v-for="error in uploadErrors" :key="error">
                            <span class="text-red-500">{{ error[0] }}</span>
                        </li>
                    </ul>
                </Message>
            </div>
        </div>
        <Dialog v-model:visible="loading" modal header="Uploading dataset(s), do not exit, this may take a moment...">
            <div class="flex justify-center items-center">
                <ProgressSpinner />
            </div>
        </Dialog>
    </div>
</template>
