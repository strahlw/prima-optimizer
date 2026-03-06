export type User = {
    id: number;
    firstName: string;
    lastName: string;
    email: string;
    roleId: number;
    organizationId: number | null;
    accountVerified: boolean;
    roleName?: string | null;
    showDisclaimer: boolean;
};
