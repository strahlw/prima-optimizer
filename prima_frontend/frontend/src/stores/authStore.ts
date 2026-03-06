import { defineStore } from 'pinia';
import type { Role } from '../types/role';
import { createApiService } from '../services/apiService';
import type { User } from '../types/user';
import type { Organization } from '../types/organization';

export const useAuthStore = defineStore('auth', {
    state: () => ({
        user: null as User | null, // TODO: Trim down storing roles, orgs, permissions separately, instead storing these all at the user level
        codeVerifier: '',
        codeChallenge: '',
        state: '',
        accessToken: '',
        refreshToken: '',
        expiryTime: 0,
        role: '',
        permissions: [] as string[],
        organization: {} as Organization,
        availbleRoles: [] as Role[],
        availableRolesFetched: false
    }),
    persist: true,
    getters: {
        isAuthenticated: (state) => !!state.accessToken,
        isSuperAdmin: (state) => state.role === 'super-admin',
        isOrgAdmin: (state) => state.role === 'org-admin',
        getUser: (state) => state.user,
        getCodeVerifier: (state) => state.codeVerifier,
        getCodeChallenge: (state) => state.codeChallenge,
        getState: (state) => state.state,
        getAccessToken: (state) => state.accessToken,
        getRefreshToken: (state) => state.refreshToken,
        getExpiryTime: (state) => state.expiryTime, // Currently not in use
        getOrganization: (state) => state.organization,
        getAvailableRoles: (state) => state.availbleRoles
    },
    actions: {
        login(token: string, user: any) {
            this.accessToken = token;
            this.user = user;
        },
        logout() {
            this.accessToken = '';
            this.refreshToken = '';
            this.user = null;
        },
        setCodeVerifier(codeVerifier: string) {
            this.codeVerifier = codeVerifier;
        },
        setCodeChallenge(codeChallenge: string) {
            this.codeChallenge = codeChallenge;
        },
        setState(state: string) {
            this.state = state;
        },
        setAccessToken(accessToken: string) {
            this.accessToken = accessToken;
        },
        setRefreshToken(refreshToken: string) {
            this.refreshToken = refreshToken;
        },
        setExpiryTime(expiryTime: number) {
            this.expiryTime = expiryTime;
        },
        setRole(role: string) {
            this.role = role;
        },
        setPermissions(permissions: Array<string>) {
            this.permissions = permissions;
        },
        setOrganization(organization: Organization) {
            this.organization = organization;
        },
        setUser(user: User) {
            this.user = user;
        },
        async fetchAvailableRoles(override = false) {
            if (this.availableRolesFetched && !override) return;
            try {
                // NOTE: Technically incorrect usage of inject() outside of a component
                const apiService = createApiService();
                const response = await apiService.get('/api/role');
                if (response.data && response.data.roles) {
                    this.availbleRoles = response.data.roles;
                    this.availableRolesFetched = true;
                }
            } catch (error) {
                console.error('Error fetching available roles:', error);
            }
        }
    }
});
