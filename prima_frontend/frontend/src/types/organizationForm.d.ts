export interface OrganizationForm {
    id?: number | null;
    key: string;
    name: string;
    logo: File | null;
    availableFunding: number;
    wellCount: number;
    paTarget: number;
    longitude: number;
    latitude: number;
    logoUrl?: string | null;
}
