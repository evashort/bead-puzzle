<script>
const colors = ['', 'red', 'green', 'blue', 'indigo', 'pink']
export default {
  props: {
    id: Number,
    index: Number,
    beadCount: Number,
  },
  computed: {
    x() {
      return Math.sin(2 * Math.PI * this.index / this.beadCount)
    },
    y() {
      return -Math.cos(2 * Math.PI * this.index / this.beadCount)
    },
    color() {
      return colors[this.id]
    },
  },
}
</script>

<template>
  <circle v-if="id > 0" :cx="x" :cy="y" r=".1" :fill="color" />
</template>
