<script setup>
import { Visibility } from '../Visibility'
</script>

<script>
export default {
  data() {
    return {
      aDelay: this.a.delay,
      bDelay: this.b.delay,
    }
  },
  props: {
    path: String,
    length: Number,
    onPath: Boolean,
    gap: Number,
    a: Visibility,
    b: Visibility,
    masked: Boolean,
    arrow: Boolean,
  },
  computed: {
    dashArray() {
      let dash = 4, space = 12
      let result = null
      if (this.aHidden && !this.masked) {
        let overlap = this.gap % (dash + space)
        if (overlap < dash) {
          result = [0, this.gap, dash - overlap, space]
        } else {
          result = [0, this.gap + dash + space - overlap]
        }

        let dashCount = Math.floor((this.length - this.gap) / (dash + space))
        for (; dashCount > 0; dashCount--) {
          result.push(dash, space)
        }
      } else if (this.bHidden && !this.masked) {
        result = []
        let dashCount = Math.floor((this.length - this.gap) / (dash + space))
        for (; dashCount > 0; dashCount--) {
          result.push(dash, space)
        }

        let extra = (this.length - this.gap) % (dash + space)
        result.push(Math.min(dash, extra))
        result.push('100%')
      } else if (this.aHidden) {
        result = []
        let dashCount = Math.floor(this.gap / (dash + space))
        for (; dashCount > 0; dashCount--) {
          result.push(dash, space)
        }

        let extra = this.gap % (dash + space)
        if (extra > dash) {
          result.push(dash, extra - dash)
        }

        result.push('100%')
      } else if (this.bHidden) {
        let overlap = (this.length - this.gap) % (dash + space)
        let extra = Math.min(dash - overlap, 0)
        result = [this.length - this.gap + extra, space + extra]
        let dashCount = Math.floor(this.length / (dash + space)) -
          Math.floor((this.length - this.gap) / (dash + space))
        for (; dashCount > 0; dashCount--) {
          result.push(dash, space)
        }
      } else {
        result = [dash, space]
      }

      return result.join(' ')
    },
    aHidden() {
      return this.hidden(this.a)
    },
    bHidden() {
      return this.hidden(this.b)
    },
  },
  methods: {
    hidden(visibility) {
      return visibility == Visibility.Hidden ||
        visibility == Visibility.DelayHidden
    },
    delay(visibility) {
      return visibility == Visibility.DelayHidden ||
        visibility == Visibility.DelayShown
    },
  },
  watch: {
    a(newA, oldA) {
      if (this.hidden(newA) != this.hidden(oldA)) {
        this.aDelay = this.delay(newA)
        this.bDelay &&= !this.aDelay
      }
    },
    b(newB, oldB) {
      if (this.hidden(newB) != this.hidden(oldB)) {
        this.bDelay = this.delay(newB)
        this.aDelay &&= !this.bDelay
      }
    },
    arrow(newArrow, oldArrow) {
      if (newArrow) {
        this.aDelay = false
        this.bDelay = false
      }
    },
  },
}
</script>

<template>
  <path
    :class="{
      edge: true,
      onPath: onPath,
      masked: masked,
      aHidden: aHidden && !arrow,
      bHidden: bHidden && !arrow,
      aDelay: aDelay,
      bDelay: bDelay,
    }"
    :d="path"
    :pathLength="length"
    :style="{
      '--gap': gap,
      '--non-gap': length - gap,
      '--dash-array': dashArray,
    }"
  />
</template>

<style scoped>
.edge {
  fill: none;
  stroke: var(--color-text);
  stroke-width: 4;
  stroke-linecap: round;
  stroke-dasharray: var(--dash-array);
}

.canAnimate .edge {
  transition: d 0.5s;
}

.edge.onPath {
  stroke-dasharray: none;
}

.edge.onPath.aHidden {
  stroke-dasharray: 0 var(--gap) 100%;
}

.edge.onPath.bHidden {
  stroke-dasharray: var(--non-gap) 100%;
}

.edge.onPath.masked {
  stroke-dasharray: var(--dash-array);
}

.canAnimate .edge.aHidden.aDelay {
  animation: hideStart 0.45s ease 0.3s backwards;
}

.canAnimate .edge.aDelay {
  animation: revealStart 0.45s ease 0.3s backwards;
}

.canAnimate .edge.bHidden.bDelay {
  animation: hideEnd 0.45s ease 0.3s backwards;
}

.canAnimate .edge.bDelay {
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
