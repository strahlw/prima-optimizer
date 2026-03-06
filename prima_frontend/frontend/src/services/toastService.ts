import { useToast } from 'primevue/usetoast';

export function createToastService() {
    const toast = useToast();

    const toastError = (message: string, duration?: number) => {
        toast.add({ severity: 'error', summary: 'Error', detail: message, life: duration || 5000 });
    };

    const toastWarn = (message: string, duration?: number) => {
        toast.add({ severity: 'warn', summary: 'Warning', detail: message, life: duration || 5000 });
    };

    const toastSuccess = (message: string, duration?: number) => {
        toast.add({ severity: 'success', summary: 'Success', detail: message, life: duration || 5000 });
    };

    const stickyError = (message: string) => {
        toast.add({ severity: 'error', summary: 'Error', detail: message });
    };

    const stickyWarn = (message: string) => {
        toast.add({ severity: 'warn', summary: 'Warning', detail: message });
    };

    const stickySuccess = (message: string) => {
        toast.add({ severity: 'success', summary: 'Success', detail: message });
    };

    const removeAllToast = () => {
        toast.removeAllGroups();
    };

    return {
        toastError,
        toastSuccess,
        toastWarn,
        stickyError,
        stickySuccess,
        stickyWarn,
        removeAllToast
    };
}
