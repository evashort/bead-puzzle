<script setup>
import getControlVector from '../ControlVector.js'
</script>

<script>
export default {
  props: {
    dLength: Number,
    nodeA: Number,
    nodeB: Number,
    size: Number,
    history: Array,
    index: Number,
    start: Number,
  },
  computed: {
    hole() {
      return this.history[this.history.length - 2]
    },
    tail() {
      return this.history[this.history.length - 1]
    },
    first() {
      return this.history[this.start]
    },
    second() {
      return this.history[this.start + 1]
    },
    node0() {
      if (this.index <= this.start) {
        return this.node1
      } else if (this.index <= this.start + 1) {
        if (
          this.first == this.tail &&
          // going back is not a loop
          this.history[this.history.length - 3] != this.tail
        ) {
          return this.hole
        } else if (
          this.first == this.hole &&
          this.second == this.tail &&
          this.history.length >= 3
        ) {
          return this.history[this.history.length - 3]
        } else if (
          this.history.length >= 3 &&
          this.tail == this.history[this.history.length - 3]
        ) {
          return this.tail // reversing the loop
        } else {
          return this.start
        }
      } else {
        return this.history[this.index - 2]
      }
    },
    node1() {
      return this.index > 0 ? this.history[this.index - 1] : this.nodeA
    },
    node2() {
      return this.index > 0 ? this.history[this.index] : this.nodeB
    },
    node3() {
      if (this.index <= this.start) {
        return this.node2
      } else if (
        this.index == this.history.length - 2 && this.node1 == this.tail &&
        this.first == this.hole
      ) {
        return this.second // reversing the loop
      } else if (this.index < this.history.length - 1) {
        return this.history[this.index + 1]
      } else {
        return this.tail == this.first ? this.second : this.tail
      }
    },
    x0() {
      return this.getX(this.node0)
    },
    y0() {
      return this.getY(this.node0)
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
      return this.getX(this.node3)
    },
    y3() {
      return this.getY(this.node3)
    },
    active() {
      return this.index > this.start
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
      return `M ${this.x2} ${this.y2} C ${this.x2 + this.d2.x} ${this.y2 + this.d2.y}, ${this.x1 + this.d1.x} ${this.y1 + this.d1.y}, ${this.x1} ${this.y1}`
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
  stroke-dasharray: 0 0.2 100;
}

</style>
