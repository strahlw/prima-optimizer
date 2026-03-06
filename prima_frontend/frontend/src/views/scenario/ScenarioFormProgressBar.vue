<script setup lang="ts">
    import type { MenuItem } from 'primevue/menuitem';
    import Divider from 'primevue/divider';

    const props = defineProps<{
        steps: Array<MenuItem>;
        activeStep: string;
        rankOnly: boolean;
        optimizationOnly: boolean;
    }>();

    const stepDisabled = (step: string): boolean => {
        if (props.optimizationOnly) {
            return (
                props.optimizationOnly && ['impact-factors', 'well-ranking', 'pa-project-comparisons'].includes(step)
            );
        }

        if (props.rankOnly) {
            return ['efficiency-factors', 'pa-project-recommendations', 'pa-project-comparisons'].includes(step);
        }

        return false;
    };

    const getClass = (targetStep: string, type: string) => {
        const activeIndex = props.steps.findIndex((step) => step.key === props.activeStep);
        const targetIndex = props.steps.findIndex((step) => step.key === targetStep);
        const forIcon = type === 'icon';
        let computedClass = '';

        if (activeIndex === -1 || targetIndex === -1) {
            computedClass = '';
        } else if (targetIndex < activeIndex) {
            computedClass = forIcon ? 'bg-primary text-primary' : 'border-primary';
        } else if (targetIndex === activeIndex) {
            computedClass = forIcon ? 'bg-primary text-white' : 'border-primary';
        } else {
            computedClass = forIcon ? 'bg-gray-300 text-gray-300' : 'border-gray-300';
        }

        if (stepDisabled(targetStep)) {
            computedClass += ' disabled';
        }

        return computedClass;
    };
</script>

<template>
    <div class="progress-container mt-10 mr-10">
        <PCard :pt="{ root: { class: 'flex flex-col items-center' } }">
            <template #header>
                <div class="flex justify-center w-full">
                    <h1 class="max-w-72 flex-wrap overflow-hidden w-full text-center">Running New Scenario</h1>
                </div>
            </template>
            <template #content>
                <div v-for="(step, index) in steps" :key="step.key" class="flex flex-col items-center">
                    <div class="circle" :class="getClass(step.key || '', 'icon')">
                        <i :class="'text-2xl pi ' + step.icon" />
                    </div>
                    <div
                        class="font-bold text-sm text-center"
                        :class="stepDisabled(step.key || '') ? 'text-gray-300' : ''"
                    >
                        {{ step.label }}
                    </div>
                    <div class="flex flex-col divider-container mb-2">
                        <Divider
                            layout="vertical"
                            type="solid"
                            :pt="{
                                root: {
                                    class:
                                        'my-3 flex flex-col justify-center flex-1 ' +
                                        getClass(step.key || '', 'divider')
                                }
                            }"
                            v-if="index !== steps.length - 1"
                        />
                    </div>
                </div>
            </template>
        </PCard>
    </div>
</template>

<style scoped>
    .progress-container {
        position: sticky;
        top: 10px;
    }

    .circle {
        width: 50px;
        height: 50px;
        border-radius: 50%;
        display: flex;
        justify-content: center;
        align-items: center;
    }

    .p-divider.p-component::before {
        border-width: 4px;
        border-style: solid !important;
        border-left-style: none !important;
        left: 40%;
    }

    .p-divider.p-component.border-primary::before {
        border-color: #0092c3;
    }

    .p-divider.p-component.border-gray-300::before {
        border-color: #d1d5da;
    }

    .disabled {
        background-color: #f3f4f6;
        color: #f3f4f6;
    }
</style>
