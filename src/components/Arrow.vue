<script setup>
import Head from './Head.vue'
</script>

<script>
export default {
  props: {
    path: String,
    length: Number,
    controlLength: Number,
    onPath: Boolean,
    aArrow: Boolean,
    bArrow: Boolean,
    aOldArrow: Boolean,
    bOldArrow: Boolean,
    suppressOldArrow: Boolean,
  },
  computed: {
    strokeRadius() {
      return 2 // half of stroke-width
    },
    dashLength() {
      // cut off strokeRadius at the tip of the arrow to make sure the dash
      // doesn't stick out in front.
      return (this.onPath ? 20 : 11) - this.strokeRadius
    },
    aShown() {
      return this.aArrow ||
        (this.aOldArrow && !this.bArrow && !this.suppressOldArrow)
    },
    bShown() {
      return this.bArrow ||
        (this.bOldArrow && !this.aArrow && !this.suppressOldArrow)
    },
    animationDuration() {
      let seconds = 0.25 * 0.0045 * this.length + 0.75 * 0.45
      return `${seconds}s`
    },
  },
}
/*
aArrow bArrow aOldArrow bOldArrow suppressOldArrow visibility dasharray disappear suppress
0      0      0         0                          0                    0
1      0      0         0                          1          A         0         0
0      1      0         0                          1          B         0         0
0      0      1         0         0                0          A         A         0
0      1      1         0                          1          B         A         0
0      0      0         1         0                0          B         B         0
1      0      0         1                          1          A         B         0
0      0      1         0         1                                     A         1
0      0      0         1         1                                     B         1

suppress = suppressOldArrow && !aArrow && !bArrow
disappearA = aOldArrow
disappearB = aOldArrow
dasharrayA = aArrow || (aOldArrow && !bArrow)
dasharrayB = bArrow || (bOldArrow && !aArrow)
visibility = aArrow || bArrow
*/
</script>

<template>
  <Head
    :shown="aShown"
    :disappear="aOldArrow"
    :path="path"
    :length="length"
    :offset="7"
  />
  <Head
    :shown="bShown"
    :disappear="bOldArrow"
    :path="path"
    :length="length"
    :offset="-7"
  />
  <path
    :class="{
      tail: true,
      aShown: aShown,
      bShown: bShown,
      aDisappear: aOldArrow,
      bDisappear: bOldArrow,
    }"
    :d="path"
    :pathLength="length"
    :style="{
      '--dash-length': dashLength,
      '--non-dash-length': length - dashLength - strokeRadius,
      '--dash-offset': -strokeRadius,
      '--duration': animationDuration,
    }"
  />
</template>

<style scoped>
.tail {
  fill: none;
  stroke: var(--color-text);
  stroke-width: 4;
  stroke-linecap: round;
  visibility: hidden;
}

.canAnimate .tail {
  transition: d 0.5s;
}

.tail.aShown {
  visibility: initial;
  stroke-dasharray: var(--dash-length) 100%;
  stroke-dashoffset: var(--dash-offset);
}

.tail.bShown {
  visibility: initial;
  stroke-dasharray: 100% var(--non-dash-length) var(--dash-length) 100%;
  stroke-dashoffset: 100%;
}

.tail.aDisappear, .tail.bDisappear {
  visibility: hidden;
}

.tail.aDisappear {
  animation: aDisappear 0s;
}

@keyframes aDisappear {
  from { visibility: initial; }
  to { visibility: initial; }
}

.tail.bDisappear {
  animation: bDisappear 0s;
}

@keyframes bDisappear {
  from { visibility: initial; }
  to { visibility: initial; }
}

.canAnimate .tail {
  animation-duration: var(--duration);
}

.tail.bDisappear.aShown, .tail.aDisappear.bShown {
  visibility: initial;
  animation-duration: 0;
}

.tail:not(.aShown, .bShown) {
  visibility: hidden !important;
}
</style>
