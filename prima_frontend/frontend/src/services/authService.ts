import { ref } from 'vue';
import axios from 'axios';
import { generateRandomString, generateCodeChallenge } from '../utils/pkceUtils';
import { useAuthStore } from '../stores/authStore';
import { useWellOverviewStore } from '../stores/wellOverviewStore';
import { createApiService } from './apiService';
import { createToastService } from './toastService';
import { useRouter } from 'vue-router';
import type { User } from '../types/user';
import { keysToCamelCase } from '../utils/toCamelCase';
import type { Organization } from '../types/organization';

export interface LoginData {
    email: string;
    password: string;
}

export interface AuthData {
    access_token: string;
    expires_in: number;
    refresh_token: string;
    role: string;
    permissions: Array<string>;
    organization: Organization;
    user: User;
}

export function createAuthService() {
    const codeVerifier = ref('');
    const accessToken = ref('');
    const authStore = useAuthStore();
    const wellOverviewStore = useWellOverviewStore();
    const apiService = createApiService();
    const toastService = createToastService();
    const { toastError, toastSuccess } = toastService;
    const loginWindow = ref<Window | null>(null);
    const router = useRouter();

    const clientId = import.meta.env.VITE_PASSPORT_CLIENT_ID;
    const redirectUri = `${import.meta.env.VITE_APP_URL}/${import.meta.env.VITE_REDIRECT_PATH}`;
    const authEndpoint = `${import.meta.env.VITE_API_URL}/oauth/authorize`;
    const tokenEndpoint = `${import.meta.env.VITE_API_URL}/oauth/token`;
    const rolesEndpoint = `${import.meta.env.VITE_API_URL}/api/roles-and-permissions`;

    const getLoginUrl = async () => {
        codeVerifier.value = generateRandomString(128);
        authStore.setCodeVerifier(codeVerifier.value);

        const codeChallenge = await generateCodeChallenge(codeVerifier.value);

        const state = generateRandomString(40);
        return `${authEndpoint}?client_id=${clientId}&redirect_uri=${redirectUri}&response_type=code&scope=&state=${state}&code_challenge=${codeChallenge}&code_challenge_method=S256&prompt=login`;
    };

    const openLoginWindow = async () => {
        const url = await getLoginUrl();

        if (!loginWindow.value?.closed) {
            loginWindow.value?.close();
        }

        loginWindow.value = window.open(url, 'popup', 'width=700,height=700');

        return loginWindow.value;
    };

    const login = (authData: AuthData) => {
        // NOTE: Must use snake case here in order to avoid modifying underlying auth setup
        accessToken.value = authData.access_token;
        authStore.setCodeVerifier('');
        authStore.setAccessToken(accessToken.value);
        authStore.setRefreshToken(authData.refresh_token);
        authStore.setExpiryTime(new Date().getTime() + authData.expires_in * 1000);
        authStore.setRole(authData.role);
        authStore.setPermissions(authData.permissions);
        authStore.setOrganization(authData.organization);
        authStore.setUser(authData.user);
    };

    const openPasswordResetWindow = async (token: string) => {
        const url = `${import.meta.env.VITE_API_URL}/reset-password/${token}`;
        window.open(url, 'popup', 'width=700,height=700');
    };

    const handleRedirect = async () => {
        const params = new URLSearchParams(window.location.search);
        const code = params.get('code');
        const state = params.get('state');

        try {
            if (code && state) {
                const data = {
                    grant_type: 'authorization_code',
                    client_id: clientId,
                    code_verifier: authStore.getCodeVerifier,
                    code,
                    redirect_uri: redirectUri
                };

                const response = await axios.post(tokenEndpoint, data, {
                    headers: {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    }
                });

                const roleAndPermissionResponse = await axios.get(rolesEndpoint, {
                    headers: {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*',
                        Authorization: 'Bearer ' + response.data.access_token
                    }
                });

                const loginData = {
                    ...response.data,
                    ...roleAndPermissionResponse.data,
                    user: keysToCamelCase(roleAndPermissionResponse.data.user)
                };

                if (window && !window.closed) {
                    window.opener.postMessage({ type: 'loginSuccess', loginData: loginData }, '*');
                    window.close();
                }
            }
        } catch (error) {
            if (window && !window.closed) {
                window.opener.postMessage({ type: 'loginFailure' }, '*');
                window.close();
            }
        }
    };

    const getAccessToken = () => {
        return accessToken.value || authStore.getAccessToken;
    };

    const logoutUser = async () => {
        try {
            const accessToken = authStore.getAccessToken;
            router.push('/');
            authStore.logout();
            wellOverviewStore.resetSelectedDataset();
            wellOverviewStore.setOrgName('');
            wellOverviewStore.setOrgCoordinates({ longitude: 0, latitude: 0 });
            await axios.post(
                `${import.meta.env.VITE_API_URL}/api/logout`,
                {},
                {
                    headers: {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*',
                        Authorization: `Bearer ${accessToken}`
                    }
                }
            );
        } catch (error) {
            console.error(error);
        }
    };

    const getData = async () => {
        const response = await apiService.get(`/api/getData`);
        return response;
    };

    const resendAccountCreationEmail = async (id: number) => {
        try {
            const response = await apiService.post(`/api/resend-account-creation-email/${id}`, {});
            toastSuccess('A new account creation link has been sent.');
            return response;
        } catch (error) {
            toastError('An error occurred while resending the account creation link');
            return error;
        }
    };

    const hideDisclaimer = async () => {
        try {
            const response = await apiService.post(`/api/hide-disclaimer`, {});
            return response;
        } catch (error) {
            return error;
        }
    };

    return {
        handleRedirect,
        hideDisclaimer,
        getAccessToken,
        logoutUser,
        openLoginWindow,
        openPasswordResetWindow,
        getData,
        login,
        resendAccountCreationEmail
    };
}
