<script setup>
import AnimProp from '../AnimProp.js'
import cubicBezier from '../CubicBezier.js'
</script>

<script>
export default {
  data() {
    return {
      activeAnim: new AnimProp(this.active ? 1 : 0, 150, this.setActive, cubicBezier(0, 0, 0.58, 1)),
    }
  },
  props: {
    x1: Number,
    y1: Number,
    x2: Number,
    y2: Number,
    active: Boolean,
  },
  computed: {
    dashArray() {
      return `${this.activeAnim.value * 0.12} ${(1 - this.activeAnim.value) * 0.12}`
    },
    dashOffset() {
      return 0.06 * this.activeAnim.value
    },
  },
  watch: {
    active(newActive, oldActive) {
      this.activeAnim.set(newActive ? 1 : 0)
    },
  },
}
</script>

<template>
  <line class="edge" :x1="x1" :y1="y1" :x2="x2" :y2="y2" :stroke-dasharray="dashArray" :stroke-dashoffset="dashOffset" />
</template>

<style scoped>
.edge {
  stroke: var(--color-text);
  stroke-width: 0.05;
  stroke-linecap: round;
}

</style>
