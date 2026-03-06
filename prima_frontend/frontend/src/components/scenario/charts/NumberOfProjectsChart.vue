<script lang="ts" setup>
    import { type PropType } from 'vue';
    import type { KpiData } from '@/types/kpi';

    defineProps({
        data: {
            required: true,
            type: Object as PropType<KpiData | null>
        }
    });
</script>

<template>
    <div class="chart-container">
        <div class="chart-title"># of P&A Projects</div>

        <div v-if="!data">
            <PSkeleton width="220px" height="100px" class="top-4" />
        </div>

        <div class="h-[220px] w-[220px] pt-10" v-else>
            <div class="text-5xl">{{ data?.numProjects ?? 'N/A' }}</div>
        </div>
    </div>
</template>
