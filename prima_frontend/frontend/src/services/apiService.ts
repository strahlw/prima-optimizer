// services/apiService.js
import axios, { type AxiosRequestConfig } from 'axios';
import { useAuthStore } from '../stores/authStore';
import { useRouter } from 'vue-router';

export function createApiService() {
    const router = useRouter();
    const clientId = import.meta.env.VITE_PASSPORT_CLIENT_ID;
    const tokenEndpoint = `${import.meta.env.VITE_API_URL}/oauth/token`;
    const authStore = useAuthStore();
    const axiosInstance = axios.create({
        baseURL: import.meta.env.VITE_API_URL,
        headers: {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        }
    });

    const createRefreshFormData = (): FormData => {
        const refreshToken = authStore.getRefreshToken;
        const formData = new FormData();
        formData.append('grant_type', 'refresh_token');
        formData.append('client_id', clientId);
        if (refreshToken === null) throw new Error('Refresh token is null');
        formData.append('refresh_token', refreshToken);
        formData.append('scope', '');
        return formData;
    };

    axiosInstance.interceptors.request.use(
        (request) => {
            const token = authStore.getAccessToken;
            if (token) {
                request.headers.Authorization = `Bearer ${token}`;
            }
            return request;
        },
        (error) => {
            return Promise.reject(error);
        }
    );

    const refreshToken = async () => {
        const formData = createRefreshFormData();
        const response = await axios.post(tokenEndpoint, formData);
        const newAccessToken = response.data.access_token;
        const newRefreshToken = response.data.refresh_token;

        authStore.setAccessToken(newAccessToken);
        authStore.setRefreshToken(newRefreshToken);

        return response;
    };

    axiosInstance.interceptors.response.use(
        (response) => response,
        async (error) => {
            // Redirect if not authenticated
            const originalRequest = error.config;

            if (!authStore.isAuthenticated) {
                // If the user is not logged in, redirect to login page
                originalRequest._retry = true;
                router.push('/login');
            }

            if (axios.isCancel(error)) {
                // Convert to standard AbortError
                const abortError = new DOMException('Request aborted', 'AbortError');
                throw abortError;
            }

            if (error.response.status === 401 && !originalRequest._retry) {
                originalRequest._retry = true; // Mark the request as retried to avoid infinite loops.
                try {
                    await refreshToken();
                    axiosInstance.defaults.headers.common['Authorization'] = `Bearer ${authStore.getAccessToken}`;
                    originalRequest.headers['Authorization'] = `Bearer ${authStore.getAccessToken}`;

                    return axiosInstance(originalRequest);
                } catch (refreshError) {
                    console.error('Token refresh failed:', refreshError);
                    authStore.setAccessToken('');
                    authStore.setRefreshToken('');
                    router.push('/login');
                    return Promise.reject(refreshError);
                }
            }
            return Promise.reject(error);
        }
    );

    const get = async (url: string, queryParams?: Object) => {
        return axiosInstance.get(url, queryParams ?? {});
    };

    const getBlob = async (url: string) => {
        return axiosInstance.get(url, { responseType: 'blob' });
    };

    const post = async (url: string, data: Object, config?: AxiosRequestConfig) => {
        return axiosInstance.post(url, data, config || {});
    };

    const put = async (url: string, data: Object) => {
        return axiosInstance.put(url, data);
    };

    const del = async (url: string) => {
        return axiosInstance.delete(url);
    };

    return {
        get,
        post,
        put,
        delete: del,
        getBlob,
        refreshToken
    };
}
