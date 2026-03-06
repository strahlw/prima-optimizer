import './bootstrap';
import { createApp } from 'vue';
import Aura from '@primeuix/themes/aura';
import { definePreset } from '@primeuix/themes';
import PrimeVue from 'primevue/config';
import '../css/app.css';

import 'primeicons/primeicons.css'; // icons

// PrimeVue components
import InputText from 'primevue/inputtext';
import Card from 'primevue/card';
import InputGroup from 'primevue/inputgroup';
import InputGroupAddon from 'primevue/inputgroupaddon';

// Custom components
import EmailInput from './Components/EmailInput.vue';
import PasswordInput from './Components/PasswordInput.vue';
import SubmitButton from './Components/SubmitButton.vue';
import PasswordReset from './Components/PasswordReset.vue';

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

const app = createApp({});
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

app.component('InputText', InputText);
app.component('Card', Card);
app.component('InputGroup', InputGroup);
app.component('InputGroupAddon', InputGroupAddon);

app.component('EmailInput', EmailInput);
app.component('PasswordInput', PasswordInput);
app.component('SubmitButton', SubmitButton);
app.component('PasswordReset', PasswordReset);

app.mount('#app');
