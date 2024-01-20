<script>
export default {
  props: {
    shown: Boolean,
    path: String,
    atEnd: Boolean,
    strokeWidth: Number,
    radius: Number,
    degrees: Number,
  },
  computed: {
    minWidth() {
      return 1.5 * this.strokeWidth
    },
    lineEnd() {
      // r^2 = (x * cos(angle))^2 + (nr + x * sin(angle))^2
      // r^2 = x^2 * (cos^2(angle) + sin^2(angle)) + 2*nr*x*sin(angle) + nr^2
      // r^2 = x^2 + 2*nr*x*sin(angle) + nr^2 + (nr*sin(angle))^2-(nr*sin(angle))^2
      // r^2 = (x + nr*sin(angle))^2 + nr^2 - (nr*sin(angle))^2
      // r^2 - nr^2 + (nr*sin(angle))^2 = (x + nr*sin(angle))^2
      // sqrt(r^2 + nr^2 * (sin^2(angle) - 1)) = x + nr*sin(angle)
      // x = sqrt(r^2 - nr^2 * cos^2(angle)) - nr*sin(angle)
      let angle = 0.5 * (this.degrees * Math.PI / 180)
      let sin = Math.sin(angle), cos = Math.cos(angle)
      let r = this.radius, nr = 0.5 * this.minWidth
      let x = Math.sqrt(r * r - (nr * cos) * (nr * cos)) - nr * sin
      let l = x * cos, wr = nr + x * sin
      // console.log((l * l + wr * wr) + '=' + (r * r))
      return [l, wr]
    },
    outline() {
      //                     ┌─────r─────┐
      //                     ┌────l───┐
      //     ___---              ___---   ┐     ___---
      // ,---       \ nr_┌   ,---       \ wr ---___∢ degrees
      //  )          |   └sr⁽-)          |┘        ---
      // '---___    /        '---___    /  angle___---
      //        ---                 ---      ∡--------
      let nr = 0.5 * this.minWidth, sr = 0.5 * this.strokeWidth
      let r = this.radius, [l, wr] = this.lineEnd
      //     ___---
      //  ---       \
      //             |
      //            /
      let top = `M ${0} ${nr} L ${l} ${wr} A ${r} ${r} 0 0 0 ${l} ${-wr} `
      //  )
      // '---___
      //        ---
      let bottom = `L ${0} ${-nr} V ${-sr} A ${sr} ${sr} 0 0 1 ${0} ${sr} Z`
      return top + bottom
    },
    thinOutline() {
      let r = this.radius, [l, wr] = this.lineEnd
      let top = `M ${l} ${wr} L ${l} ${wr} A ${r} ${r} 0 0 0 ${l} ${-wr} `
      let bottom = `L ${l} ${-wr} V ${-wr} A ${r} ${r} 0 0 1 ${l} ${wr} Z`
      return top + bottom
    }
  },
}
</script>

<template>
  <path
    :d="shown ? outline : thinOutline"
    :class="{cover: true, atEnd: atEnd}"
    :style="{ 'offset-path': `path('${path}')` }"
  />
</template>

<style scoped>
.cover {
  fill: red;
  opacity: 0.5;
  transition: d 2s;
}
.atEnd {
  offset-distance: 100%;
  offset-rotate: reverse;
}
</style>
