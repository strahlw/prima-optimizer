<script lang="ts" setup>
    import { ref, type PropType, watch } from 'vue';
    import { centerTextPlugin, type DoughnutChartOptionsWithCenterText } from '@/plugins/centerTextPlugin';
    import type { KpiData } from '@/types/kpi';
    import { getDoughnutChartOptions } from '@/utils/chartUtils';
    import { formatCompactNumber } from '@/utils/formatNumber';

    const props = defineProps({
        data: {
            required: true,
            type: Object as PropType<KpiData | null>
        },
        isRankOnly: {
            required: false,
            default: false,
            type: Boolean
        }
    });

    const chartData = ref();
    const chartOptions = ref<DoughnutChartOptionsWithCenterText | null>(null);

    const setChartData = () => {
        if (!props.data?.cost || !props.data?.budgetRemaining) {
            return null;
        }

        const documentStyle = getComputedStyle(document.body);

        return {
            labels: ['Allocated', 'Unallocated'],
            datasets: [
                {
                    data: [props.data.cost, props.data.budgetRemaining],
                    backgroundColor: [
                        documentStyle.getPropertyValue('--p-orange-500'),
                        documentStyle.getPropertyValue('--p-gray-200')
                    ],
                    hoverBackgroundColor: [
                        documentStyle.getPropertyValue('--p-orange-400'),
                        documentStyle.getPropertyValue('--p-gray-100')
                    ]
                }
            ]
        };
    };

    watch(
        () => props.data,
        () => {
            if (!props.data) {
                return;
            }
            chartData.value = setChartData();
            chartOptions.value = getDoughnutChartOptions({
                tooltipLabelCallback: (context) => {
                    const formatter = new Intl.NumberFormat('en-US', {
                        style: 'currency',
                        currency: 'USD',
                        maximumFractionDigits: 0
                    });
                    return `${context.label}: ${formatter.format(Number(context.raw))}`;
                },
                centerText: {
                    text: `$${formatCompactNumber(props.data?.cost)}`,
                    fontSize: 36,
                    color: 'black'
                }
            });
        }
    );
</script>

<template>
    <div class="chart-container">
        <div class="chart-title">P&A Budget</div>

        <div v-if="(!chartData || !chartOptions) && !isRankOnly">
            <PSkeleton shape="circle" size="220px" class="top-4" />
        </div>

        <div class="h-[220px] w-[220px] pt-10 text-center" v-if="isRankOnly">
            <div class="text-5xl">N/A</div>
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
