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
        viewBox="902.927 523.009 166.643 166.639"
        :d="[
            'M939.622 525.17 985.261 568.649 1028.74 523.009 1067.41 559.851 1023.93 605.49 1069.57 648.969 1032.88 687.487 987.239 644.009 943.76 689.648 905.088 652.807 948.566 607.167 902.927 563.689Z'
        ]"
    >
        <mask
            id="mask0_1079_915"
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
