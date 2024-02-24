<script>
export default {
  props: {
    path: String,
    offset: Number,
    reverse: Boolean,
    hole: Number,
    size: Number,
    radius: Number,
    holeRadius: Number,
  },
  computed: {
    x() {
      return this.radius * Math.sin(2 * Math.PI * this.hole / this.size)
    },
    y() {
      return -this.radius * Math.cos(2 * Math.PI * this.hole / this.size)
    },
  },
}
</script>

<template>
  <mask :id="`trophy-mask-${hole}`">
    <circle
      :cx="x"
      :cy="y"
      :r="holeRadius"
      fill="white"
    >
    </circle>
  </mask>
  <g :mask="`url(#trophy-mask-${hole})`">
    <use
      href="#star-small"
      :class="{ trophy: true, reverse: reverse }"
      :style="{ offsetPath: `path('${path}')`, offsetDistance: `${offset}px`}"
    />
  </g>
</template>

<style scoped>
.trophy {
  transition: offset-distance 0.75s;
  transform: scale(2.7) rotate(90deg);
  offset-rotate: reverse;
}
.trophy.reverse {
  offset-rotate: auto;
}
</style>
