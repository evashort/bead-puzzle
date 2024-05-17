<script>
export default {
  data() {
    return {
      offsetChange: 0,
    }
  },
  props: {
    path: String,
    offset: Number,
    totalLength: Number,
    reverse: Boolean,
    hole: Number,
    won: Boolean,
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
    transitionDuration() {
      return 0.75 * Math.pow(this.offsetChange / 150, 0.1)
    },
    imageId() {
      return this.won ? '#star' : '#star-small'
    },
  },
  watch: {
    offset(newOffset, oldOffset) {
      this.offsetChange = Math.abs(
        (newOffset == Infinity ? this.totalLength : newOffset) -
          (oldOffset == Infinity ? this.totalLength : oldOffset)
      )
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
      :href="imageId"
      :class="{ trophy: true, reverse: reverse, hidden: !visible }"
      :style="{
        offsetPath: `path('${path}')`,
        offsetDistance: offset == Infinity ? '100%' : `${offset}px`,
        transitionDuration: `${transitionDuration}s`,
      }"
    />
  </g>
</template>

<style scoped>
.trophy {
  transition-property: none;
  transform: scale(2.7) rotate(90deg);
  offset-rotate: reverse;
  pointer-events: none;
}
.canAnimate .trophy {
  transition-property: offset-distance;
}
.trophy.reverse {
  offset-rotate: auto;
}
.trophy.hidden {
  visibility: hidden;
}
</style>
