# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Tools Used

### Frontend

- [Vue 3](https://vuejs.org/)
- [Vue Router](https://router.vuejs.org/)
- [Pinia](https://pinia.vuejs.org/)
- [PrimeVue 4](https://www.primevue.org/)
- [Tailwind CSS v3](https://tailwindcss.com/)
- [Vuelidate](https://vuelidate-next.netlify.app/)
- [Mapbox GL JS](https://docs.mapbox.com/mapbox-gl-js/)

### Backend

- [Laravel 12](https://laravel.com/)
- [Laravel Excel](https://laravel-excel.com/)
- [Laravel MongoDB](https://www.mongodb.com/docs/drivers/php/laravel-mongodb/current/)

### CI/CD

- [Github Actions](https://github.com/features/actions)
- [Husky for git hooks](https://typicode.github.io/husky/#/)
- [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/)

## Project Overview

PRIMO (P&A Project Optimizer Application) is a web application for optimizing oil and gas well plugging and abandonment (P&A) projects. The application includes:

- **Backend (Laravel API)**: Located in `/api` directory - RESTful API handling user management, scenarios, datasets, and optimization algorithms
- **Frontend (Vue.js SPA)**: Located in `/frontend` directory - Modern Vue 3 application with TypeScript, Pinia state management, and PrimeVue components
- **Root-level scripts**: Package management and git hooks configuration
- **External Services**: MongoDB for scenario data, MySQL for relational data, Redis for queues, Mapbox for mapping
- **External API**: Integration with a python API for calculations

## Development Commands

### Root Level

- `npm run prettier:check:ci` - Check code formatting across project
- `npm run version` - Bump version and generate changelog

## Architecture Overview

### Backend Structure

- **Controllers**: Handle HTTP requests and responses
- **Models**: Eloquent ORM models for database entities (User, Scenario, Dataset, Organization, etc.)
- **Services**: Business logic layer (PrimoApiService for external API integration)
- **Repositories**: Data access layer for complex queries
- **Actions**: Single-purpose classes for specific operations
- **Jobs**: Queue-able background tasks
- **Policies**: Authorization logic using Laravel's policy system
- **Types**: Custom data structures for scenario configurations

### Frontend Structure

- **Views/Screens**: Main application pages
- **Components**: Reusable Vue components organized by feature
- **Stores (Pinia)**: State management for auth, scenarios, forms, etc.
- **Services**: API communication layer
- **Composables**: Reusable composition functions
- **Types**: TypeScript type definitions
- **Constants**: Application-wide constants and configurations

### Key Features

- **Role-based Access Control**: Users have roles (super-admin, org-admin, user) with specific permissions
- **Scenario Management**: Create, configure, and optimize P&A scenarios with various factors
- **Data Import/Export**: Excel template-based data uploads and multiple export formats
- **Real-time Processing**: Queue-based scenario processing with status tracking
- **Map Integration**: Mapbox GL integration for geographic well data visualization

## Testing

- **Backend**: Uses Pest testing framework with Feature and Unit tests
- **Test Database**: SQLite in-memory database for backend tests

## Code Quality

- **Backend**: Laravel Pint for code formatting following Laravel preset
- **Frontend**: ESLint + Prettier for code linting and formatting
- **Git Hooks**: Husky with lint-staged for pre-commit formatting
- **Conventional Commits**: Required commit message format for automatic versioning

## Database

- **Primary**: MySQL for relational data
- **MongoDB**: For complex JSON scenario data storage
- **Redis**: Queue processing and caching
- **Testing**: SQLite in-memory for tests

## Key Dependencies

### Backend

- Laravel 12.x with Passport (OAuth2), Horizon (queue management)
- MongoDB Laravel integration for document storage
- Spatie Laravel Permission for role/permission management
- Maatwebsite Excel for data import/export

### Frontend

- Vue 3 with Composition API and TypeScript
- Pinia for state management with persistence
- PrimeVue component library with custom theming
- Mapbox GL for interactive maps
- Chart.js for data visualization
- Axios for HTTP requests

## Environment Setup

Both `/api` and `/frontend` directories require `.env` files. The frontend specifically needs `VITE_APP_MAPBOX_TOKEN` for map functionality.
