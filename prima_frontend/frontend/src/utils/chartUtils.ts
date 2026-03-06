import type { ChartOptions, TooltipItem } from 'chart.js';
import { baseColorFamilies, shadeVariants } from '@/constants/chartConstants';

export interface CenterTextOptions {
    text: string;
    fontSize?: number;
    color?: string;
    yOffset?: number;
    xOffset?: number;
}

export interface DoughnutChartOptionsParams {
    centerText?: CenterTextOptions;
    tooltipLabelCallback?: ((context: TooltipItem<'doughnut'>) => string) | null;
    cutout?: string;
}

export function getDoughnutChartOptions({
    centerText,
    tooltipLabelCallback,
    cutout = '65%'
}: DoughnutChartOptionsParams = {}): ChartOptions<'doughnut'> {
    const tooltipCallbacks = tooltipLabelCallback
        ? {
              callbacks: {
                  label: tooltipLabelCallback
              }
          }
        : {};

    return {
        cutout,
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                display: false
            },
            tooltip: tooltipCallbacks,
            centerText: centerText
                ? {
                      ...centerText
                  }
                : undefined
        },
        layout: {
            padding: 0
        }
    };
}

const getTopLevelFactor = (label: string): string =>
    label.includes(' - ') ? label.split(' - ')[0].trim() : label.trim();

const hashToIndex = (input: string, max: number): number => {
    let hash = 0;
    for (let i = 0; i < input.length; i++) {
        hash = input.charCodeAt(i) + ((hash << 5) - hash);
    }
    return Math.abs(hash) % max;
};

export const generateColors = (labels: string[], documentStyle: CSSStyleDeclaration) => {
    const topLevelToFamilyIndex: Record<string, number> = {};
    const prefixCounts: Record<string, number> = {};
    const bgColors: string[] = [];
    const hoverColors: string[] = [];

    let nextFamilyIndex = 0;

    for (const label of labels) {
        const topLevel = getTopLevelFactor(label);

        if (!(topLevel in topLevelToFamilyIndex)) {
            topLevelToFamilyIndex[topLevel] = nextFamilyIndex;
            nextFamilyIndex++;

            if (nextFamilyIndex >= baseColorFamilies.length) {
                console.warn(`⚠️ Not enough color families to assign a unique one to: ${topLevel}`);
                nextFamilyIndex = 0; // Start cycling through again
            }
        }

        const familyIndex = topLevelToFamilyIndex[topLevel];
        const baseVar = baseColorFamilies[familyIndex];

        const siblingIndex = prefixCounts[topLevel] ?? 0;
        prefixCounts[topLevel] = siblingIndex + 1;

        const shade = shadeVariants[siblingIndex % shadeVariants.length];
        const hoverShade = shadeVariants[(siblingIndex + 1) % shadeVariants.length];

        const bgColor = documentStyle.getPropertyValue(`${baseVar}-${shade}`).trim();
        const hoverColor = documentStyle.getPropertyValue(`${baseVar}-${hoverShade}`).trim();

        bgColors.push(bgColor || '#ccc');
        hoverColors.push(hoverColor || '#aaa');
    }

    return { bgColors, hoverColors };
};
