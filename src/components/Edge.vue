<script setup>
import getControlVector from '../ControlVector.js'
</script>

<script>
export default {
  props: {
    dLength: Number,
    node1: Number,
    node2: Number,
    size: Number,
    history: Array,
    index: Number,
  },
  computed: {
    x0() {
      return this.x1
    },
    y0() {
      return this.y1
    },
    x1() {
      return this.getX(this.node1)
    },
    y1() {
      return this.getY(this.node1)
    },
    x2() {
      return this.getX(this.node2)
    },
    y2() {
      return this.getY(this.node2)
    },
    x3() {
      return this.x2
    },
    y3() {
      return this.y2
    },
    active() {
      return this.index >= this.history.length - 1
    },
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
  methods: {
    getX(node) {
      return Math.sin(2 * Math.PI * node / this.size)
    },
    getY(node) {
      return -Math.cos(2 * Math.PI * node / this.size)
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
