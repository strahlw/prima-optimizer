// src/plugins/centerTextPlugin.ts
import type { Chart, Plugin, ChartOptions } from 'chart.js';

interface CenterTextOptions {
    text?: string;
    fontSize?: number;
    color?: string;
    fontFamily?: string;
    xOffset?: number;
    yOffset?: number;
}

export type DoughnutChartOptionsWithCenterText = ChartOptions<'doughnut'> & {
    plugins?: {
        centerText?: CenterTextOptions;
    };
};

export const centerTextPlugin: Plugin<'doughnut'> = {
    id: 'centerText',
    beforeDraw(chart: Chart<'doughnut'>) {
        const { width, height, ctx } = chart;

        const opts = chart.config.options?.plugins?.centerText ?? {};

        const text = opts.text ?? '';
        const fontSize = opts.fontSize ?? 16;
        const fontColor = opts.color ?? '#000';
        const fontFamily = opts.fontFamily ?? 'Arial';
        const xOffset = opts.xOffset ?? 0;
        const yOffset = opts.yOffset ?? 0;

        ctx.save();
        ctx.font = `${fontSize}px ${fontFamily}`;
        ctx.fillStyle = fontColor;
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(text, width / 2 + xOffset, height / 2 + yOffset);
        ctx.restore();
    }
};
