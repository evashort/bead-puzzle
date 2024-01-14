<script>
export default {
  props: {
    size: Number,
    bead: Number,
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
      ][this.size][this.bead - 1]
    },
    scale() {
      return {
        heart: 2.7,
        butterfly: 2.8,
        saturn: 3.35,
        leaf: 2.5,
        mushroom: 2.6,
        flower: 2.5,
      }[this.name]
    },
    angle() {
      return 2 * Math.PI * this.bead / this.size
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
      ][this.size][this.bead] * Math.PI / 180
    },
    x() {
      return this.radius * (
        Math.sin(this.angle) + 0.3 * Math.sin(this.goalAngle)
      )
    },
    y() {
      return -this.radius * (
        Math.cos(this.angle) + 0.3 * Math.cos(this.goalAngle)
      )
    },
  },
}
</script>

<template>
  <g :transform="`translate(${x},${y})`">
    <use
      :href="`#${name}-outline`"
      :style="{ 'transform': `scale(${scale})` }"
    />
  </g>
</template>
