// types.d.ts
import 'vue-router';

declare module 'vue-router' {
    interface RouteMeta {
        title?: string;
        requiresAuth?: boolean;
        roles?: string | string[];
        permissions?: string | string[];
        logout?: boolean;
    }
}
