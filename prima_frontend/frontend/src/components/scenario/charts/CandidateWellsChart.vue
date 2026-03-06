<script lang="ts" setup>
    import { ref, type PropType, watch } from 'vue';
    import { WellType } from '@/constants/wellEnums';
    import { centerTextPlugin, type DoughnutChartOptionsWithCenterText } from '@/plugins/centerTextPlugin';
    import type { KpiData } from '@/types/kpi';
    import { getDoughnutChartOptions } from '@/utils/chartUtils';

    const props = defineProps({
        data: {
            required: true,
            type: Object as PropType<KpiData | null>
        }
    });

    const chartData = ref();
    const chartOptions = ref<DoughnutChartOptionsWithCenterText | null>(null);

    watch(
        () => props.data,
        () => {
            if (!props.data) {
                return;
            }
            chartData.value = setChartData();
            chartOptions.value = getDoughnutChartOptions({
                centerText: {
                    text: `${props.data?.numCandidateWells}`,
                    fontSize: 36,
                    color: 'black'
                }
            });
        }
    );

    const setChartData = () => {
        const documentStyle = getComputedStyle(document.body);

        return {
            labels: [WellType.Oil, WellType.Gas, WellType.Combined],
            datasets: [
                {
                    data: [props.data?.numOilWells, props.data?.numGasWells, props.data?.numCombinedWells],
                    backgroundColor: [
                        documentStyle.getPropertyValue('--p-cyan-500'),
                        documentStyle.getPropertyValue('--p-orange-500'),
                        documentStyle.getPropertyValue('--p-gray-500')
                    ],
                    hoverBackgroundColor: [
                        documentStyle.getPropertyValue('--p-cyan-400'),
                        documentStyle.getPropertyValue('--p-orange-400'),
                        documentStyle.getPropertyValue('--p-gray-400')
                    ]
                }
            ]
        };
    };
</script>

<template>
    <div class="chart-container">
        <div class="chart-title"># of Candidate Wells</div>

        <div v-if="!chartData || !chartOptions">
            <PSkeleton shape="circle" size="220px" class="top-4" />
        </div>

        <PChart
            pt:canvas:class="h-[220px] w-[220px]"
            v-else-if="chartData && chartOptions"
            type="doughnut"
            :data="chartData"
            :options="chartOptions"
            :plugins="[centerTextPlugin]"
        />
    </div>
</template>
