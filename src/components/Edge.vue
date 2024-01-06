<script>
export default {
  props: {
    path: String,
    onPath: Boolean,
  },
}
</script>

<template>
  <path :class="{edge: true, onPath: onPath}" :d="path"/>
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
</style>
