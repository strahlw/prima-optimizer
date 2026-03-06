import { useOrganizationFormStore } from '../stores/form/organizationForm';
import { createApiService } from './apiService';
import { createToastService } from './toastService';

export function createOrganizationManagementService() {
    const organizationFormStore = useOrganizationFormStore();
    const apiService = createApiService();
    const { form } = organizationFormStore;
    const { toastError, toastSuccess, removeAllToast } = createToastService();

    const createOrganization = async () => {
        try {
            removeAllToast();
            const formData = new FormData();
            formData.append('key', form.key);
            formData.append('name', form.name);
            formData.append('longitude', form.longitude ? form.longitude.toString() : '');
            formData.append('latitude', form.latitude ? form.latitude.toString() : '');
            formData.append('availableFunding', form.availableFunding.toString());
            formData.append('wellCount', form.wellCount.toString());
            formData.append('paTarget', form.paTarget.toString());

            if (form.logo && form.logo instanceof File) {
                formData.append('logo', form.logo);
            }

            const response = await apiService.post('/api/organization', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data'
                }
            });

            if (response.status === 200) {
                toastSuccess('Organization created successfully.');
                return response.data;
            }
        } catch (error: any) {
            toastError(
                error.response.status === 403
                    ? error.response.data.message
                    : 'An error occurred while creating an organization.'
            );
        }
    };

    const updateOrganization = async () => {
        try {
            removeAllToast();
            const formData = new FormData();
            formData.append('key', form.key);
            formData.append('name', form.name);
            formData.append('longitude', form.longitude ? form.longitude.toString() : '');
            formData.append('latitude', form.latitude ? form.latitude.toString() : '');
            formData.append('availableFunding', form.availableFunding ? form.availableFunding.toString() : '');
            formData.append('wellCount', form.wellCount ? form.wellCount.toString() : '');
            formData.append('paTarget', form.paTarget ? form.paTarget.toString() : '');

            if (form.logo && form.logo instanceof File) {
                formData.append('logo', form.logo);
            }

            // Using post request because Laravel was having issue with multi-part and post
            const response = await apiService.post(`/api/organization/${form.id}`, formData, {
                headers: {
                    'Content-Type': 'multipart/form-data'
                }
            });

            if (response.status === 200) {
                toastSuccess('Organization updated successfully.');
                return response.data;
            }
        } catch (error: any) {
            console.error(error);
            toastError(
                error.response.status === 403
                    ? error.response.data.message
                    : 'An error occurred while updating an organization.'
            );
        }
    };

    const deleteOrganization = async (id: number) => {
        try {
            removeAllToast;
            const response = await apiService.delete(`/api/organization/${id}`);

            if (response.status === 200) {
                toastSuccess('Organization deleted successfully.');
                return response.data.id;
            }
        } catch (error: any) {
            const errorMessage =
                error.response.status === 403
                    ? error.response.data.message
                    : 'An error occurred while deleting the organization.';
            toastError(errorMessage);
        }
    };

    return {
        createOrganization,
        updateOrganization,
        deleteOrganization
    };
}
