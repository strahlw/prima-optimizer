<script lang="ts" setup>
    import Dialog from 'primevue/dialog';

    defineProps({
        isOpen: {
            type: Boolean,
            required: true,
            default: false
        },
        message: {
            type: String,
            required: false,
            default: 'Exporting well data...'
        }
    });

    const visible = defineModel<boolean>('isOpen', {
        default: false
    });
</script>
<template>
    <Dialog
        v-model:visible="visible"
        modal
        :pt="{
            root: 'border-none',
            mask: {
                style: 'backdrop-filter: blur(2px)'
            }
        }"
        ><template #container>
            <div class="flex flex-col px-5 pb-5 bg-white max-w-lg">
                <h2>{{ message }}</h2>
                <ProgressSpinner /></div></template
    ></Dialog>
</template>
