<script>
export default {
  props: {
    shown: Boolean,
    disappear: Boolean,
    path: String,
    length: Number,
    controlLength: Number,
    offset: Number,
  },
  computed: {
    x() {
      return this.points ? this.bezier(this.t, ...this.points.map(p => p.x)) :
        0
    },
    y() {
      return this.points ? this.bezier(this.t, ...this.points.map(p => p.y)) :
        0
    },
    angle() {
      if (!this.points) {
        return 0
      }

      let dx = this.bezierSlope(this.t, ...this.points.map(p => p.x))
      let dy = this.bezierSlope(this.t, ...this.points.map(p => p.y))
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
      // https://en.wikipedia.org/wiki/B%C3%A9zier_curve#Cubic_B%C3%A9zier_curves
      // x = A(1-t)^3 + B*3t(1-t)^2 + C*3(1-t)t^2 + D*t^3
      // A = 0, B = c/l, C = 1 - c/l, D = 1
      // x = c/l*3t(1-t)^2 + (1-c/l)*3(1-t)t^2 + t^3
      // c/l = 0: x ~= 1/2 - cos(pi*t)/2
      // c/l = 1/3: x = t
      // x = 1/2 - cos(pi*t)/2
      // cos(pi*t)/2 = 1/2 - x
      // cos(pi*t) = 1 - 2x
      // pi*t = acos(1-2x)
      // t = acos(1-2x)/pi
      // t = (1 - 3c/l)acos(1-2x)/pi + 3c/l*x
      let x = (this.offset + this.length * this.facingB) / this.length
      // m = "how much does controlLength matter"
      // without this parameter, the formula assigns too much importance to
      // controlLength and the arrow heads are too far back. I decreased m
      // until none of the arrow tails stuck out in front of the arrow heads.
      let m = 0.3
      let ratio = Math.pow(3 * this.controlLength / this.length, m)
      return (1 - ratio) * Math.acos(1 - 2 * x) / Math.PI + ratio * x
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
  },
  methods: {
    bezier(x, a, b, c, d) {
      let y = 1 - x
      let e = y * a + x * b, f = y * b + x * c, g = y * c + x * d
      let h = y * e + x * f, i = y * f + x * g
      let j = y * h + x * i
      return j
    },
    bezierSlope(x, a, b, c, d) {
      // https://computergraphics.stackexchange.com/questions/10551/how-to-take-the-derivative-of-a-b%C3%A9zier-curve
      let r = b - a, s = c - b, t = d - c
      let y = 1 - x
      let u = y * r + x * s, v = y * s + x * t
      let w = y * u + x * v
      return 3 * w
    },
  },
}
</script>

<template>
  <g
    :class="{ head: true, shown: shown, disappear: disappear }"
    :style="{
      transform: `translate(${x}px, ${y}px) rotate(${angle}rad) translateX(${Math.abs(offset)}px)`
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
.canAnimate .head.disappear {
  animation: disappear 0.45s;
}
@keyframes disappear {
  from { visibility: initial; }
  to { visibility: initial; }
}
</style>
