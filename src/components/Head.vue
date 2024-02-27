<script setup>
import Bezier from '../Bezier.js'
</script>

<script>
export default {
  props: {
    shown: Boolean,
    disappear: Boolean,
    path: String,
    length: Number,
    offset: Number,
  },
  computed: {
    x() {
      return this.points ? Bezier.value(...this.points.map(p => p.x), this.t) :
        0
    },
    y() {
      return this.points ? Bezier.value(...this.points.map(p => p.y), this.t) :
        0
    },
    angle() {
      if (!this.points) {
        return 0
      }

      let dx = Bezier.slope(...this.points.map(p => p.x), this.t)
      let dy = Bezier.slope(...this.points.map(p => p.y), this.t)
      let angle = Math.atan2(dy * this.sign, dx * this.sign)
      if (angle > this.straightAngle + Math.PI) {
        angle -= 2 * Math.PI
      } else if (angle <= this.straightAngle - Math.PI) {
        angle += 2 * Math.PI
      }

      return angle
    },
    straightAngle() {
      return Math.atan2(
        (this.points[3].y - this.points[0].y) * this.sign,
        (this.points[3].x - this.points[0].x) * this.sign,
      )
    },
    t() {
      return Bezier.estimateParameter(
        this.length,
        this.controlLength,
        this.offset + this.length * this.facingB,
      )
    },
    controlLength() {
      let point = this.facingB ? this.points[3] : this.points[0]
      let control = this.facingB ? this.points[2] : this.points[1]
      let dx = control.x - point.x, dy = control.y - point.y
      return Math.sqrt(dx * dx + dy * dy)
    },
    sign() {
      return this.facingB ? 1 : -1
    },
    facingB() {
      // take the reciprocal to allow negative zero
      // https://dev.to/emnudge/identifying-negative-zero-2j1o
      return 1 / this.offset < 0
    },
    points() {
      let match = this.path.match(this.pathPattern)
      if (!match) {
        return null
      }

      let [, x1, y1, cx1, cy1, cx2, cy2, x2, y2] = match
      return [
        { x: parseFloat(x1), y: parseFloat(y1) },
        { x: parseFloat(cx1), y: parseFloat(cy1) },
        { x: parseFloat(cx2), y: parseFloat(cy2) },
        { x: parseFloat(x2), y: parseFloat(y2) },
      ]
    },
    pathPattern() {
      // https://www.w3.org/TR/SVG11/paths.html#PathDataBNF
      // regex can't parse SVG path syntax properly because backtracking allows
      // "56" to be parsed as "5, 6", so we parse using a very simplified
      // approximation of the syntax which assumes that the path has no syntax
      // errors and that numbers are separated (e.g. "-5-6" won't occur).
      let number = '[-+0-9.eE]+'
      let arg = `(${number})`
      let wsp = '[ \\t\\r\\n]*'
      let sep = `[, \\t\\r\\n]+`
      let curve = [
        [arg, arg].join(sep),
        'C',
        [arg, arg, arg, arg, arg, arg].join(sep),
      ].join(wsp)
      return new RegExp(curve)
    },
    animationDuration() {
      let seconds = 0.25 * 0.0045 * this.length + 0.75 * 0.45
      return `${seconds}s`
    },
  },
}
</script>

<template>
  <g
    :class="{ head: true, shown: shown, disappear: disappear }"
    :style="{
      transform: `translate(${x}px, ${y}px) rotate(${angle}rad) translateX(${Math.abs(offset)}px)`,
      '--duration': animationDuration,
    }"
  >
    <use v-if=shown href="#head-shadow"/>
    <use v-if=shown href="#head-stroke"/>
  </g>
</template>

<style scoped>
.head {
  visibility: hidden;
}
.head.shown {
  visibility: initial;
}
.canAnimate .head {
  transition: transform 0.7s -0.2s;
}
.head.disappear {
  visibility: hidden;
}
.head.disappear {
  animation: disappear 0s;
}
@keyframes disappear {
  from { visibility: initial; }
  to { visibility: initial; }
}
.canAnimate .head.disappear {
  animation-duration: var(--duration);
}
.head:not(.shown) {
  visibility: hidden !important;
}
</style>
