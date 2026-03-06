export default function roundTo(value: number | null, precision: number = 0): number {
    if (value === null || value === undefined) {
        return 0;
    }
    const factor = 10 ** precision;
    return Math.round(value * factor) / factor;
}
