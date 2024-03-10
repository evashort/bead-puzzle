<script>
export default {
  props: {
    size: Number,
    altHistory: Array,
    loopStart: Number,
    buttonY: Number,
    smallButtonY: Number,
    buttonClicked: Boolean,
    smallButtonClicked: Boolean,
  },
  computed: {
    path() {
      return this.getPath(10, 11)
    },
    smallPath() {
      return this.getPath(7, 9)
    },
    clockwise() {
      let top = -Infinity
      let topIndex = 0
      let loopEnd = this.altHistory.length - 1
      for (let i = this.loopStart; i < loopEnd; i++) {
        let height = Math.abs(this.altHistory[i] - 0.5 * this.size)
        if (height > top) {
          top = height
          topIndex = i
        }
      }

      let prev = this.altHistory[
        topIndex > this.loopStart ? topIndex - 1 : loopEnd - 1
      ]
      let next = this.altHistory[
        topIndex < loopEnd ? topIndex + 1 : this.loopStart + 1
      ]
      return prev > next
    },
  },
  methods: {
    getPath(r, w) {
      let tailAngle = 160, headAngle = -30, sweep = 0, largeArc = 1
      let s = -1 + 2 * sweep
      let x1 = r * Math.sin(tailAngle * Math.PI / 180)
      let y1 = -r * Math.cos(tailAngle * Math.PI / 180)
      let u = Math.sin(headAngle * Math.PI / 180)
      let v = -Math.cos(headAngle * Math.PI / 180)
      let x2 = r * u, y2 = r * v
      let h = w * Math.sqrt(0.375)
      let neck = 4.5
      let nx = s * -neck * v, ny = s * neck * u
      let dx1 = s * (0.5 * w * u + h * v), dy1 = s * (0.5 * w * v - h * u)
      let dx2 = s * (-.5 * w * u + h * v), dy2 = s * (-.5 * w * v - h * u)
      return `M ${x1} ${y1} A ${r} ${r} 0 ${largeArc} ${sweep} ${x2} ${y2} l ${nx} ${ny} m ${dx1} ${dy1} L ${x2 + nx} ${y2 + ny} l ${dx2} ${dy2}`
    },
  },
}
</script>

<template>
  <g
    :style="{transform: `translate(0,${buttonY}px) scale(${clockwise ? 1 : -1},1)`}"
  >
    <g :class="{group: true, clicked: buttonClicked, ghost: !buttonClicked}">
      <path :d="path" class="icon shadow"/>
      <path :d="path" class="icon"/>
    </g>
  </g>
  <g
    :style="{transform: `translate(0,${smallButtonY}px) scale(${clockwise ? -1 : 1},1)`}"
  >
    <g :class="{group: true, clicked: smallButtonClicked, ghost: !smallButtonClicked}">
      <path :d="smallPath" class="icon shadow"/>
      <path :d="smallPath" class="icon"/>
    </g>
  </g>
</template>

<style scoped>
.icon {
  stroke: var(--color-text);
  stroke-width: 3;
  stroke-linecap: round;
  stroke-linejoin: round;
  fill: none;
  pointer-events: none;
}
.icon.shadow {
  stroke: var(--color-background);
  stroke-width: 9;
}
.group.clicked {
  transform: scale(calc(5/3));
}
.canAnimate .group.clicked {
  animation: revert 1s 0.35s forwards;
}
@keyframes revert {
  from { transform: scale(1); }
  to { transform: scale(1); }
}
.canAnimate .group.ghost {
  transition: transform 0s 0.05s;
}
</style>
