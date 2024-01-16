<script>
export default {
  props: {
    shown: Boolean,
    path: String,
    facingA: Boolean,
    headRadius: Number,
    radius: Number,
    strokeWidth: Number,
    shadowWidth: Number,
  },
  computed: {
    headHeight() {
      return this.headRadius * Math.sqrt(1.5)
    },
    offsetDistance() {
      // tuned based on what makes the arrow look best
      let averageEdgeLength = 1.6 * this.radius
      let offsetFraction = 0.5 * this.headHeight / averageEdgeLength
      if (!this.facingA) {
        offsetFraction = 1 - offsetFraction
      }

      return 100 * offsetFraction + '%'
    },
    headPath() {
      let r = this.headRadius, hr = 0.5 * this.headHeight
      return `M ${-hr} ${-r} L ${hr} ${0} L ${-hr} ${r}`
    },
    coneRadius() {
      // there is a notch in the back of the arrow head shadow to prevent it
      // from covering the arrow tail. the notch is exactly as wide as the
      // arrow tail where the head and tail intersect, but it gets wider
      // further away from the intersection in case the arrow tail is slightly
      // curved. this value controls the width of the widest part of the
      // notch. it should be larger than 0.5 * strokeWidth
      return this.strokeWidth
    },
    shadowPath() {
      // I put a lot of work into creating a shape that would cover any edges
      // below it except for the tail of the arrow. I did it because the tail
      // of the arrow sometimes needs to be underneath the "terminator"
      // circle, so I can't put the tail above the head.
      //   headHeight = 2 * heightRadius (hr)
      //   ⌜⎺⌝
      //   \  ⎫
      //    \ ⎬headRadius (r)
      // ____\⎭
      //     /   note: these measurements are taken as if shadowWidth is zero
      //    /    (it's not) and named as if the arrow is pointing upward (it's
      //   /     pointing right)
      let r = this.headRadius, hr = 0.5 * this.headHeight
      //  ⌢
      // \  \       /
      //  ︡_> )  sin ︡⎸ sr (shadowRadius; half of shadow's "stroke width")
      // /︡―┄/┄┄┄┄┄> ―cos―︡―       /
      //  ⌣      /              /
      let cos = this.headHeight, sin = this.headRadius
      let cot = cos / sin
      let sr = 0.5 * this.shadowWidth
      let scale = sr / Math.sqrt(cos * cos + sin * sin)
      cos *= scale
      sin *= scale
      let tr = 0.5 * this.strokeWidth
      // fr is head stroke radius, which happens to be the same as tail stroke
      // radius
      let fr = tr
      // distance from center of arrow head to the concave corner, if the
      // stroke had unit radius
      let v = sr / sin
      let cr = this.coneRadius
      //  ⌢
      // \  \
      let upperFin = `M ${-hr - sin} ${-r + cos} A ${sr} ${sr} 0 0 1 ${-hr + sin} ${-r - cos} L ${hr + sin} ${-cos} `
      //     )
      let nose = `A ${sr} ${sr} 0 0 1 ${hr + sin} ${cos} `
      // /  /
      //  ⌣
      let lowerFin = `L ${-hr + sin} ${r + cos} A ${sr} ${sr} 0 0 1 ${-hr + -sin} ${r - cos} L ${hr - sr * v - cr * cot} ${cr} `
      //  ︡_>
      // note that the angle of the ︡_ part may be wider or narrower than the
      // angle of the > part depending on coneRadius. the angle changes right
      // at the intersection of the head and the tail.
      let notch = `L ${hr - fr * v - tr * cot} ${tr} L ${hr} ${0} L ${hr - fr * v - tr * cot} ${-tr} L ${hr - sr * v - cr * cot} ${-cr} Z`
      //  ⌢
      // \  \
      //  ︡_> )
      // /  /
      //  ⌣
      return upperFin + nose + lowerFin + notch
    },
  },
}
</script>

<template>
  <g
    v-if=shown
    :class="{ facingA: facingA }"
    :style="{ 'offset-path': `path('${path}')`, 'offset-distance': offsetDistance }"
  >
    <path :d="shadowPath" class="shadow"/>
    <path :d="headPath" class="head"/>
  </g>
</template>

<style scoped>
.head {
  stroke: var(--color-text);
  stroke-width: 4;
  stroke-linecap: round;
  stroke-linejoin: round;
  fill: none;
}
.shadow {
  fill: var(--color-background);
}
.facingA {
  offset-rotate: reverse;
}
</style>
