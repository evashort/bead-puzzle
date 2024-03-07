<script setup>
import Board from './Board.vue'
import Goal from './Goal.vue'
import Holes from './Holes.vue'
import Permute from '../Permute.js'
import SimpleGraph from '../SimpleGraph.js'
</script>

<script>
export default {
  data() {
    return {
      beads: 0,
      won: false,
      history: [],
      tail: null,
      showTail: false,
      showCross: false,
      focusIsClick: false,
      clickingButton: false,
      spinButtonClicked: false,
      smallSpinButtonClicked: false,

      oldHole: 0,
      reversed: false,
      hasWon: false,
    }
  },
  props: {
    graphId: String,
    state: { beads: Number, history: Array },
    initialTail: Number,
    autofocus: Boolean,
    curvedPaths: Boolean,
    canAnimate: Boolean,
  },
  emits: ['update:won', 'update:state', 'update:tail', 'nextLevel'],
  computed: {
    graph() {
      return SimpleGraph.fromString(this.graphId)
    },
    size() {
      return SimpleGraph.bytesToNodeCount(this.graph)
    },
    hole() {
      return this.history[this.history.length - 1]
    },
    loopEnd() {
      return this.altHistory.length - 1
    },
    loopStart() {
      return Math.max(
        0,
        this.history.lastIndexOf(
          this.altHistory[this.altHistory.length - 1],
          -2,
        )
      )
    },
    deadEnd() {
      let edges = 0
      for (let _ of SimpleGraph.nodeEdges(this.graph, this.hole)) {
        edges += 1
        if (edges > 1) {
          return false
        }
      }

      return true
    },
    reversing() {
      return this.history.length >= 2 &&
        this.tail == this.history[this.history.length - 2]
    },
    nodeXs() {
      let xs = new Float64Array(this.size)
      for (let i = 0; i < this.size; i++) {
        xs[i] = 100 * Math.sin(2 * Math.PI * i / this.size)
      }

      return xs
    },
    nodeYs() {
      let ys = new Float64Array(this.size)
      for (let i = 0; i < this.size; i++) {
        ys[i] = -100 * Math.cos(2 * Math.PI * i / this.size)
      }

      return ys
    },
    crossRadius() {
      return 18
    },
    crossPath() {
      let d = this.crossRadius * Math.sqrt(0.5)
      return `M ${-d} ${-d} L ${d} ${d} M ${d} ${-d} L ${-d} ${d}`
    },
    clickRadius() {
      return 42
    },
    spinButtonY() {
      return -15
    },
    smallClickRadius() {
      return 20
    },
    smallSpinButtonY() {
      return this.clickRadius - this.smallClickRadius - this.spinButtonY
    },
    spinPath() {
      return this.getSpinPath(10, 11)
    },
    smallSpinPath() {
      return this.getSpinPath(7, 9)
    },
    altHistory() {
      return this.extra.length ? this.history.concat(this.extra) : this.history
    },
    extra() {
      // extrapolate history to the future if there's no choice of moves
      if (this.history.length <= 1) {
        return this.showTail ? [this.tail] : []
      }

      let hasForwardTail =
        this.showTail && this.tail != this.history[this.history.length - 2]
      if (
        this.history[0] == this.history[this.history.length - 1] &&
          (this.tail == this.history[1] || !hasForwardTail)
      ) {
        return []
      }

      let last = this.history[this.history.length - 1]
      let next = hasForwardTail ? this.tail :
        this.getOnlyPath(this.history[this.history.length - 2], last)
      let historySet = new Set(this.history)
      let extra = []
      while (next >= 0) {
        extra.push(next)
        if (historySet.has(next)) {
          break
        }

        next = this.getOnlyPath(last, next)
        last = extra[extra.length - 1]
      }

      return extra
    },
    canSpin() {
      return this.altHistory[this.altHistory.length - 1] ==
        this.history[this.loopStart]
    },
    clockwise() {
      let minA = Infinity, minB = Infinity
      let clockwise = false
      for (let i = this.loopStart; i < this.loopEnd; i++) {
        let node1 = this.altHistory[i], node2 = this.altHistory[i + 1]
        let y1 = this.getHeightRank(node1)
        let y2 = this.getHeightRank(node2)
        let minY = Math.min(y1, y2)
        let maxY = Math.max(y1, y2)
        if (minY < minA || (minY == minA && maxY < minB)) {
          minA = minY
          minB = maxY
          let x1 = this.getXRank(node1)
          let x2 = this.getXRank(node2)
          if (y1 < y2) {
            let node0 = this.altHistory[
              i <= this.loopStart ? this.loopEnd - 1 : i - 1
            ]
            let y0 = this.getHeightRank(node0)
            if (y0 == y2) {
              let x0 = this.getXRank(node0)
              clockwise = x0 < x2
            } else {
              clockwise = x1 < x2
            }
          } else {
            let node3 = this.altHistory[
              i >= this.loopEnd - 1 ? this.loopStart + 1 : i + 2
            ]
            let y3 = this.getHeightRank(node3)
            if (y3 == y1) {
              let x3 = this.getXRank(node3)
              clockwise = x1 < x3
            } else {
              clockwise = x1 < x2
            }
          }
        }
      }

      return clockwise
    },
  },
  methods: {
    getSpinPath(r, w) {
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
    getHeightRank(node) {
      return Math.abs((node + this.size/2) % this.size - this.size/2)
    },
    getOnlyPath(a, b) {
      let result = -1
      for (let c of SimpleGraph.nodeEdges(this.graph, b)) {
        if (c == a) { continue }
        if (result >= 0) { return -1 }
        result = c
      }

      return result
    },
    getXRank(node) {
      let a = (node + this.size/2) % this.size - this.size/2 // top half
      let b = this.size/2 - node // bottom half
      return Math.abs(a) < Math.abs(b) ? a : b
    },
    goForward() {
      if (this.ensureTail()) {
        if (this.canSpin && !this.won) {
          // continue going around the loop with the tail hidden
          this.showTail = this.won
          this.goForwardHelp()
        }
      } else {
        this.goForwardHelp()
        if (!this.reversed && this.reversing) {
          this.showTail = false // dead end
        }
      }
    },
    goForwardHelp() {
      this.beads = Permute.swap(this.beads, this.hole, this.tail)
      this.oldHole = this.hole
      this.reversed = false
      if (this.reversing) {
        this.history.pop()
        if (this.history[0] == this.oldHole) {
          // reverse the loop
          this.history.reverse()
          this.history.push(this.history[0])
        } else {
          // not a loop
          this.reversed = true
          if (this.history.length >= 2) {
            this.tail = this.history[this.history.length - 2] // keep going back
          } else {
            this.tail = this.oldHole
          }

          return
        }
      } else {
        this.history.push(this.tail)
      }

      // remove before loop
      for (let offset = this.history.length - 4; offset >= 0; offset--) {
        if (this.history[offset] == this.hole) {
          this.history = this.history.slice(offset)
          break
        }
      }

      this.tail = this.getNextTail(this.history)
    },
    getNextTail(history) {
      // first choice: continue the loop
      let end = history.length - 1
      let hole = history[end]
      if (history[0] == hole && end >= 3) {
        return history[1]
      }

      // second choice: keep going as straight as possible
      let oldHole = history[end - 1]
      return SimpleGraph.oppositeEdge(this.graph, oldHole, hole)
    },
    goBack() {
      if (this.history.length >= 2) {
        let newHole = this.history[this.history.length - 2]
        // always show tail when undoing win because winning hides tail.
        //
        // tutorial levels have dead ends which cause the tail to be hidden
        // even when using the keyboard. it's confusing if going back
        // doesn't cause the tail to be shown again.
        this.showTail = this.showTail || this.won || this.deadEnd

        this.oldHole = this.hole
        this.reversed = true
        this.tail = this.hole
        this.beads = Permute.swap(this.beads, newHole, this.tail)
        this.history.pop()
        if (this.history[0] == this.tail) {
          // ensure the entire loop is represented
          this.history.unshift(this.hole)
        }
      }
    },
    selectLeft() {
      if (this.ensureTail()) {
        return
      }

      // iterate counterclockwise and choose the first edge
      for (let i = this.size - 1; i >= 0; i--) {
        let newTail = (this.tail + i) % this.size
        if (SimpleGraph.hasEdge(this.graph, this.hole, newTail)) {
          this.tail = newTail
          return
        }
      }
    },
    selectRight() {
      if (this.ensureTail()) {
        return
      }

      // iterate counterclockwise and choose the first edge
      for (let i = 1; i <= this.size; i++) {
        let newTail = (this.tail + i) % this.size
        if (SimpleGraph.hasEdge(this.graph, this.hole, newTail)) {
          this.tail = newTail
          return
        }
      }
    },
    ensureTail() {
      if (!this.showTail) {
        if (this.history.length <= 1 || !this.deadEnd) {
          this.showTail = true
        }

        this.resetButtons()
        return true
      }

      return false
    },
    onPointerDown(event) {
      this.focusIsClick = true
      if (event.button != 0) {
        return
      }

      let target = this.getClickTarget(event.offsetX, event.offsetY)
      this.resetButtons()
      this.clickingButton = target != null
      if (target != null && target >= 0) {
        if (target == this.hole) {
          if (this.history.length >= 2) {
            this.goBack()
          } else {
            this.showCross = true
          }
        } else if (SimpleGraph.hasEdge(this.graph, target, this.hole)) {
          this.tail = target
          this.goForwardHelp()
        } else {
          this.showCross = true
        }

        this.showTail = false
      } else if (target == -2) {
        if (this.history[0] == this.hole) {
          this.tail = this.history[1]
        } else {
          this.tail = this.getOnlyPath(
            this.history[this.history.length - 2],
            this.hole,
          )
        }

        this.goForwardHelp()
        this.showTail = false
        this.spinButtonClicked = true
      } else if (target == -3) {
        this.goBack()
        this.showTail = false
        this.smallSpinButtonClicked = true
      }
    },
    clicked(event) {
      this.focusIsClick = false
      if (event.button == 0) {
        this.clickingButton = false
        if (this.canAnimate) {
          this.resetButtons()
        }
      }
    },
    getClickTarget(offsetX, offsetY) {
      let gameView = document.getElementById('game-view')
      let clientSize = Math.min(gameView.clientWidth, gameView.clientHeight)
      let x = (offsetX - 0.5 * gameView.clientWidth) * 286 / clientSize
      let y = (offsetY - 0.5 * gameView.clientHeight) * 286 / clientSize
      for (let i = 0; i < this.size; i++) {
        let dx = this.nodeXs[i] - x
        let dy = this.nodeYs[i] - y
        if (dx * dx + dy * dy < this.clickRadius * this.clickRadius) {
          return i
        }
      }

      if (this.canSpin) {
        let dx = 0 - x
        let dy = this.smallSpinButtonY - y
        if (
          dx * dx + dy * dy < this.smallClickRadius * this.smallClickRadius
        ) {
          return -3
        }

        dx = 0 - x
        dy = this.spinButtonY - y
        if (dx * dx + dy * dy < this.clickRadius * this.clickRadius) {
          return -2
        }
      }

      return null
    },
    nextLevel(event) {
      if (this.won || this.hasWon) {
        event.stopPropagation()
        event.preventDefault()
        this.$emit('nextLevel')
      }
    },
    buttonClicked() {
      if (!this.ensureTail()) {
        this.showTail = false
      }
    },
    onFocus(event) {
      if (!this.focusIsClick) {
        event.target.scrollIntoView(false)
      }

      this.focusIsClick = false
      if (!this.clickingButton) {
        this.ensureTail()
      }
    },
    onBlur() {
      this.focusIsClick = false
      this.showTail = false
      this.resetButtons()
    },
    resetButtons() {
      this.clickingButton = false
      this.showCross = false
      this.spinButtonClicked = false
      this.smallSpinButtonClicked = false
    },
  },
  watch: {
    state: {
      handler(newState, oldState) {
        this.won = false
        this.hasWon = false
        let gameView = document.getElementById('game-view')
        this.showTail = gameView?.parentNode?.matches(':focus-within') ?? false
        this.beads = newState.beads
        this.history = [...newState.history]
        this.oldHole = this.hole
        this.tail = this.getNextTail(this.history)
      },
      immediate: true,
    },
    graphId(newGraphId, oldGraphId) {
      this.won = false
      this.hasWon = false
      let gameView = document.getElementById('game-view')
      this.showTail = gameView?.parentNode?.matches(':focus-within') ?? false
    },
    initialTail: {
      handler(newInitialTail, oldInitialTail) {
        if (newInitialTail != null) {
          this.tail = newInitialTail
        }
      },
      immediate: true,
    },
    beads(newBeads, oldBeads) {
      let newWon = this.beads == 0
      if (newWon != this.won) {
        if (newWon) {
          this.showTail = false
        } else {
          this.hasWon = true
        }

        this.won = newWon
        this.$emit('update:won', newWon)
      }

      this.$emit('update:state', { beads: this.beads, history: this.history })
    },
    tail(newTail, oldTail) {
      this.$emit('update:tail', newTail)
    },
  },
}
</script>

<template>
  <button
    :class="{game: true, canAnimate: canAnimate}"
    :autofocus="autofocus"
    @keydown.up.stop.prevent="goForward()"
    @keydown.down.stop.prevent="goBack()"
    @keydown.left.stop.prevent="selectLeft()"
    @keydown.right.stop.prevent="selectRight()"
    @keydown.w.stop.prevent="goForward()"
    @keydown.s.stop.prevent="goBack()"
    @keydown.a.stop.prevent="selectLeft()"
    @keydown.d.stop.prevent="selectRight()"
    @keydown.enter="nextLevel"
    @click="buttonClicked"
    @focus.native="onFocus"
    @blur.native="onBlur"
  >
    <svg id="game-view" viewBox="-143 -143 286 286" @pointerdown="onPointerDown" @click.stop.prevent="clicked" @pointerup="clicked">
      <defs>
        <image id="star" x="-6" y="-6" width="12" height="12" href="../assets/star.svg"/>
        <image id="star-small" x="-4" y="-4" width="8" height="8" href="../assets/star_small.svg"/>
        <image id="heart-bead" x="-6" y="-6" width="12" height="12" href="../assets/heart.svg"/>
        <image id="butterfly-bead" x="-6" y="-6" width="12" height="12" href="../assets/butterfly.svg"/>
        <image id="saturn-bead" x="-6" y="-6" width="12" height="12" href="../assets/saturn.svg"/>
        <image id="leaf-bead" x="-6" y="-6" width="12" height="12" href="../assets/leaf.svg"/>
        <image id="mushroom-bead" x="-6" y="-6" width="12" height="12" href="../assets/mushroom.svg"/>
        <image id="flower-bead" x="-6" y="-6" width="12" height="12" href="../assets/flower.svg"/>
        <image id="heart-outline" x="-4" y="-4" width="8" height="8" href="../assets/heart_outline.svg"/>
        <image id="butterfly-outline" x="-4" y="-4" width="8" height="8" href="../assets/butterfly_outline.svg"/>
        <image id="saturn-outline" x="-4" y="-4" width="8" height="8" href="../assets/saturn_outline.svg"/>
        <image id="leaf-outline" x="-4" y="-4" width="8" height="8" href="../assets/leaf_outline.svg"/>
        <image id="mushroom-outline" x="-4" y="-4" width="8" height="8" href="../assets/mushroom_outline.svg"/>
        <image id="flower-outline" x="-4" y="-4" width="8" height="8" href="../assets/flower_outline.svg"/>
        <path
          id="head-path"
          :d="`M ${-12*Math.sqrt(1.5)} -12 L 0 0 L ${-12*Math.sqrt(1.5)} 12`"
          stroke-linecap="round"
          stroke-linejoin="round"
          fill="none"
        />
        <use
          id="head-stroke"
          href="#head-path"
          stroke="var(--color-text)"
          stroke-width="4"
        />
        <use
          id="head-shadow"
          href="#head-path"
          stroke="var(--color-background)"
          stroke-width="12"
        />
      </defs>
      <rect class="active-indicator"/>
      <rect class="active-indicator outline"/>
      <Holes
        :size="size"
        :beads="beads"
        :radius="100"
        :clickRadius="clickRadius"
        :smallClickRadius="smallClickRadius"
        :buttonY="spinButtonY"
        :smallButtonY="smallSpinButtonY"
      />
      <Board
        :key="graphId"
        :graphId="graphId"
        :beads="beads"
        :history="history"
        :tail="showTail ? tail : -1"
        :altHistory="altHistory"
        :loopStart="loopStart"
        :hasWon="won || hasWon"
        :controlLength="curvedPaths ? 30 : 0"
        :gap="curvedPaths ? 28 : 36"
        :radius="100"
        :holeRadius="clickRadius"
      />
      <Goal
        v-for="i in size - 1"
        :size="size"
        :bead="i"
        :radius="100"
      />
      <g
        :transform="`translate(${nodeXs[hole] ?? 0}, ${nodeYs[hole] ?? 0})`"
        :class="{crossGroup: true, ghost: !showCross}"
        :visibility="showCross ? 'initial' : 'hidden'"
      >
        <path :d="crossPath" class="cross shadow"/>
        <path :d="crossPath" class="cross"/>
      </g>
      <template v-if="canSpin">
        <g
          :style="{transform: `translate(0,${spinButtonY}px) scale(${clockwise ? 1 : -1},1)`}"
        >
          <g :class="{spinGroup: true, clicked: spinButtonClicked, ghost: !spinButtonClicked}">
            <path :d="spinPath" class="spinIcon shadow"/>
            <path :d="spinPath" class="spinIcon"/>
          </g>
        </g>
        <g
          :style="{transform: `translate(0,${smallSpinButtonY}px) scale(${clockwise ? -1 : 1},1)`}"
        >
          <g :class="{spinGroup: true, clicked: smallSpinButtonClicked, ghost: !smallSpinButtonClicked}">
            <path :d="smallSpinPath" class="spinIcon shadow"/>
            <path :d="smallSpinPath" class="spinIcon"/>
          </g>
        </g>
      </template>
    </svg>
  </button>
</template>

<style scoped>
button {
  background-color: inherit;
  border: none;
  font: inherit;
  padding: 0;
}
.game {
  aspect-ratio: 1;
  width: min(120%, 1.2 * max(100vh, 15rem), 42rem);
  margin-top: calc(0.5 * (max(100vh, 15rem) - min(120%, 1.2 * max(100vh, 15rem), 42rem)));
  margin-left: calc(0.5 * (100% - min(120%, 1.2 * max(100vh, 15rem), 42rem)));
  margin-bottom: min(0rem, 0.5 * (max(100vh, 15rem) - min(120%, 1.2 * max(100vh, 15rem), 42rem)));
  border: 2px solid #444444;
  border-radius: 2px;
  background-color: black;
}
button:focus-within .active-indicator {
  x: calc(-50% / 1.2 + 1px);
  y: calc(-50% / 1.2 + 1px);
  width: calc(100% / 1.2 - 2px);
  height: calc(100% / 1.2 - 2px);
  rx: 5px;
  ry: 5px;
  fill: none;
  stroke: #008cef; /* average of Firefox (#0060df) and Chrome/Edge (#00b8ff) */
  stroke-width: 1px;
  stroke-linecap: round;
  stroke-linejoin: round;
}
button:focus-within .active-indicator.outline {
  x: calc(-50% / 1.2 + 0.25px);
  y: calc(-50% / 1.2 + 0.25px);
  width: calc(100% / 1.2 - 0.5px);
  height: calc(100% / 1.2 - 0.5px);
  rx: 5.75px;
  ry: 5.75px;
  stroke: white;
  stroke-width: 0.5px;
}
.cross {
  stroke: var(--color-text);
  stroke-width: 4;
  stroke-linecap: round;
  stroke-linejoin: round;
  fill: none;
}
.cross.shadow {
  stroke: var(--color-background);
  stroke-width: 12;
}
.canAnimate .crossGroup.ghost {
  transition: visibility 0s 0.35s;
}
.spinIcon {
  stroke: var(--color-text);
  stroke-width: 3;
  stroke-linecap: round;
  stroke-linejoin: round;
  fill: none;
}
.spinIcon.shadow {
  stroke: var(--color-background);
  stroke-width: 9;
}
.spinGroup.clicked {
  transform: scale(calc(5/3));
}
.canAnimate .spinGroup.clicked {
  animation: revert 1s 0.35s forwards;
}
@keyframes revert {
  from { transform: scale(1); }
  to { transform: scale(1); }
}
.canAnimate .spinGroup.ghost {
  transition: transform 0s 0.05s;
}
@keyframes slide {
  from { offset-distance: 0%; }
  to { offset-distance: 100%; }
}
@keyframes slide2 {
  from { offset-distance: 0%; }
  to { offset-distance: 100%; }
}
</style>
