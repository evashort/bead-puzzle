<script>
export default {
  props: {
    x0: Number,
    y0: Number,
    x1: Number,
    y1: Number,
    x2: Number,
    y2: Number,
    x3: Number,
    y3: Number,
    dLength: Number,
    active: Boolean,
  },
  computed: {
    d1() {
      return this.getD(
        this.x2 - this.x1,
        this.y2 - this.y1,
        this.x0 - this.x1,
        this.y0 - this.y1,
      )
    },
    d2() {
      return this.getD(
        this.x1 - this.x2,
        this.y1 - this.y2,
        this.x3 - this.x2,
        this.y3 - this.y2,
      )
    },
    path() {
      return `M ${this.x1} ${this.y1} C ${this.x1 + this.d1.x} ${this.y1 + this.d1.y}, ${this.x2 + this.d2.x} ${this.y2 + this.d2.y}, ${this.x2} ${this.y2}`
    },
  },
  methods: {
    getD(thisX, thisY, otherX, otherY) {
      let otherLength = Math.sqrt(otherX * otherX + otherY * otherY)
      let thisLength = Math.sqrt(thisX * thisX + thisY * thisY)
      let dx = thisX * otherLength - otherX * thisLength
      let dy = thisY * otherLength - otherY * thisLength
      let oldLength = Math.sqrt(dx * dx + dy * dy)
      let factor = oldLength > 0 ? this.dLength / oldLength : 0
      return {x: dx * factor, y: dy * factor}
    },
  },
}
</script>

<template>
  <path :class="{ edge: true, active: active }" :d="path" fill="none" />
</template>

<style scoped>
.edge {
  stroke: var(--color-text);
  stroke-width: 0.05;
  stroke-linecap: round;
  stroke-dasharray: 0 0.12;
}
.edge.active {
  stroke-dasharray: none;
}

</style>
