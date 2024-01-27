<script setup>
import Head from './Head.vue'
</script>

<script>
export default {
  props: {
    path: String,
    length: Number,
    controlLength: Number,
    aArrow: Boolean,
    bArrow: Boolean,
    aOldArrow: Boolean,
    bOldArrow: Boolean,
    suppressOldArrow: Boolean,
  },
}
</script>

<template>
  <Head
    :shown="aArrow || (aOldArrow && !suppressOldArrow)"
    :disappear="aOldArrow"
    :path="path"
    :length="length"
    :controlLength="controlLength"
    :offset="7"
  />
  <Head
    :shown="bArrow || (bOldArrow && !suppressOldArrow)"
    :disappear="bOldArrow"
    :path="path"
    :length="length"
    :controlLength="controlLength"
    :offset="-7"
  />
  <!-- TODO: make sure aArrow class is not set based on aOldArrow if bArrow is
       true -->
  <path
    :class="{ tail: true, aArrow: aArrow || (aOldArrow && !suppressOldArrow), bArrow: bArrow || (bOldArrow && !suppressOldArrow), disappear: (aOldArrow || bOldArrow) && !(aArrow || bArrow) }"
    :d="path"
    :pathLength="length"
    :style="{ '--dash-length': 20, '--non-dash-length': length - 20 }"
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

.tail.aArrow {
  visibility: initial;
  stroke-dasharray: var(--dash-length) 100%;
}

.tail.bArrow {
  visibility: initial;
  stroke-dasharray: 100% var(--non-dash-length);
  stroke-dashoffset: 100%;
}

.tail.disappear {
  visibility: hidden;
}

.canAnimate .tail.aArrow.disappear {
  animation: disappear 0.45s;
}

@keyframes disappear {
  from { visibility: initial; }
  to { visibility: initial; }
}

.canAnimate .tail.bArrow.disappear {
  animation: disappear2 0.45s;
}

@keyframes disappear2 {
  from { visibility: initial; }
  to { visibility: initial; }
}
</style>
