<script setup lang="ts">
    import IconDownloading from '@/components/icons/IconDownloading.vue';
    import CreateScenarioSubHeading from '@/components/scenario/CreateScenarioSubHeading.vue';
    import ScenarioCopyAndEditDialog from '@/components/scenario/ScenarioCopyAndEditDialog.vue';
    import { useRouter } from 'vue-router';
    import { createRankingService } from '@/services/rankingService';
    import { useScenarioActions } from '@/composables/useScenarioActions';

    const props = defineProps<{
        scenarioId: number | null;
    }>();

    const subHeading = 'Your Scenario has been added to the Scenario Queue.';
    const rankService = createRankingService();
    const router = useRouter();

    const goToScenarioQueue = () => {
        rankService.resetRankingData();
        router.push('/scenario-queue');
    };

    const { scenarioToBeCopied, handleScenarioCopy, scenarioCopyVisible, handleCopyAndEditClick } =
        useScenarioActions();

    const handleCopyClick = () => {
        const id = props.scenarioId;
        if (typeof id === 'number') {
            handleCopyAndEditClick(id);
            return;
        }
    };
</script>

<template>
    <div class="flex-auto text-center">
        <ScenarioCopyAndEditDialog
            v-model:scenarioCopyVisible="scenarioCopyVisible"
            v-model:scenarioToBeCopied="scenarioToBeCopied"
            :handleScenarioCopy="handleScenarioCopy"
        />
        <CreateScenarioSubHeading :text="subHeading" />
        <div class="w-3/4 mx-auto">
            <h1 class="font-bold mt-10">Your Scenario has been added to the Queue</h1>
            <p>
                You may check the Scenario Queue page to see the status on your scenario, you may also run a new
                scenario
            </p>

            <div class="flex justify-center mt-6 flex-col gap-3">
                <div>
                    <PButton class="btn-primary mt-6 mb-2" @click="goToScenarioQueue">
                        <IconDownloading fillClass="fill-white" />
                        <span class="ml-2 text-white font-bold">Go to Queue</span>
                    </PButton>
                </div>
                <div>
                    <PButton class="btn-secondary" @click.stop="handleCopyClick" :disabled="!props.scenarioId">
                        <span>Copy & Edit Scenario Inputs</span>
                    </PButton>
                </div>
            </div>
        </div>
    </div>
</template>
