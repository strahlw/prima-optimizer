<script setup lang="ts">
    import { ref, type PropType } from 'vue';
    import { Divider } from 'primevue';
    import ScenarioRenameDialog from '@/components/scenario/ScenarioRenameDialog.vue';
    import ScenarioCopyAndEditDialog from '@/components/scenario/ScenarioCopyAndEditDialog.vue';

    import type { MinimalDetailsScenario } from '@/types/scenario';
    import { useCollapse } from '@/composables/collapse';
    import { useScenarioActions } from '@/composables/useScenarioActions';
    import { convertKeyToLabel } from '@/utils/convertKeyToLabel';

    defineProps({
        scenario: {
            required: false,
            type: Object as PropType<MinimalDetailsScenario>
        },
        sideBySide: {
            required: false,
            type: Boolean,
            default: false
        },
        scenarioScreenLoading: {
            required: false,
            type: Boolean,
            default: false
        }
    });

    const { enter, leave } = useCollapse();

    const collapsed = ref(false);
    const generalCollapsed = ref(true);
    const impactCollapsed = ref(true);
    const efficiencyCollapsed = ref(true);

    function toggleCollapse() {
        collapsed.value = !collapsed.value;
    }

    const emit = defineEmits<{
        (e: 'scenarioRenamed', id: number, name: string): void;
    }>();

    const {
        scenarioIdBeingRenamed,
        scenarioToBeCopied,
        handleScenarioRename,
        handleScenarioCopy,
        canRenameScenario,
        scenarioRenameVisible,
        scenarioCopyVisible,
        handleCopyAndEditClick,
        handleRenameClick,
        newScenarioName
    } = useScenarioActions(() => {
        emit('scenarioRenamed', scenarioIdBeingRenamed.value!, newScenarioName.value);
    });
</script>

<template>
    <span>
        <ScenarioRenameDialog
            v-model:scenarioRenameVisible="scenarioRenameVisible"
            v-model:scenarioIdBeingRenamed="scenarioIdBeingRenamed"
            v-model:newScenarioName="newScenarioName"
            :handleScenarioRename="handleScenarioRename"
        />
        <ScenarioCopyAndEditDialog
            v-model:scenarioCopyVisible="scenarioCopyVisible"
            v-model:scenarioToBeCopied="scenarioToBeCopied"
            :handleScenarioCopy="handleScenarioCopy"
        />
        <div v-if="scenario" class="overflow-visible scenario-detail-view mb-4 p-4 rounded-lg max-w-full bg-white">
            <div
                class="flex flex-col py-0 h-auto relative"
                :class="!scenarioScreenLoading ? 'cursor-pointer' : ''"
                @click="scenarioScreenLoading ? '' : toggleCollapse()"
            >
                <div
                    v-if="scenarioScreenLoading"
                    class="absolute inset-0 flex items-center justify-center bg-white bg-opacity-75 rounded"
                >
                    <i class="pi pi-spin pi-spinner text-lg text-gray-500"></i>
                </div>
                <div class="flex flex-row text-center items-center">
                    <p class="font-bold text-2xl w-full">{{ scenario?.data.name }}</p>
                    <div class="justify-self-end items-center flex flex-row">
                        <i
                            class="justify-self-end mr-2"
                            :class="{
                                'pi pi-chevron-up': collapsed,
                                'pi pi-chevron-down': !collapsed,
                                'text-xs': sideBySide
                            }"
                        ></i>
                    </div>
                </div>
                <div class="flex flex-row gap-10 text-xl">
                    <div class="justify-self-start text-sm" :class="{ 'text-xs': sideBySide }">
                        <div>
                            <span>Uploaded By: </span>
                            <br v-if="sideBySide" />
                            <span class="italic">{{ scenario?.user?.firstName }} {{ scenario?.user?.lastName }}</span>
                        </div>

                        <div>
                            <span>Dataset: </span>
                            <br v-if="sideBySide" />
                            <span class="italic">{{ scenario?.dataset?.name }}</span>
                        </div>

                        <div>
                            <span v-if="scenario?.parent?.data">
                                <br />
                                <span
                                    >Child of:
                                    <router-link
                                        :to="{ path: `/scenarios/${scenario.parent?.id}`, hash: '#projects' }"
                                        target="_blank"
                                        class="router-link"
                                        >{{ scenario.parent?.data.name }}</router-link
                                    ></span
                                >
                            </span>
                        </div>

                        <div>
                            <span v-if="scenario.copyParent?.data">
                                <br />
                                <span
                                    >Modified based on:
                                    <router-link
                                        :to="{
                                            path: `/scenarios/${scenario.copyParent?.id}`,
                                            hash: '#projects'
                                        }"
                                        target="_blank"
                                        class="router-link"
                                        >{{ scenario.copyParent?.data.name }}</router-link
                                    ></span
                                >
                            </span>
                        </div>
                    </div>
                </div>
            </div>

            <div>
                <transition name="accordion" @enter="enter" @leave="leave">
                    <div v-if="!collapsed">
                        <div class="gap-4 mt-3">
                            <div class="flex flex-col gap-4">
                                <div class="flex flex-row justify-between gap-2">
                                    <PButton class="btn-secondary text-sm" @click="handleCopyAndEditClick(scenario.id)"
                                        >Copy & Edit Scenario Inputs</PButton
                                    >
                                    <PButton
                                        v-if="canRenameScenario(scenario)"
                                        class="btn-secondary text-sm"
                                        @click="handleRenameClick(scenario.id)"
                                        >Rename Scenario</PButton
                                    >
                                </div>
                                <div class="gap-4" :class="sideBySide ? 'flex flex-col' : 'grid grid-cols-2'">
                                    <PCard
                                        :pt="{
                                            root: { class: 'cursor-pointer', style: { height: 'fit-content' } },
                                            body: { class: 'py-3 px-4 flex-col mb-[-1rem]' },
                                            caption: { class: 'w-full' }
                                        }"
                                        @click="generalCollapsed = !generalCollapsed"
                                    >
                                        <template #title>
                                            <div class="flex w-full justify-between">
                                                <div class="text-base pb-2">General Specifications</div>
                                                <div class="text-primary items-center flex flex-row">
                                                    <i
                                                        class="justify-self-end"
                                                        :class="{
                                                            'pi pi-chevron-right': generalCollapsed,
                                                            'pi pi-chevron-down': !generalCollapsed,
                                                            'text-xs': sideBySide
                                                        }"
                                                    ></i>
                                                </div>
                                            </div>
                                        </template>

                                        <template #content>
                                            <transition name="general-accordion" @enter="enter" @leave="leave">
                                                <div v-if="!generalCollapsed" class="mt-[-1rem]">
                                                    <Divider />
                                                    <!-- TODO: Implement additional datasets -->
                                                    <div class="flex flex-col mb-4 gap-2 text-xs">
                                                        <div class="grid grid-cols-3 justify-between items-center">
                                                            <div class="col-span-2">Organization:</div>
                                                            <InputText
                                                                :disabled="true"
                                                                size="small"
                                                                :value="scenario.organization?.key"
                                                                :pt="{ root: { class: 'p-1' } }"
                                                                :v-tooltip="scenario.organization?.name"
                                                            ></InputText>
                                                        </div>
                                                        <div class="grid grid-cols-3 justify-between items-center">
                                                            <div class="col-span-2">Dataset:</div>
                                                            <InputText
                                                                :disabled="true"
                                                                size="small"
                                                                :value="scenario.dataset?.name"
                                                                :pt="{ root: { class: 'p-1' } }"
                                                                :v-tooltip="scenario.dataset?.name"
                                                            ></InputText>
                                                        </div>
                                                        <template
                                                            v-for="(value, key) in scenario.data.generalSpecifications"
                                                        >
                                                            <div
                                                                class="grid grid-cols-3 justify-between items-center"
                                                                v-if="key !== 'datasetId' && key !== 'organizationId'"
                                                                :key="key"
                                                            >
                                                                <div class="col-span-2">
                                                                    {{ convertKeyToLabel(key) }}:
                                                                </div>
                                                                <InputText
                                                                    :disabled="true"
                                                                    size="small"
                                                                    :value="value"
                                                                    :pt="{ root: { class: 'p-1' } }"
                                                                    :v-tooltip="value"
                                                                ></InputText>
                                                            </div>
                                                        </template>
                                                    </div></div
                                            ></transition>
                                        </template>
                                    </PCard>
                                    <PCard
                                        :pt="{
                                            root: { class: 'cursor-pointer', style: { height: 'fit-content' } },
                                            body: { class: 'py-3 px-4 flex-col mb-[-1rem]' },
                                            caption: { class: 'w-full' }
                                        }"
                                        v-if="scenario.data.impactFactors"
                                        @click="impactCollapsed = !impactCollapsed"
                                    >
                                        <template #title>
                                            <div class="flex w-full justify-between">
                                                <div class="text-base pb-2">Impact Factors</div>
                                                <div class="text-primary items-center flex flex-row">
                                                    <i
                                                        class="justify-self-end"
                                                        :class="{
                                                            'pi pi-chevron-right': impactCollapsed,
                                                            'pi pi-chevron-down': !impactCollapsed,
                                                            'text-xs': sideBySide
                                                        }"
                                                    ></i>
                                                </div>
                                            </div>
                                        </template>

                                        <template #content>
                                            <transition name="impact-accordion" @enter="enter" @leave="leave">
                                                <div v-if="!impactCollapsed" class="mt-[-1rem] mb-4">
                                                    <Divider />
                                                    <div class="flex flex-col gap-1.5 text-xs">
                                                        <template
                                                            v-for="(value, key) in scenario.data.impactFactors"
                                                            :key="key"
                                                        >
                                                            <div class="grid grid-cols-5 justify-between items-center">
                                                                <div class="col-span-4">
                                                                    {{ convertKeyToLabel(`${key}`) }}:
                                                                </div>
                                                                <InputText
                                                                    :disabled="true"
                                                                    size="small"
                                                                    :value="value.value"
                                                                    :pt="{ root: { class: 'p-1' } }"
                                                                ></InputText>
                                                            </div>
                                                            <template v-if="value.childFactors">
                                                                <ul class="flex flex-col gap-1 my-0">
                                                                    <template
                                                                        v-for="(
                                                                            childValue, childKey
                                                                        ) in value.childFactors"
                                                                        :key="childKey"
                                                                        ><li>
                                                                            <div
                                                                                class="grid grid-cols-5 justify-between items-center"
                                                                            >
                                                                                <div class="col-span-4">
                                                                                    {{
                                                                                        convertKeyToLabel(
                                                                                            `${key} - ${childKey}`
                                                                                        )
                                                                                    }}:
                                                                                </div>
                                                                                <InputText
                                                                                    :disabled="true"
                                                                                    size="small"
                                                                                    :value="childValue.value"
                                                                                    :pt="{
                                                                                        root: {
                                                                                            class: 'p-1 col-span-1'
                                                                                        }
                                                                                    }"
                                                                                ></InputText>
                                                                            </div>
                                                                        </li>
                                                                    </template>
                                                                </ul>
                                                            </template>
                                                        </template>
                                                    </div></div
                                            ></transition>
                                        </template>
                                    </PCard>
                                    <PCard
                                        :pt="{
                                            root: { class: 'cursor-pointer', style: { height: 'fit-content' } },
                                            body: { class: 'py-3 px-4 flex-col mb-[-1rem]' },
                                            caption: { class: 'w-full' }
                                        }"
                                        @click="efficiencyCollapsed = !efficiencyCollapsed"
                                        v-if="scenario.data.efficiencyFactors"
                                    >
                                        <template #title>
                                            <div class="flex w-full justify-between">
                                                <div class="text-base pb-2">Efficiency Factors</div>
                                                <div class="text-primary items-center flex flex-row">
                                                    <i
                                                        class="justify-self-end"
                                                        :class="{
                                                            'pi pi-chevron-right': efficiencyCollapsed,
                                                            'pi pi-chevron-down': !efficiencyCollapsed,
                                                            'text-xs': sideBySide
                                                        }"
                                                    ></i>
                                                </div>
                                            </div>
                                        </template>

                                        <template #content>
                                            <transition name="efficiency-accordion" @enter="enter" @leave="leave">
                                                <div v-if="!efficiencyCollapsed" class="mt-[-1rem] mb-4">
                                                    <Divider />
                                                    <div class="flex flex-col gap-1.5 text-xs">
                                                        <template
                                                            v-for="(value, key) in scenario.data.efficiencyFactors"
                                                            :key="key"
                                                        >
                                                            <div class="grid grid-cols-5 justify-between items-center">
                                                                <div class="col-span-4">
                                                                    {{ convertKeyToLabel(`${key}`) }}:
                                                                </div>
                                                                <InputText
                                                                    :disabled="true"
                                                                    size="small"
                                                                    :value="value.value"
                                                                    :pt="{ root: { class: 'p-1' } }"
                                                                ></InputText>
                                                            </div>
                                                        </template>
                                                    </div></div
                                            ></transition>
                                        </template>
                                    </PCard>
                                </div>
                            </div>
                        </div>
                    </div>
                </transition>
            </div>
        </div>
    </span>
</template>

<style scoped>
    .accordion-enter-active,
    .accordion-leave-active {
        transition: max-height 0.5s ease-in-out;
    }
    .accordion-enter,
    .accordion-leave-to {
        max-height: 0;
    }

    .p-card .p-card-body {
        /* flex-direction: row !important; */
        padding: 0.5rem;
    }
</style>
