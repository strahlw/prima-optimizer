import 'chart.js';

declare module 'chart.js' {
    interface PluginOptionsByType<TType extends string = string> {
        centerText?: {
            text?: string;
            fontSize?: number;
            color?: string;
            fontFamily?: string;
            xOffset?: number;
            yOffset?: number;
        };
    }
}
