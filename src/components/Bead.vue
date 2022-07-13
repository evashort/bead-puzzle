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
      return Math.sin(2 * Math.PI * this.node / this.nodeCount)
    },
    y() {
      return -Math.cos(2 * Math.PI * this.node / this.nodeCount)
    },
    color() {
      return colors[this.id]
    },
  },
}
</script>

<template>
  <g :transform="transformation">
    <path :d="shape" :fill="color" />
  </g>
</template>
