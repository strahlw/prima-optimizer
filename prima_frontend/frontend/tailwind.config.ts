import type { Config } from 'tailwindcss';

export default {
    content: ['./src/**/*.{html,js,ts,vue}'],
    theme: {
        fontFamily: {
            sans: [
                '"Inter var"',
                '-apple-system',
                'BlinkMacSystemFont',
                'Segoe UI',
                'Roboto',
                'Oxygen',
                'Ubuntu',
                'Cantarell',
                'Fira Sans',
                'Droid Sans',
                'Helvetica Neue',
                'sans-serif'
            ]
        },
        extend: {
            colors: {
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
                },
                warn: {
                    50: '#fef9e8',
                    100: '#fef0c3',
                    200: '#fee28a',
                    300: '#fdd147',
                    400: '#fac215',
                    500: '#eab308',
                    600: '#ca9a04',
                    700: '#a17c07',
                    800: '#85680e',
                    900: '#715a12',
                    950: '#423306',
                    DEFAULT: '#eab308'
                },
                bgDefault: '#F7F5F7'
            }
        }
    },
    plugins: []
} satisfies Config;
