<script setup>
import getControlVector from '../ControlVector.js'
</script>

<script>
export default {
  props: {
    dLength: Number,
    headRadius: Number,
    headLength: Number,
    node1: Number,
    node2: Number,
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
    prevNode() {
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
    nextNode() {
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
    node0() {
      return this.index > this.start &&
        this.node1 == this.history[this.index] ?
        this.nextNode : this.prevNode
    },
    node3() {
      return this.index > this.start &&
        this.node2 == this.history[this.index - 1] ?
        this.prevNode : this.nextNode
    },
    arrow() {
      return (this.node1 == this.hole && this.node2 == this.tail) -
        (this.node2 == this.hole && this.node1 == this.tail)
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
      if (this.arrow == 0) {
        return ''
      }

      let x = this.x1, y = this.y1, dA = this.d1
      if (this.arrow < 0) {
        x = this.x2, y = this.y2, dA = this.d2
      }

      // mixture of tangent and average slope looks better
      let aAmount = 2, bAmount = 1
      let dB = {
        x: (this.x2 - this.x1) * this.arrow,
        y: (this.y2 - this.y1) * this.arrow,
      }
      let dBLength = Math.sqrt(dB.x * dB.x + dB.y * dB.y)
      let d = {
        x: dA.x * dBLength * aAmount + dB.x * bAmount,
        y: dA.y * dBLength * aAmount + dB.y * bAmount,
      }
      let factor = 1 / Math.sqrt(d.x * d.x + d.y * d.y)
      d.x *= factor
      d.y *= factor
      let rad = this.headRadius, len = this.headLength
      return `M ${x - d.y * rad + d.x * len} ${y + d.x * rad + d.y * len} L ${x} ${y} L ${x + d.y * rad + d.x * len} ${y - d.x * rad + d.y * len}`
    },
  },
  methods: {
    getX(node) {
      return Math.sin(2 * Math.PI * node / this.size + 0.00001)
    },
    getY(node) {
      return -Math.cos(2 * Math.PI * node / this.size + 0.00001)
    },
  },
}
</script>

<template>
  <path class="edge" :d="path" fill="none" v-bind:mask="arrow ? 'none': 'url(#head-mask)'"/>
  <path :class="{ segment: true, active: active, arrow: arrow }" :d="path" fill="none" v-bind:mask="arrow ? 'none': 'url(#head-mask)'"/>
  <path v-if="arrow" class="head" :d="headPath" fill="none"/>
  <mask v-if="arrow" id="head-mask">
    <rect x="-1.2" y="-1.2" width="2.4" height="2.4" fill="white"></rect>
    <path :d="headPath" fill="none" stroke="black" stroke-width="0.18" stroke-linecap="round" stroke-linejoin="round"/>
  </mask>
</template>

<style scoped>
.edge {
  stroke: var(--color-text);
  stroke-width: 0.04;
  stroke-linecap: round;
  stroke-dasharray: 0.04 0.12;
  transition: d 0.5s;
}
.segment {
  stroke: var(--color-text);
  stroke-width: 0.04;
  stroke-linecap: round;
  opacity: 0;
  transition: opacity 0.5s, d 0.5s;
}
.segment.active {
  stroke-linecap: butt;
  opacity: 1;
}
.segment.arrow {
  stroke-width: 0.06;
  stroke-linecap: butt;
  transition: d 0.5s;
}
.head {
  stroke: var(--color-text);
  stroke-width: 0.06;
  stroke-linecap: round;
  stroke-linejoin: round;
}

</style>
