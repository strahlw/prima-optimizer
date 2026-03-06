export function formatCompactNumber(value: number | null): string {
    if (!value) return '';
    if (value === null || value === undefined) return '';
    return Intl.NumberFormat('en', { notation: 'compact', maximumFractionDigits: 1 }).format(value);
}
