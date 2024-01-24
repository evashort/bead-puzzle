<script>
export default {
  props: {
    shown: Boolean,
    path: String,
    length: Number,
    offset: Number,
  },
  computed: {
    headRadius() {
      return 12
    },
    headHeight() {
      return this.headRadius * Math.sqrt(1.5)
    },
    headPath() {
      let r = this.headRadius, h = this.headHeight
      return `M ${-h} ${-r} L ${0} ${0} L ${-h} ${r}`
    },
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
      // TODO: 15*3t(1-t)^2+85*3(1-t)t^2+100*t^3 from 0 to 1
      // 50x + 25 - 25cos(pi*x) from 0 to 1
      return (this.offset + this.length * this.facingB) / this.length
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
    class="headGroup"
    :style="{ transform: `translate(${x}px, ${y}px) rotate(${angle}rad) translateX(${Math.abs(offset)}px)` }"
  >
    <path v-if=shown :d="headPath" class="shadow"/>
    <path v-if=shown :d="headPath" class="head"/>
  </g>
</template>

<style scoped>
.headGroup {
  transition: transform 0.5s;
}
.head {
  stroke: var(--color-text);
  stroke-width: 4;
  stroke-linecap: round;
  stroke-linejoin: round;
  fill: none;
}
.shadow {
  stroke: var(--color-background);
  stroke-width: 12;
  stroke-linecap: round;
  stroke-linejoin: round;
  fill: none;
}
.facingA {
  offset-rotate: reverse;
}
</style>
