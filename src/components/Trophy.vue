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
    visible: Boolean,
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
  <!--<path :d="path" fill="none" stroke="red"/>-->
  <mask :id="`trophy-mask-${hole}`" v-if="visible">
    <circle
      :cx="x"
      :cy="y"
      :r="holeRadius"
      fill="white"
    >
    </circle>
  </mask>
  <g :mask="visible ? `url(#trophy-mask-${hole})` : 'none'">
    <use
      href="#star-small"
      :class="{ trophy: true, reverse: reverse, hidden: !visible }"
      :style="{ offsetPath: `path('${path}')`, offsetDistance: offset == Infinity ? '100%' : `${offset}px`}"
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
.trophy.hidden {
  visibility: hidden;
}
</style>
