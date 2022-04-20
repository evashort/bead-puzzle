<script setup>
import getControlVector from '../ControlVector.js'
</script>

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
      return getControlVector(
        this.x2 - this.x1,
        this.y2 - this.y1,
        this.x0 - this.x1,
        this.y0 - this.y1,
        this.dLength,
      )
    },
    d2() {
      return getControlVector(
        this.x1 - this.x2,
        this.y1 - this.y2,
        this.x3 - this.x2,
        this.y3 - this.y2,
        this.dLength,
      )
    },
    path() {
      return `M ${this.x1} ${this.y1} C ${this.x1 + this.d1.x} ${this.y1 + this.d1.y}, ${this.x2 + this.d2.x} ${this.y2 + this.d2.y}, ${this.x2} ${this.y2}`
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
