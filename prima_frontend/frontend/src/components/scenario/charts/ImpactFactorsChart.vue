<script lang="ts" setup>
    import { ref, type PropType, watch } from 'vue';
    import { centerTextPlugin, type DoughnutChartOptionsWithCenterText } from '@/plugins/centerTextPlugin';
    import type { KpiData } from '@/types/kpi';
    import type { ImpactFactors } from '@/types/scenarioForm/impactFactor';
    import { generateColors, getDoughnutChartOptions } from '@/utils/chartUtils';
    import { convertKeyToLabel } from '@/utils/convertKeyToLabel';
    import { amountFromPercent } from '@/utils/percentage';

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

    const convertFactorsToChartData = (factorData: ImpactFactors) => {
        for (const [key, value] of Object.entries(factorData)) {
            if (!value.value || !value.selected) {
                continue;
            }

            const parentValue = value.value;
            const parentLabel = convertKeyToLabel(key);

            // Factors without Child Factors
            if (!value.childFactors) {
                labels.value.push(parentLabel);
                values.value.push(parentValue);
                continue;
            } else {
                // Factors with Child Factors
                for (const [childKey, childValue] of Object.entries(value.childFactors)) {
                    if (!childValue.value || !childValue.selected) {
                        continue;
                    }

                    const childLabel = convertKeyToLabel(childKey);
                    labels.value.push(`${parentLabel}: \n${childLabel}`);
                    const absoluteChildValue = amountFromPercent(childValue.value, parentValue);
                    values.value.push(absoluteChildValue);
                }
            }
        }
    };

    const setChartData = () => {
        if (!props.data?.impactFactors) {
            return null;
        }

        convertFactorsToChartData(props.data.impactFactors);
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
                    text: `${props.data?.overallImpactWeight ?? ''}`,
                    fontSize: 36,
                    color: 'black'
                }
            });
        }
    );
</script>

<template>
    <span
        ><div class="chart-container">
            <div class="chart-title">Impact Factors</div>

            <div class="h-[220px] w-[220px] pt-10 text-center" v-if="notApplicable">
                <div class="text-5xl">N/A</div>
            </div>

            <div v-else-if="!chartData || !chartOptions">
                <PSkeleton
                    shape="circle"
                    size="220px"
                    class="top-4"
                    :animation="data?.overallImpactWeight === null ? 'none' : 'wave'"
                />
            </div>

            <PChart
                pt:canvas:class="h-[220px] w-[220px]"
                v-else-if="chartData && chartOptions && data?.impactFactors"
                type="doughnut"
                :data="chartData"
                :options="chartOptions"
                :plugins="[centerTextPlugin]"
            />
        </div>
    </span>
</template>
