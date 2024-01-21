<script setup>
import { HiddenEnd } from '../HiddenEnd'
</script>

<script>
export default {
  data() {
    return {
      oldPath: null,
      alternate: false,
      animate: false,
      reversed: false,
    }
  },
  props: {
    path: String,
    onPath: Boolean,
    hiddenEnd: HiddenEnd,
  },
  computed: {
    pathPattern() {
      // https://www.w3.org/TR/SVG11/paths.html#PathDataBNF
      // regex can't parse SVG path syntax properly because backtracking allows
      // "56" to be parsed as "5, 6", so we parse using a very simplified
      // approximation of the syntax which assumes that the path has no syntax
      // errors and that numbers are separated (e.g. "-5-6" won't occur).
      let number = '[-+0-9.eE]+'
      let arg = `(${number})`
      let wsp = '[ \\t\\r\\n]*'
      let sep = `[, \\t\\r\\n]+`
      let curve = [
        '^',
        'M',
        [arg, arg].join(sep),
        'C',
        [arg, arg, arg, arg, arg, arg].join(sep),
        '$|^',
        'M',
        [arg, arg].join(sep),
        'C',
        [arg, arg, arg, arg, arg, arg].join(sep),
        'l',
        [number, number].join(sep),
        '$',
      ].join(wsp)
      return new RegExp(curve)
    },
    orientedPath() {
      return this.orient(this.path)
    },
    orientedOldPath() {
      return this.orient(this.oldPath ?? this.path)
    },
    hidden() {
      return this.hiddenEnd == HiddenEnd.A ||
        this.hiddenEnd == HiddenEnd.B ||
        this.hiddenEnd == HiddenEnd.DelayA ||
        this.hiddenEnd == HiddenEnd.DelayB
    }
  },
  methods: {
    orient(path) {
      if (!this.reversed) {
        return path
      }

      let match = path.match(this.pathPattern)
      if (!match) {
        return path
      }

      let [, x1, y1, cx1, cy1, cx2, cy2, x2, y2] = match
      return `M${x2} ${y2}C${cx2} ${cy2},${cx1} ${cy1},${x1} ${y1}`
    }
  },
  watch: {
    path(newPath, oldPath) {
      this.oldPath = oldPath
      this.alternate = !this.alternate
    },
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
    :class="{ edge: true, onPath: onPath, alternate: alternate, hidden: hidden, animate: animate }"
    :d="orientedPath"
    :style="{ '--old-path': `path('${orientedOldPath}')`, '--gap': 28 }"
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

.edge.onPath {
  stroke-dasharray: none;
}

.edge.onPath.hidden {
  stroke-dasharray: 0 var(--gap) 100%;
}

.canAnimate .edge {
  animation: bend 0.5s;
}

.canAnimate .edge.alternate {
  animation: bend2 0.5s;
}

.canAnimate .edge.animate.hidden {
  animation: hideEnd 0.45s ease 0.3s backwards, bend 0.5s;
}

.canAnimate .edge.animate.hidden.alternate {
  animation: hideEnd 0.45s ease 0.3s backwards, bend2 0.5s;
}

.canAnimate .edge.animate.onPath {
  animation: revealEnd 0.45s ease 0.3s backwards, bend 0.5s;
}

.canAnimate .edge.animate.onPath.alternate {
  animation: revealEnd 0.45s ease 0.3s backwards, bend2 0.5s;
}

@keyframes bend {
  from {
    d: var(--old-path);
  }
}

@keyframes bend2 {
  from {
    d: var(--old-path);
  }
}

@keyframes hideEnd {
  from {
    stroke-dasharray: var(--gap) 0 100%;
  }
}

@keyframes revealEnd {
  from {
    stroke-dasharray: 0 var(--gap) 100%;
  }
  to {
    stroke-dasharray: var(--gap) 0 100%;
  }
}
</style>
