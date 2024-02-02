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
    a: { hidden: Boolean, delay: Boolean },
    b: { hidden: Boolean, delay: Boolean },
    arrow: Boolean,
  },
  computed: {
    dashArray() {
      let dash = 4, space = 12
      if (!this.a.hidden && !this.b.hidden) {
        return [dash, space].join(' ')
      }

      let dashCount = Math.floor((this.length - this.gap) / (dash + space))
      let result = null
      if (this.a.hidden) {
        let overlap = this.gap % (dash + space)
        if (overlap < dash) {
          result = [0, this.gap, dash - overlap, space]
        } else {
          result = [0, this.gap + dash + space - overlap]
        }
        for (; dashCount > 0; dashCount--) {
          result.push(dash, space)
        }
      } else if (this.b.hidden) {
        result = []
        for (; dashCount > 0; dashCount--) {
          result.push(dash, space)
        }

        let extra = (this.length - this.gap) % (dash + space)
        result.push(Math.min(dash, extra))
        result.push('100%')
      }

      return result.join(' ')
    }
  },
  watch: {
    a(newA, oldA) {
      if (newA.hidden != oldA.hidden) {
        this.aDelay = newA.delay
      }
    },
    b(newB, oldB) {
      if (newB.hidden != oldB.hidden) {
        this.bDelay = newB.delay
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
      aHidden: a.hidden && !arrow,
      bHidden: b.hidden && !arrow,
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

.canAnimate .edge.aHidden.aDelay {
  animation: hideStart 0.45s ease 0.3s backwards;
}

.canAnimate .edge.bDelay {
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
