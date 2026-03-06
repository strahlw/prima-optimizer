<script setup lang="ts">
    import ReusableIcon from '../icons/ReusableIcon.vue';

    defineProps({
        size: {
            type: String,
            default: 'md'
        },
        fillClass: {
            type: String,
            default: 'fill-black'
        }
    });
</script>

<template>
    <ReusableIcon
        :fillClass="fillClass"
        :size="size"
        viewBox="568.5 518.5 198.0 198.0"
        :d="[
            'M568.5 617.5C568.5 562.824 612.824 518.5 667.5 518.5 722.176 518.5 766.5 562.824 766.5 617.5 766.5 672.176 722.176 716.5 667.5 716.5 612.824 716.5 568.5 672.176 568.5 617.5ZM618 617.5C618 644.838 640.162 667 667.5 667 694.838 667 717 644.838 717 617.5 717 590.162 694.838 568 667.5 568 640.162 568 618 590.162 618 617.5Z'
        ]"
    >
        <mask
            id="mask0_1079_918"
            style="mask-type: alpha"
            maskUnits="userSpaceOnUse"
            x="0"
            y="0"
            width="30"
            height="30"
        >
            <rect width="30" height="30" fill="#D9D9D9" /> </mask
    ></ReusableIcon>
</template>
