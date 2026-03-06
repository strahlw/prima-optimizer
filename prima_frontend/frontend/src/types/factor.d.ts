export interface Factor {
    value: number;
    selected: boolean;
    childFactors?: { [key: string]: Factor } | null;
    toolTip?: string;
}
