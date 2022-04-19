<script>
const colors = ['red', 'green', 'blue', 'indigo', 'pink']
export default {
  props: {
    id: Number,
    node: Number,
    nodeCount: Number,
  },
  computed: {
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
  <circle :cx="x" :cy="y" r=".1" :fill="color" />
</template>
