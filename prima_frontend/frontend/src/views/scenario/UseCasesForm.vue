<script setup lang="ts">
    import { ScenarioFormTitle } from '@/constants/scenarioEnums';
    import { useScenarioFormStore } from '../../stores/form/scenarioForm';
    import { Message } from 'primevue';
    const scenarioFormStore = useScenarioFormStore();
    const { form } = scenarioFormStore;

    const items = [
        { icon: 'pi pi-chart-scatter', label: ScenarioFormTitle.WellRanking },
        { icon: 'pi pi-star-fill', label: ScenarioFormTitle.PAProjectRecommendations },
        { icon: 'pi pi-sitemap', label: ScenarioFormTitle.PAProjectComaprisons }
    ];

    const setSelectedCase = (selectedCase: string) => {
        // if (selectedCase === "Orphaned Well Ranking") {
        //     selectedCase = "Well Ranking";
        // }
        if (form.useCases.cases.includes(selectedCase)) {
            form.useCases.cases = form.useCases.cases.filter((item: string) => item !== selectedCase);
        } else {
            form.useCases.cases.push(selectedCase);
        }
    };
</script>

<template>
    <div class="flex justify-around space-x-8 mt-14 px-12">
        <div v-for="(item, index) in items" :key="index" class="flex flex-col items-center">
            <PCard
                :pt="{
                    root: {
                        class: 'flex flex-col items-center transition-all duration-300 rounded-lg h-60 w-60'
                    },
                    body: { class: 'p-4' }
                }"
                :class="{
                    'bg-blue-100': form.useCases.cases.includes(item.label),
                    'opacity-[0.6]': item.label === ScenarioFormTitle.PAProjectComaprisons,
                    'cursor-pointer': item.label !== ScenarioFormTitle.PAProjectComaprisons,
                    'cursor-not-allowed': item.label === ScenarioFormTitle.PAProjectComaprisons
                }"
                @click="item.label !== ScenarioFormTitle.PAProjectComaprisons ? setSelectedCase(item.label) : ''"
            >
                <template #content>
                    <div class="flex flex-col space-y-6 align-middle">
                        <div class="flex justify-center text-black">
                            <i :class="`${item.icon} text-6xl mt-4 icon`"></i>
                        </div>
                        <div class="flex justify-center">
                            <span class="mb-4 text-xl font-bold text-center break-words w-full px-2">{{
                                item.label
                            }}</span>
                        </div>
                    </div>
                </template>
            </PCard>
            <Message v-if="index === 2" severity="warn" class="w-60 mt-4"
                ><span class="text-sm">Under development!</span></Message
            >
        </div>
    </div>
</template>

<style scoped>
    .icon {
        color: #0092c3;
    }
    .disabled-icon {
        color: #a8aaad;
    }
</style>
