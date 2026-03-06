export type Organization = {
    id: number;
    key: string;
    name: string;
    logo?: File;
    logoUrl?: string;
    availableFunding: number;
    wellCount: number;
    paTarget: number;
    latitude: number;
    longitude: number;
};
