import { required, numeric, minValue, maxValue, decimal } from '@vuelidate/validators';
import type { OrganizationForm } from '../types/organizationForm';

export const validationRules = {
    key: { required },
    name: { required },
    logo: {},
    availableFunding: {
        numeric,
        minValue: minValue(0)
    },
    wellCount: {
        numeric,
        minValue: minValue(0)
    },
    paTarget: {
        numeric,
        minValue: minValue(0)
    },
    longitude: {
        required,
        decimal,
        minValue: minValue(-180),
        maxValue: maxValue(180)
    },
    latitude: {
        required,
        decimal,
        minValue: minValue(-90),
        maxValue: maxValue(90)
    }
};

export const initialOrganizationForm: OrganizationForm = {
    id: null,
    key: '',
    name: '',
    logo: null,
    availableFunding: 0,
    wellCount: 0,
    paTarget: 0,
    longitude: 0,
    latitude: 0,
    logoUrl: null
};
