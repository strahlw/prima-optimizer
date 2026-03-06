<script setup lang="ts">
    import { computed } from 'vue';
    import type { LazyParams } from '@/types/pagination';
    import type { RankingDataJson } from '@/types/ranking';
    import type { ColumnDefinition } from '@/constants/rankingConstants';
    import { useScenarioFormStore } from '@/stores/form/scenarioForm';
    import type { ScenarioData } from '@/types/scenario';

    const scenarioFormStore = useScenarioFormStore();

    const props = defineProps<{
        existing?: boolean;
        scenarioData?: ScenarioData;
        lazyParams: LazyParams;
        rankingData: RankingDataJson[];
        totalRecords: number;
        loading: boolean;
        columns: ColumnDefinition[];
        isRecommendationOnly?: boolean;
    }>();

    function roundToDecimalPlaces(value: number, decimalPlaces = 2) {
        if (isNaN(value)) return value; // Handle non-numeric values

        return parseFloat(value.toFixed(decimalPlaces)); // Round to the desired decimal places
    }

    const scoreRange = (scoreKey: string) => {
        const keys = scoreKey.split('.');
        let score: any = 0;
        let parentScore: number = 0;
        const impactFactors = props.existing ? props.scenarioData?.impactFactors : scenarioFormStore.form.impactFactors;

        if (keys.length === 1 && impactFactors) {
            score = impactFactors[keys[0]];
            parentScore = score.value ?? 0;
            return `[0-${parentScore}]`;
        } else if (impactFactors) {
            const parentFactor = impactFactors[keys[0]];
            const childFactors = parentFactor?.childFactors;
            if (childFactors) {
                score = childFactors[keys[2]];
                parentScore = parentFactor.value ?? 0;
            }
        }

        // Get the value or default to 0 if not found
        const actualValue = (parentScore * score.value) / 100;
        return `[0-${roundToDecimalPlaces(actualValue)}]`;
    };

    function formatField(value: any, key: string): string {
        const fieldsToFormat = [
            'lifelongOilProduction',
            'lifelongGasProduction',
            'depth',
            'fiveYearOilProduction',
            'fiveYearGasProduction'
        ];

        if (fieldsToFormat.includes(key) && typeof value === 'number') {
            if (value > 999) {
                return new Intl.NumberFormat('en-US').format(value);
            }
        }
        return value;
    }

    const computedColumns = computed(() => {
        if (props.isRecommendationOnly) {
            return props.columns.filter((col) => col.key !== 'wellType');
        }
        return props.columns;
    });
</script>

<template>
    <DataTable
        :sortField="lazyParams.sortField || 'wellRank'"
        :sortOrder="lazyParams.sortOrder || 1"
        :first="lazyParams.first"
        :value="rankingData"
        size="small"
        dataKey="key"
        showGridlines
        lazy
        paginator
        :totalRecords="totalRecords"
        :loading="loading"
        :rows="20"
        @page="(event) => $emit('page', event)"
        :globalFilterFields="['wellType']"
        :pt="{
            header: { class: 'border-none' },
            headerRow: { class: 'bg-primary' },
            thead: { class: 'bg-primary' },
            column: { class: 'bg-primary-500' },
            tableContainer: { class: 'rounded-t-lg' }
        }"
    >
        <PColumn
            label="Map"
            :pt="{
                headerCell: { class: 'bg-primary border-l-0' },
                headerTitle: { class: 'text-slate-50 text-sm' }
            }"
        >
            <template #body="slotProps">
                <i class="pi pi-map text-secondary cursor-pointer" @click="() => $emit('navigate', slotProps.data)">
                </i>
            </template>
        </PColumn>
        <PColumn
            :sortable="true"
            :pt="{
                headerCell: { class: 'bg-primary border-l-0' },
                headerTitle: {
                    class: 'text-slate-50 w-auto whitespace-nowrap overflow-visible text-sm'
                },
                sortIcon: { class: 'text-slate-50' }
            }"
            v-for="col in computedColumns"
            :key="col.key"
            :field="`${col.key}`"
            :sortField="col.key"
        >
            <template #header>
                <div class="bg-primary border-l-0 text-slate-50 w-auto whitespace-nowrap overflow-visible text-sm">
                    <div v-if="col.factor">
                        {{ col.header }}
                        <div>{{ scoreRange(col.factor ?? '') }}</div>
                    </div>
                    <div v-else>{{ col.header }}</div>
                </div>
            </template>
            <template #body="slotProps">
                <span v-if="col.score">
                    {{ roundToDecimalPlaces(slotProps.data[col.key]) }}
                </span>
                <span v-else>
                    {{ formatField(slotProps.data[col.key], col.key) }}
                </span>
            </template>
        </PColumn>
    </DataTable>
</template>
