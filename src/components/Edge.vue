<script setup>
import { HiddenEnd } from '../HiddenEnd'
</script>

<script>
export default {
  data() {
    return {
      animate: false,
      reversed: false,
    }
  },
  props: {
    path: String,
    length: Number,
    onPath: Boolean,
    hiddenEnd: HiddenEnd,
  },
  computed: {
    hidden() {
      return this.hiddenEnd == HiddenEnd.A ||
        this.hiddenEnd == HiddenEnd.B ||
        this.hiddenEnd == HiddenEnd.DelayA ||
        this.hiddenEnd == HiddenEnd.DelayB
    }
  },
  watch: {
    hiddenEnd: {
      handler(newHiddenEnd, oldHiddenEnd) {
        let oldShown = oldHiddenEnd == HiddenEnd.None ||
          oldHiddenEnd == HiddenEnd.DelayNone
        let newShown = newHiddenEnd == HiddenEnd.None ||
          newHiddenEnd == HiddenEnd.DelayNone
        if (newShown != oldShown) {
          this.animate = newHiddenEnd == HiddenEnd.DelayA ||
            newHiddenEnd == HiddenEnd.DelayB ||
            newHiddenEnd == HiddenEnd.DelayNone
        }

        if (!newShown) {
          this.reversed = newHiddenEnd == HiddenEnd.B ||
            newHiddenEnd == HiddenEnd.DelayB
        }
      },
      immediate: true,
    },
  },
}
</script>

<template>
  <path
    :class="{ edge: true, onPath: onPath, hidden: hidden, animate: animate, reversed: reversed }"
    :d="path"
    :pathLength="length"
    :style="{ '--gap': 28, '--non-gap': length - 28 }"
  />
</template>

<style scoped>
.edge {
  fill: none;
  stroke: var(--color-text);
  stroke-width: 4;
  stroke-linecap: round;
  stroke-dasharray: 4 12;
}

.canAnimate .edge {
  transition: d 0.5s;
}

.edge.onPath {
  stroke-dasharray: none;
}

.edge.onPath.hidden {
  stroke-dasharray: 0 var(--gap) 100%;
}

.edge.onPath.hidden.reversed {
  stroke-dasharray: var(--non-gap) 100%;
}

.canAnimate .edge.animate.hidden {
  animation: hideStart 0.45s ease 0.3s backwards;
}

.canAnimate .edge.animate.onPath {
  animation: revealStart 0.45s ease 0.3s backwards;
}

.canAnimate .edge.animate.hidden.reversed {
  animation: hideEnd 0.45s ease 0.3s backwards;
}

.canAnimate .edge.animate.onPath.reversed {
  animation: revealEnd 0.45s ease 0.3s backwards;
}

@keyframes hideStart {
  from { stroke-dasharray: var(--gap) 0 100%; }
  to { stroke-dasharray: 0 var(--gap) 100%; }
}

@keyframes revealStart {
  from { stroke-dasharray: 0 var(--gap) 100%; }
  to { stroke-dasharray: var(--gap) 0 100%; }
}

@keyframes hideEnd {
  from { stroke-dasharray: var(--non-gap) 0 100% }
  to { stroke-dasharray: var(--non-gap) var(--gap) 100% }
}

@keyframes revealEnd {
  from { stroke-dasharray: var(--non-gap) var(--gap) 100% }
  to { stroke-dasharray: var(--non-gap) 0 100% }
}
</style>
