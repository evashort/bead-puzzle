<script>
export default {
  props: {
    path: String,
    onPath: Boolean,
    hideStart: Boolean,
    hideEnd: Boolean,
  },
}
</script>

<template>
  <path :class="{edge: true, onPath: onPath}" :d="path"/>
  <circle
    v-if="hideStart || hideEnd"
    :r="28"
    :class="{ terminator: true, end: hideEnd }"
    :style="{ 'offset-path': `path('${path}')` }"
  />
</template>

<style scoped>
.edge {
  fill: none;
  stroke: var(--color-text);
  stroke-width: 4;
  stroke-linecap: round;
  stroke-dasharray: 4 12;
}

.canAnimate .edge {
  transition: d 0.5s;
}

.edge.onPath {
  stroke-dasharray: none;
}

.terminator {
  fill: var(--color-background);
  offset-distance: 0%;
  offset-rotate: none;
}

.terminator.end {
  offset-distance: 100%;
}
</style>
