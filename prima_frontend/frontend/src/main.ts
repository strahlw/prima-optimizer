import 'primeicons/primeicons.css';
import './assets/main.css';
import Aura from '@primeuix/themes/aura';
import { definePreset } from '@primeuix/themes';
import PrimeVue from 'primevue/config';

import { createApp } from 'vue';

import App from './App.vue';
const app = createApp(App);

const MyPreset = definePreset(Aura, {
    primitive: {
        primary: {
            50: '#cdf9ff',
            100: '#a1f1ff',
            200: '#60e4ff',
            300: '#18cdf8',
            400: '#00b0de',
            500: '#0092c3',
            600: '#086f96',
            700: '#105a7a',
            800: '#124b67',
            900: '#053047',
            DEFAULT: '#0092c3'
        },
        secondary: {
            50: '#f9fbf5',
            100: '#e2edd1',
            200: '#cbdead',
            300: '#b4cf89',
            400: '#9dc164',
            500: '#86b240',
            600: '#729736',
            700: '#5e7d2d',
            800: '#4a6223',
            900: '#36471a',
            950: '#222d10',
            DEFAULT: '#86b240'
        }
    },
    semantic: {
        primary: {
            50: '#cdf9ff',
            100: '#a1f1ff',
            200: '#60e4ff',
            300: '#18cdf8',
            400: '#00b0de',
            500: '#0092c3',
            600: '#086f96',
            700: '#105a7a',
            800: '#124b67',
            900: '#053047',
            DEFAULT: '#0092c3'
        },
        secondary: {
            50: '#f9fbf5',
            100: '#e2edd1',
            200: '#cbdead',
            300: '#b4cf89',
            400: '#9dc164',
            500: '#86b240',
            600: '#729736',
            700: '#5e7d2d',
            800: '#4a6223',
            900: '#36471a',
            950: '#222d10',
            DEFAULT: '#86b240'
        }
    }
});

app.use(PrimeVue, {
    theme: {
        preset: MyPreset,
        options: {
            prefix: 'p',
            darkModeSelector: 'never-available',
            cssLayer: {
                name: 'primevue',
                order: 'tailwind-base, primevue, tailwind-utilities'
            }
        }
    },
    pt: {
        dataTable: {
            headerCell: { class: 'text-white' }
        }
    }
});

import { createPinia } from 'pinia';
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate';
const pinia = createPinia();
pinia.use(piniaPluginPersistedstate);
app.use(pinia);

import router from './router';

import Accordion from 'primevue/accordion';
import AccordionTab from 'primevue/accordiontab';
import ToastService from 'primevue/toastservice';
import Button from 'primevue/button';
import FileUpload from 'primevue/fileupload';
import ProgressBar from 'primevue/progressbar';
import Badge from 'primevue/badge';
import Card from 'primevue/card';
import InputText from 'primevue/inputtext';
import InputNumber from 'primevue/inputnumber';
import InputGroup from 'primevue/inputgroup';
import InputGroupAddon from 'primevue/inputgroupaddon';
import RadioButton from 'primevue/radiobutton';
import Select from 'primevue/select';
import Slider from 'primevue/slider';
import Chart from 'primevue/chart';
import ConfirmDialog from 'primevue/confirmdialog';
import ConfirmationService from 'primevue/confirmationservice';
import ProgressSpinner from 'primevue/progressspinner';
import Checkbox from 'primevue/checkbox';
import Tooltip from 'primevue/tooltip';
import SelectButton from 'primevue/selectbutton';
import ValidationError from '@/components/forms/FormValidationErrors.vue';
import MultiSelect from 'primevue/multiselect';
import Column from 'primevue/column';
import DataTable from 'primevue/datatable';
import Skeleton from 'primevue/skeleton';

import LabelTooltip from '@/components/forms/LabelTooltip.vue';

app.use(ToastService);
app.use(ConfirmationService);

app.use(router);
app.component('PAccordion', Accordion);
app.component('AccordionTab', AccordionTab);
app.component('InputGroup', InputGroup);
app.component('InputGroupAddon', InputGroupAddon);
app.component('PButton', Button);
app.component('FileUpload', FileUpload);
app.component('ProgressBar', ProgressBar);
app.component('PBadge', Badge);
app.component('PCard', Card);
app.component('InputText', InputText);
app.component('InputNumber', InputNumber);
app.component('RadioButton', RadioButton);
app.component('PSelect', Select);
app.component('InputSlider', Slider);
app.component('ConfirmDialog', ConfirmDialog);
app.component('ProgressSpinner', ProgressSpinner);
app.component('PCheckbox', Checkbox);
app.component('ValidationError', ValidationError);
app.component('SelectButton', SelectButton);
app.component('MultiSelect', MultiSelect);
app.component('PColumn', Column);
app.component('DataTable', DataTable);
app.component('LabelTooltip', LabelTooltip);
app.component('PChart', Chart);
app.component('PSkeleton', Skeleton);

app.directive('tooltip', Tooltip);

app.mount('#app');
