export function percentage(partialValue: number, totalValue: number): number {
    return (100 * partialValue) / totalValue;
}

export function amountFromPercent(percentValue: number, totalValue: number, precision: number = 2): number {
    if (totalValue === 0) {
        return 0;
    }
    const amount = (percentValue * totalValue) / 100;
    return parseFloat(amount.toFixed(precision));
}
