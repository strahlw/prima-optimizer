import { useUserFormStore } from '../stores/form/userForm';
import { createApiService } from './apiService';
import { useToast } from 'primevue/usetoast';
import { keysToCamelCase } from '../utils/toCamelCase';

export function createUserManagementService() {
    const userFormStore = useUserFormStore();
    const apiService = createApiService();
    const toast = useToast();
    const { form } = userFormStore;

    const createUser = async () => {
        try {
            toast.removeAllGroups();
            const data = form;

            if (form.organizationId === 0) {
                data.organizationId = null;
            }

            const response = await apiService.post('/api/user', data);

            if (response.status === 200) {
                toast.add({
                    severity: 'success',
                    summary: 'Success',
                    detail: 'User created successfully. They have been sent an email with instructions for completing account registration.',
                    life: 5000
                });
                return keysToCamelCase(response.data.user);
            }
        } catch (error: any) {
            const errorData = error.response.data.errors;
            toast.add({
                severity: 'error',
                summary: 'Error',
                detail:
                    error.response.status === 403
                        ? error.response.data.message
                        : 'An error occurred while creating a user.',
                life: 5000
            });

            if (errorData) {
                userFormStore.setExternalResults(keysToCamelCase(errorData));
            }
        }
    };

    const updateUser = async () => {
        try {
            toast.removeAllGroups();
            const data = form;
            const response = await apiService.put(`/api/user/${form.id}`, data);

            if (response.status === 200) {
                toast.add({
                    severity: 'success',
                    summary: 'Success',
                    detail: 'User updated successfully.',
                    life: 5000
                });
                return keysToCamelCase(response.data.user);
            }
        } catch (error: any) {
            const errorData = error.response.data.errors;
            toast.add({
                severity: 'error',
                summary: 'Error',
                detail:
                    error.response.status === 403
                        ? error.response.data.message
                        : 'An error occurred while update the user.',
                life: 5000
            });

            if (errorData) {
                userFormStore.setExternalResults(errorData);
            }
        }
    };

    const deleteUser = async (id: number) => {
        try {
            toast.removeAllGroups();
            const response = await apiService.delete(`/api/user/${id}`);

            if (response.status === 200) {
                toast.add({
                    severity: 'success',
                    summary: 'Success',
                    detail: 'User deleted successfully.',
                    life: 5000
                });
                return response;
            } else if (response.status === 403) {
                return response;
            }
        } catch (error: any) {
            toast.add({
                severity: 'error',
                summary: 'Error',
                detail:
                    error.response.status === 403
                        ? error.response.data.message
                        : 'An error occurred while deleting the user.',
                life: 5000
            });

            return error;
        }
    };

    return {
        createUser,
        updateUser,
        deleteUser
    };
}
