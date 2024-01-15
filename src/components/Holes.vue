<script>
export default {
  props: {
    size: Number,
    radius: Number,
    clickRadius: Number,
  },
  computed: {
    colorNames() {
      return ['gray', 'red', 'yellow', 'green', 'cyan', 'blue', 'pink']
    },
    colors() {
      return {
        // source: http://tsitsul.in/blog/coloropt/
        gray: "#cacaca",
        red: "#b51d14",
        yellow: "#ddb310",
        green: "#00b25d",
        cyan: "#00beff",
        // the original blue #4053d3 was too dark on the black background so I
        // tried making it brighter two ways:
        // 1. turning the HSV value all the way up: #4d64ff
        // 2. turning the LCh chroma all the way up: #0750f4
        // I decided the optimal color was midway between the two:
        // color-mix(in lch, #4d64ff, #0750f4) = #3e59f0
        blue: "#3e59f0",
        pink: "#fb49b0",
      }
    },
    fadeWidths() {
      return {
        gray: 0.27,
        red: 0.33,
        yellow: 0.27,
        green: 0.3,
        cyan: 0.27,
        blue: 0.33,
        pink: 0.29,
      }
    },
    solidRadius() {
      return 1.1
    },
    glowRadius() {
      return this.solidRadius + Math.max(...Object.values(this.fadeWidths))
    },
    inPlace() {
      
    },
  },
}
</script>

<template>
  <defs>
    <radialGradient v-for="name in colorNames" :id="`${name}-glow`">
      <stop
        :offset="100 * solidRadius / glowRadius + '%'"
        :stop-color="colors[name]"
        stop-opacity="0.25"
      />
      <stop
        :offset="100 * (solidRadius + fadeWidths[name]) / glowRadius + '%'"
        stop-opacity="0"
      />
    </radialGradient>
  </defs>
  <g :transform="`translate(${x},${y})`">
    <use
      :href="`#${name}-outline`"
      :style="{ 'transform': `scale(${scale})` }"
    />
  </g>
</template>
