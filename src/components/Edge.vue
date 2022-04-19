<script setup>
import AnimProp from '../AnimProp.js'
import cubicBezier from '../CubicBezier.js'
</script>

<script>
const easeOut = cubicBezier(0, 0, 0.58, 1)

export default {
  data() {
    let d1 = this.getD1(this.x0, this.y0)
    let d2 = this.getD2(this.x3, this.y3)
    return {
      activeAnim: new AnimProp(this.active ? 1 : 0, 150, easeOut),
      dx1Anim: new AnimProp(d1.x, 150, easeOut),
      dy1Anim: new AnimProp(d1.y, 150, easeOut),
      dx2Anim: new AnimProp(d2.x, 150, easeOut),
      dy2Anim: new AnimProp(d2.y, 150, easeOut),
    }
  },
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
    dashArray() {
      return `${this.activeAnim.value * 0.12} ${(1 - this.activeAnim.value) * 0.12}`
    },
    dashOffset() {
      return 0.06 * this.activeAnim.value
    },
    path() {
      return `M ${this.x1} ${this.y1} C ${this.x1 + this.dx1Anim.value} ${this.y1 + this.dy1Anim.value}, ${this.x2 + this.dx2Anim.value} ${this.y2 + this.dy2Anim.value}, ${this.x2} ${this.y2}`
    }
  },
  methods: {
    getD1(x0, y0) {
      return this.getD(
        this.x2 - this.x1,
        this.y2 - this.y1,
        x0 - this.x1,
        y0 - this.y1,
      )
    },
    getD2(x3, y3) {
      return this.getD(
        this.x1 - this.x2,
        this.y1 - this.y2,
        x3 - this.x2,
        y3 - this.y2,
      )
    },
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
  watch: {
    active(newActive, oldActive) {
      this.activeAnim.set(newActive ? 1 : 0)
    },
    x0(newX0, oldX0) {
      let d1 = this.getD1(newX0, this.y0)
      this.dx1Anim.set(d1.x)
      this.dy1Anim.set(d1.y)
    },
    y0(newY0, oldY0) {
      let d1 = this.getD1(this.x0, newY0)
      this.dx1Anim.set(d1.x)
      this.dy1Anim.set(d1.y)
    },
    x3(newX3, oldX3) {
      let d2 = this.getD2(newX3, this.y3)
      this.dx2Anim.set(d2.x)
      this.dy2Anim.set(d2.y)
    },
    y3(newY3, oldY3) {
      let d2 = this.getD2(this.x3, newY3)
      this.dx2Anim.set(d2.x)
      this.dy2Anim.set(d2.y)
    },
  },
}
</script>

<template>
  <path class="edge" :d="path" :stroke-dasharray="dashArray" :stroke-dashoffset="dashOffset" fill="none" />
</template>

<style scoped>
.edge {
  stroke: var(--color-text);
  stroke-width: 0.05;
  stroke-linecap: round;
}

</style>
