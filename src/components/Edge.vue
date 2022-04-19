<script setup>
import AnimProp from '../AnimProp.js'
import cubicBezier from '../CubicBezier.js'
</script>

<script>
const easeOut = cubicBezier(0, 0, 0.58, 1)

export default {
  data() {
    let d1 = this.getD(
      this.x2 - this.x1,
      this.y2 - this.y1,
      this.x0 - this.x1,
      this.y0 - this.y1,
    )
    let d2 = this.getD(
      this.x1 - this.x2,
      this.y1 - this.y2,
      this.x3 - this.x2,
      this.y3 - this.y2,
    )
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
      return `M ${this.x1} ${this.y1} C ${this.x1 + this.dx1Anim.value} ${this.y1 + this.dy1Anim.value}, ${this.x2 + this.dx2Anim.value} ${this.y2 + this.dy2Anim.value}, ${this.x2} ${this.y2}`
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
  watch: {
    active(newActive, oldActive) {
      this.activeAnim.set(newActive ? 1 : 0)
    },
    d1(newD1, oldD1) {
      this.dx1Anim.set(newD1.x)
      this.dy1Anim.set(newD1.y)
    },
    d2(newD2, oldD2) {
      this.dx2Anim.set(newD2.x)
      this.dy2Anim.set(newD2.y)
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
