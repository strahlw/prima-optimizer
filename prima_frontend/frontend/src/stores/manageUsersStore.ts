import { defineStore } from 'pinia';
import { createApiService } from '../services/apiService';
import { keysToCamelCase } from '../utils/toCamelCase';
import type { User } from '../types/user';

export const useManageUsersStore = defineStore('manageUsers', {
    state: () => ({
        users: Array<User>()
    }),
    persist: false,
    getters: {
        getUsers: (state) => state.users,
        getUserById: (state) => (id: number) => state.users.find((user) => user.id === id)
    },
    actions: {
        async fetchOrganizationUsers(organizationId: number) {
            try {
                // NOTE: Technically incorrect usage of inject() outside of a component
                const apiService = createApiService();
                const response = await apiService.get(`/api/user/${organizationId}`);
                if (response.data) {
                    this.users = keysToCamelCase(response.data.users);
                }
            } catch (error) {
                console.error('Error fetching organizations:', error);
            }
        },
        async fetchSuperAdmins() {
            try {
                // NOTE: Technically incorrect usage of inject() outside of a component
                const apiService = createApiService();
                const response = await apiService.get(`/api/user/supers`);
                if (response.data) {
                    this.users = keysToCamelCase(response.data.users);
                }
            } catch (error) {
                console.error('Error fetching organizations:', error);
            }
        }
    }
});
