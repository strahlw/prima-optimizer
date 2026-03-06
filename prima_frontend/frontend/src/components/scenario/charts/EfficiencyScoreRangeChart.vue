<script lang="ts" setup>
    import { type PropType, computed } from 'vue';
    import type { KpiData } from '@/types/kpi';
    import SpeedometerChart from './SpeedometerChart.vue';
    import roundTo from '@/utils/roundTo';

    const props = defineProps({
        data: {
            required: true,
            type: Object as PropType<KpiData | null>
        }
    });

    const visible = computed<boolean>(() => {
        return (
            props.data?.efficiencyScoreMin !== null &&
            props.data?.efficiencyScoreMax !== null &&
            props.data?.efficiencyScoreAvg !== null
        );
    });
</script>

<template>
    <div class="chart-container">
        <div class="chart-title">Efficiency Score Range</div>
        <div class="overflow-hidden flex h-[126px]" v-if="!data">
            <PSkeleton shape="circle" size="200px" class="top-6" />
        </div>

        <SpeedometerChart
            v-else-if="visible"
            :avg="roundTo(data?.efficiencyScoreAvg)"
            :min="roundTo(data?.efficiencyScoreMin)"
            :max="roundTo(data?.efficiencyScoreMax)"
        />

        <div class="h-[220px] w-[220px] pt-10" v-else>
            <div class="text-5xl">N/A</div>
        </div>
    </div>
</template>
