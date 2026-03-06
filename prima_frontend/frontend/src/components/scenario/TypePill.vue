<script setup lang="ts">
    import { computed } from 'vue';
    import { ScenarioType, ScenarioFormTitle } from '@/constants/scenarioEnums';
    import Tag from 'primevue/tag';

    const props = defineProps<{
        type: ScenarioFormTitle;
    }>();

    const typeClass = computed<string>(() => {
        if (props.type.includes(ScenarioType.Rank)) return 'bg-secondary';
        if (props.type.includes(ScenarioType.Compare) || props.type.includes('Comparison')) return 'bg-warn';
        if (props.type.includes(ScenarioType.Recommend)) return 'bg-primary';
        return '';
    });

    const typeName = computed<string>(() => {
        if (props.type.includes(ScenarioType.Rank)) return ScenarioType.Rank;
        if (props.type.includes(ScenarioType.Compare) || props.type.includes('Comparison')) return ScenarioType.Compare;
        if (props.type.includes(ScenarioType.Recommend)) return ScenarioType.Recommend;
        return '';
    });
</script>

<template>
    <Tag
        :value="typeName"
        :class="'text-xs text-black font-normal ' + typeClass"
        rounded
        :pt="{ label: { class: 'black' } }"
    ></Tag>
</template>
