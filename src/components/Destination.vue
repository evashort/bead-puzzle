<script>
export default {
  props: {
    size: Number,
    index: Number,
    won: Boolean,
    radius: Number,
  },
  computed: {
    name() {
      return [
        [],
        [],
        ['mushroom'],
        ['butterfly', 'mushroom'],
        ['heart', 'butterfly', 'mushroom'],
        ['heart', 'butterfly', 'leaf', 'mushroom'],
        ['heart', 'butterfly', 'leaf', 'mushroom', 'flower'],
        ['heart', 'butterfly', 'saturn', 'leaf', 'mushroom', 'flower'],
      ][this.size][this.index]
    },
    goalAngle() {
      return [
        [],
        [90],
        [80, 100],
        [80, 15, -15],
        [80, 170, 100, 190],
        [80, 15, 105, 255, -15],
        [80, 15, 165, 105, 195, -15],
        [80, 40, 170, 105, 255, 195, -40],
      ][this.size][this.index]
    },
    x() {
      return radius * Math.sin(2 * Math.PI * i / size) +
        30 * Math.sin(goalAngles[i] * Math.PI / 180)
    },
    y() {
      return -radius * Math.cos(2 * Math.PI * i / size) -
        30 * Math.cos(goalAngles[i] * Math.PI / 180)
    },
  },
}
</script>

<template>
  <g :transform="`translate(${x},${y})`">
    <use :href="`#${name}-outline`" :style="{ 'transform': 'scale(2.7)' }"/>
  </g>
</template>

<style scoped>
</style>
