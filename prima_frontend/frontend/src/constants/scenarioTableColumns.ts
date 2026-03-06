import type { ScenarioTableColumn } from '../types/scenario.d.ts';

export const scenarioTableColumns: ScenarioTableColumn[] = [
    { field: 'name', header: 'Scenario Name' },
    { field: 'user', header: 'Created By' },
    { field: 'dataset.name', header: 'Well Filename' },
    { field: 'wellCount', header: '# of Wells' },
    { field: 'status', header: 'Status' }
];
