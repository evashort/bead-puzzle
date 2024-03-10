<script>
export default {
  props: {
    size: Number,
    hole: Number,
    radius: Number,
    shown: Boolean,
  },
  computed: {
    path() {
      let d = 18 * Math.sqrt(0.5)
      return `M ${-d} ${-d} L ${d} ${d} M ${d} ${-d} L ${-d} ${d}`
    },
    x() {
      return this.radius * Math.sin(2 * Math.PI * this.hole / this.size)
    },
    y() {
      return -this.radius * Math.cos(2 * Math.PI * this.hole / this.size)
    },
  },
}
</script>

<template>
  <g
    :transform="`translate(${x}, ${y})`"
    :class="{crossGroup: true, ghost: !shown}"
    :visibility="shown ? 'initial' : 'hidden'"
  >
    <path :d="path" class="cross shadow"/>
    <path :d="path" class="cross"/>
  </g>
</template>

<style scoped>
.cross {
  stroke: var(--color-text);
  stroke-width: 4;
  stroke-linecap: round;
  stroke-linejoin: round;
  fill: none;
}
.cross.shadow {
  stroke: var(--color-background);
  stroke-width: 12;
}
.canAnimate .crossGroup.ghost {
  transition: visibility 0s 0.35s;
}
</style>
