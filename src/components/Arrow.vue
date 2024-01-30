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
    dashLength() {
      return this.onPath ? 20 : 11
    },
    aShown() {
      return this.aArrow ||
        (this.aOldArrow && !this.bArrow && !this.suppressOldArrow)
    },
    bShown() {
      return this.bArrow ||
        (this.bOldArrow && !this.aArrow && !this.suppressOldArrow)
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
      '--non-dash-length': length - dashLength
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
}

.tail.bShown {
  visibility: initial;
  stroke-dasharray: 100% var(--non-dash-length);
  stroke-dashoffset: 100%;
}

.canAnimate .tail.aDisappear {
  animation: aDisappear 0.45s;
}

@keyframes aDisappear {
  from { visibility: initial; }
  to { visibility: initial; }
}

.canAnimate .tail.bDisappear {
  animation: bDisappear 0.45s;
}

@keyframes bDisappear {
  from { visibility: initial; }
  to { visibility: initial; }
}

.tail:not(.aShown, .bShown) {
  visibility: hidden !important;
}
</style>
