import type { ErrorObject } from '@vuelidate/core';

export interface ValidationField {
    $model: unknown;
    $dirty: boolean;
    $error: boolean;
    $errors: ErrorObject[];
    $silentErrors: ErrorObject[];
    $externalResults: ErrorObject[];
    $pending: boolean;
    $params: Record<string, unknown>;
    $response: unknown;
    $validate: () => Promise<void>;
    $reset: () => void;
    $touch: () => void;
    $untouch: () => void;
    [key: string]: any;
}
