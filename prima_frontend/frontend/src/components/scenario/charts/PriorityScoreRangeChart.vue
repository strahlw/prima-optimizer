<script lang="ts" setup>
    import { type PropType } from 'vue';
    import type { KpiData } from '@/types/kpi';
    import SpeedometerChart from './SpeedometerChart.vue';
    import roundTo from '@/utils/roundTo';

    defineProps({
        data: {
            required: true,
            type: Object as PropType<KpiData | null>
        }
    });
</script>

<template>
    <div class="chart-container">
        <div class="chart-title">Priority/Impact Score Range</div>

        <div v-if="!data" class="overflow-hidden justify-center flex h-[126px]">
            <PSkeleton shape="circle" size="200px" class="top-6" />
        </div>

        <SpeedometerChart
            v-else
            :avg="roundTo(data.priorityImpactScoreAvg)"
            :min="roundTo(data.priorityImpactScoreMin)"
            :max="roundTo(data.priorityImpactScoreMax)"
        />
    </div>
</template>
