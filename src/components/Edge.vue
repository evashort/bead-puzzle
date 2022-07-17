<script setup>
import getControlVector from '../ControlVector.js'
</script>

<script>
export default {
  props: {
    dLength: Number,
    headRadius: Number,
    headLength: Number,
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
      return this.index > this.start ?
        this.history[this.index - 1] : this.nodeA
    },
    node2() {
      return this.index > this.start ? this.history[this.index] : this.nodeB
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
    arrow() {
      return (this.node1 == this.hole && this.node2 == this.tail) -
        (this.node2 == this.hole && this.node1 == this.tail)
    },
    reverse() {
      return this.active && (
        (this.arrow == 0 && this.node1 == this.hole) || this.arrow < 0
      )
    },
    gap() {
      return this.nodeA == this.hole || this.nodeB == this.hole
    },
    x0() {
      return this.getX(this.reverse ? this.node3 : this.node0)
    },
    y0() {
      return this.getY(this.reverse ? this.node3 : this.node0)
    },
    x1() {
      return this.getX(this.reverse ? this.node2 : this.node1)
    },
    y1() {
      return this.getY(this.reverse ? this.node2 : this.node1)
    },
    x2() {
      return this.getX(this.reverse ? this.node1 : this.node2)
    },
    y2() {
      return this.getY(this.reverse ? this.node1 : this.node2)
    },
    x3() {
      return this.getX(this.reverse ? this.node0 : this.node3)
    },
    y3() {
      return this.getY(this.reverse ? this.node0 : this.node3)
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
        1,
      )
    },
    d2() {
      return getControlVector(
        this.x1 - this.x2,
        this.y1 - this.y2,
        this.x3 - this.x2,
        this.y3 - this.y2,
        1,
      )
    },
    h1() {
      return d1
    },
    path() {
      let x1 = this.x1, y1 = this.y1, x2 = this.x2, y2 = this.y2
      let d1 = this.d1, d2 = this.d2, len = this.dLength
      return `M ${x2} ${y2} C ${x2 + d2.x * len} ${y2 + d2.y * len}, ${x1 + d1.x * len} ${y1 + d1.y * len}, ${x1} ${y1}`
    },
    headPath() {
      let x = this.x1, y = this.y1
      let dA = this.d1, rad = this.headRadius, len = this.headLength
      // mixture of tangent and average slope looks better
      let aAmount = 2, bAmount = 1
      let dB = {
        x: this.x2 - this.x1,
        y: this.y2 - this.y1,
      }
      let dBLength = Math.sqrt(dB.x * dB.x + dB.y * dB.y)
      let d = {
        x: dA.x * dBLength * aAmount + dB.x * bAmount,
        y: dA.y * dBLength * aAmount + dB.y * bAmount,
      }
      let factor = 1 / Math.sqrt(d.x * d.x + d.y * d.y)
      d.x *= factor
      d.y *= factor
      return `M ${x - d.y * rad + d.x * len} ${y + d.x * rad + d.y * len} L ${x} ${y} L ${x + d.y * rad + d.x * len} ${y - d.x * rad + d.y * len}`
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
  <path :class="{ edge: true, active: active, arrow: arrow, gap: gap }" :d="path" fill="none" />
  <path :class="{ head: true, arrow: arrow }" :d="headPath" fill="none" />
</template>

<style scoped>
.edge {
  stroke: var(--color-text);
  stroke-width: 0.05;
  stroke-linecap: round;
  stroke-dasharray: 0 0.12;
}
.edge.active {
  stroke: #bbb;
  stroke-dasharray: none;
}
.edge.active.gap {
  stroke-dasharray: 0 0.2 100;
}
.edge.active.arrow {
  stroke: var(--color-text);
  stroke-dasharray: none;
}
.head {
  stroke: var(--color-text);
  stroke-width: 0.05;
  stroke-linecap: round;
  visibility: hidden;
}
.head.arrow {
  visibility: visible;
}

</style>
