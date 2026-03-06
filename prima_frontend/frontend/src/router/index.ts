import { createRouter, createWebHistory } from 'vue-router';
import { useAuthStore } from '../stores/authStore';
import { usePermissions } from '../composables/usePermissions';

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes: [
        {
            path: '/well-overview',
            name: 'well-overview',
            component: () => import('@/views/screens/WellOverviewScreen.vue'),
            meta: { title: 'Well Overview' }
        },
        {
            path: '/scenarios/:scenarioId?/:organizationId?',
            name: 'scenarios',
            component: () => import('@/views/screens/ScenariosScreen.vue'),
            meta: { title: 'Scenarios' }
        },
        {
            path: '/scenario-queue',
            name: 'scenario-queue',
            component: () => import('@/views/screens/ScenarioQueue.vue'),
            meta: { title: 'Scenario Queue' }
        },
        // {
        //     path: '/review-scenario/:scenarioId',
        //     name: 'review-scenario',
        //     component: () => import('@/views/screens/ScenarioReview.vue'),
        //     meta: { title: 'Review Scenario' }
        // },
        {
            path: '/upload-data',
            name: 'upload-data',
            component: () => import('@/views/screens/AddWellDataScreen.vue'),
            meta: { title: 'Upload Data', requiresAuth: true, permissions: ['upload-data'] }
        },
        {
            path: '/manage-users',
            name: 'manage-users',
            component: () => import('@/views/admin/ManageUsers.vue'),
            meta: { title: 'Manage Users', requiresAuth: true, roles: ['org-admin'] }
        },
        {
            path: '/account-details',
            name: 'account-details',
            component: () => import('@/views/screens/AccountDetailsScreen.vue'),
            meta: { title: 'Account Details', requiresAuth: true, roles: ['user'] }
        },
        {
            path: '/manage-organizations',
            name: 'manage-organizations',
            component: () => import('@/views/admin/ManageOrganizations.vue'),
            meta: { title: 'Manage Organizations', requiresAuth: true, roles: ['super-admin'] }
        },
        {
            path: '/create-scenario',
            name: 'create-scenario',
            component: () => import('@/views/screens/CreateScenarioScreen.vue'),
            meta: { title: 'Create Scenario' },
            children: [
                {
                    path: 'use-cases',
                    name: 'use-cases',
                    component: () => import('@/views/scenario/UseCasesForm.vue')
                },
                {
                    path: 'requirements',
                    name: 'requirements',
                    component: () => import('@/views/scenario/GeneralSpecificationsForm.vue')
                },
                {
                    path: 'impact-factors',
                    name: 'impact-factors',
                    component: () => import('@/views/scenario/ImpactFactorsForm.vue')
                },
                {
                    path: 'efficiency-factors',
                    name: 'efficiency-factors',
                    component: () => import('@/views/scenario/EfficiencyFactorsForm.vue')
                },
                {
                    path: 'well-ranking',
                    name: 'well-ranking',
                    component: () => import('@/views/scenario/WellRankingPage.vue')
                },
                {
                    path: 'pa-project-comparisons',
                    name: 'pa-project-comparisons',
                    component: () => import('@/views/scenario/PAProjectRecommendations.vue')
                },
                {
                    path: 'pa-project-recommendations',
                    name: 'pa-project-recommendations',
                    component: () => import('@/views/scenario/RunOptimizationReview.vue')
                }
            ]
        },
        {
            path: '/logout',
            name: 'logout',
            meta: { logout: true },
            redirect: '/'
        },
        {
            path: '/auth-redirect',
            name: 'auth-redirect',
            component: () => import('@/views/screens/AuthRedirect.vue'),
            meta: { title: 'Authorizing...' }
        },
        {
            path: '/reset-password/:token',
            name: 'password-reset-redirect',
            component: () => import('@/views/screens/PasswordResetRedirect.vue'),
            meta: { title: 'Reset Password...' }
        },
        {
            path: '/',
            name: 'home',
            component: () => import('@/views/screens/HomeScreen.vue'),
            meta: { title: 'NETL' }
        },
        {
            path: '/login',
            name: 'login-reset',
            component: () => import('@/views/screens/HomeScreen.vue'),
            meta: { title: 'NETL' },
            props: (route) => ({ reset: route.query.reset === 'true', creation: route.query.creation === 'true' })
        },
        {
            path: '/unauthorized',
            name: 'unauthorized',
            component: () => import('@/views/screens/UnauthorizedScreen.vue'),
            meta: { title: 'Unauthorized' }
        },
        {
            path: '/:catchAll(.*)',
            name: 'not-found',
            component: () => import('@/views/screens/NotFound.vue'),
            meta: { title: '404 Not Found' }
        }
    ],
    scrollBehavior(to, _, savedPosition) {
        // If there's a saved position (back/forward), use it
        if (savedPosition) {
            return savedPosition;
        }

        // For hash links, scroll to element
        if (to.hash) {
            return {
                el: to.hash,
                behavior: 'smooth'
            };
        }

        // Custom scroll to top that works with overflow-x: hidden
        return new Promise((resolve) => {
            setTimeout(() => {
                // Find the scrollable container (main-container or #app)
                const mainContainer = document.querySelector('.main-container');
                const appContainer = document.querySelector('#app');

                if (mainContainer) {
                    mainContainer.scrollTo({ top: 0, behavior: 'smooth' });
                }
                if (appContainer) {
                    appContainer.scrollTo({ top: 0, behavior: 'smooth' });
                }

                // Also scroll window as fallback
                window.scrollTo({ top: 0, behavior: 'smooth' });

                resolve({ left: 0, top: 0 });
            }, 50);
        });
    }
});

router.beforeEach((to, _, next) => {
    const authStore = useAuthStore();
    const { hasPermission, hasRole } = usePermissions();

    if (to.name === 'login-reset' && authStore.isAuthenticated) {
        next({ name: 'home' });
        return;
    }

    if (to.matched.some((record) => record.meta.requiresAuth)) {
        if (!authStore.isAuthenticated) {
            next({ name: 'home' });
            return;
        } else {
            if (authStore.isSuperAdmin) {
                next(); // For now, super admins can access everything
                return;
            }

            const requiredRoles = to.meta.roles;
            const requiredPermissions = to.meta.permissions;

            if (requiredRoles && !hasRole(requiredRoles)) {
                next({ name: 'unauthorized' });
                return;
            }

            if (requiredPermissions && !hasPermission(requiredPermissions)) {
                next({ name: 'unauthorized' });
                return;
            }
        }
    }

    if (typeof to.meta.title === 'string') {
        document.title = to.meta.title;
    } else {
        document.title = 'NETL';
    }
    next();
});

export default router;
