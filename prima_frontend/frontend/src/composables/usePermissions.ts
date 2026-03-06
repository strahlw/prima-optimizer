import { useAuthStore } from '../stores/authStore';

export function usePermissions() {
    const authStore = useAuthStore();

    function hasRole(role: Array<string> | string): boolean {
        /// NOTE: Roles was originally an array, but this is likely not necessary
        if (Array.isArray(role)) {
            return role.some((r) => authStore.role === r);
        }

        return authStore.role === role;
    }

    function hasPermission(permission: Array<string> | string): boolean {
        if (Array.isArray(permission)) {
            return permission.some((p) => authStore.permissions.includes(p));
        }
        return authStore.permissions.includes(permission);
    }

    function belongsToOrganization(organizationKey: string): boolean {
        return authStore.organization.key === organizationKey;
    }

    return { hasRole, hasPermission, belongsToOrganization };
}
