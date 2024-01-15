<script setup>
import Permute from '../Permute.js'
</script>

<script>
export default {
  props: {
    size: Number,
    beads: Number,
    radius: Number,
    clickRadius: Number,
  },
  computed: {
    colorNames() {
      return [
        [],
        ['gray'],
        ['gray', 'blue'],
        ['gray', 'yellow', 'blue'],
        ['gray', 'red', 'yellow', 'blue'],
        ['gray', 'red', 'yellow', 'cyan', 'blue'],
        ['gray', 'red', 'yellow', 'cyan', 'blue', 'pink'],
        ['gray', 'red', 'yellow', 'green', 'cyan', 'blue', 'pink'],
      ][this.size]
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
    shownColorNames() {
      if (this.beads == 0) {
        // permutation index 0 is 0, 1, 2, 3, 4...
        return new Set(this.colorNames)
      }

      let result = new Set()
      for (
        let [i, bead] of Permute.fromIndex(this.beads, this.size).entries()
      ) {
        if (bead == i && i > 0) {
          result.add(this.colorNames[i])
        }
      }

      return result
    },
    centers() {
      let result = {}
      for (let [i, name] of this.colorNames.entries()) {
        let angle = 2 * Math.PI * i / this.size
        result[name] = {
          x: this.radius * Math.sin(angle),
          y: this.radius * -Math.cos(angle),
        }
      }

      return result
    }
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
  <circle
    v-for="name in shownColorNames"
    :fill="`url('#${name}-glow')`"
    :r="clickRadius * glowRadius"
    :cx="centers[name].x"
    :cy="centers[name].y"
  />
  <circle
    v-for="name in colorNames"
    fill="var(--color-background)"
    :r="clickRadius"
    :cx="centers[name].x"
    :cy="centers[name].y"
    :class="{hole: true, glowing: shownColorNames.has(name)}"
    :style="{ '--glow-color': colors[name] }"
  />
</template>

<style scoped>
.hole {
  stroke: #444444;
  stroke-width: 1px;
}
.hole.glowing {
  stroke: var(--glow-color);
  stroke-width: 0.75;
}
</style>
