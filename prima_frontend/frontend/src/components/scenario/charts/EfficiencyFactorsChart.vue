<script lang="ts" setup>
    import { ref, type PropType, watch } from 'vue';
    import { centerTextPlugin, type DoughnutChartOptionsWithCenterText } from '@/plugins/centerTextPlugin';
    import type { KpiData } from '@/types/kpi';
    import { generateColors } from '@/utils/chartUtils';
    import { getDoughnutChartOptions } from '@/utils/chartUtils';
    import { convertKeyToLabel } from '@/utils/convertKeyToLabel';
    import type { EfficiencyFactors } from '@/types/scenarioForm/efficiencyFactor';

    const props = defineProps({
        data: {
            required: true,
            type: Object as PropType<KpiData | null>
        },
        notApplicable: {
            required: false,
            default: false,
            type: Boolean
        }
    });

    const chartData = ref();
    const chartOptions = ref<DoughnutChartOptionsWithCenterText | null>(null);
    const documentStyle = getComputedStyle(document.body);
    const labels = ref<string[]>([]);
    const values = ref<number[]>([]);

    const convertFactorsToChartData = (factorData: EfficiencyFactors) => {
        for (const [key, value] of Object.entries(factorData)) {
            if (!value.value || !value.selected) {
                continue;
            }

            labels.value.push(convertKeyToLabel(key));
            values.value.push(value.value);
        }
    };

    const setChartData = () => {
        if (!props.data?.efficiencyFactors) {
            return null;
        }

        convertFactorsToChartData(props.data.efficiencyFactors);
        const { bgColors, hoverColors } = generateColors(labels.value, documentStyle);

        return {
            labels,
            datasets: [
                {
                    data: values.value,
                    backgroundColor: bgColors,
                    hoverBackgroundColor: hoverColors
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
                centerText: {
                    text: `${props.data.overallEfficiencyWeight ?? ''}`,
                    fontSize: 36,
                    color: 'black'
                }
            });
        }
    );
</script>

<template>
    <span>
        <div class="chart-container">
            <div class="chart-title">Efficiency Factors</div>

            <div class="h-[220px] w-[220px] pt-10 text-center" v-if="notApplicable">
                <div class="text-5xl">N/A</div>
            </div>

            <div v-else-if="!chartData || !chartOptions">
                <PSkeleton
                    shape="circle"
                    size="220px"
                    class="top-4"
                    :animation="data?.overallEfficiencyWeight === null ? 'none' : 'wave'"
                />
            </div>

            <PChart
                pt:canvas:class="h-[220px] w-[220px]"
                v-else-if="chartData && chartOptions && data?.efficiencyFactors"
                type="doughnut"
                :data="chartData"
                :options="chartOptions"
                :plugins="[centerTextPlugin]"
            />
        </div>
    </span>
</template>
