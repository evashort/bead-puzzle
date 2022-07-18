<script>
const colors = ['red', 'green', 'blue', 'indigo', 'pink']
export default {
  data() {
    return {
      oldNode: this.node,
    }
  },
  props: {
    id: Number,
    node: Number,
    nodeCount: Number,
    tail: Boolean,
    fromNode: Number,
  },
  computed: {
    transformation() {
      return `translate(${this.x} ${this.y})`
    },
    shape() {
      let radius = 0.1
      let yRadius = radius * Math.sqrt(0.75)
      return `M 0 ${-yRadius} L ${radius} ${yRadius} H ${-radius} Z`
    },
    x() {
      return Math.sin(2 * Math.PI * this.node / this.nodeCount + 0.00001)
    },
    y() {
      return -Math.cos(2 * Math.PI * this.node / this.nodeCount + 0.00001)
    },
    color() {
      return colors[this.id]
    },
  },
}
</script>

<template>
  <g :transform="transformation">
    <path :d="shape" :fill="color" :class="{bead: true, tail: tail}" />
  </g>
</template>

<style scoped>
.bead {
  stroke-width: 0;
  stroke: var(--color-text);
  stroke-linecap: round;
  stroke-linejoin: round;
  transition: stroke-width 0.5s;
}
.bead.tail {
  stroke-width: 0.04;
  transition: none;
}
</style>
