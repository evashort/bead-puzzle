<script setup>
import Board from './Board.vue'
import Cross from './Cross.vue'
import Goal from './Goal.vue'
import Holes from './Holes.vue'
import Permute from '../Permute.js'
import SimpleGraph from '../SimpleGraph.js'
import SpinButtons from './SpinButtons.vue'
</script>

<script>
export default {
  data() {
    return {
      beads: 0,
      history: [],
      tail: null,
      showTail: false,
      showCross: false,
      focusIsClick: false,
      clickingButton: false,
      spinButtonClicked: false,
      smallSpinButtonClicked: false,
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
    altHistory() {
      return this.extra.length ? this.history.concat(this.extra) : this.history
    },
    extra() {
      // extrapolate history to the future if there's no choice of moves
      if (this.history.length <= 1) {
        return this.showTail ? [this.tail] : []
      }

      let beforeHole = this.history[this.history.length - 2]
      let hasForwardTail = this.showTail && this.tail != beforeHole
      if (
        this.history[0] == this.history[this.history.length - 1] &&
          (this.tail == this.history[1] || !hasForwardTail)
      ) {
        return []
      }

      let last = this.history[this.history.length - 1]
      let next = hasForwardTail ? this.tail :
        SimpleGraph.onlyPath(this.graph, beforeHole, last)
      let historySet = new Set(this.history)
      let extra = []
      while (next >= 0) {
        extra.push(next)
        if (historySet.has(next)) {
          break
        }

        next = SimpleGraph.onlyPath(this.graph, last, next)
        last = extra[extra.length - 1]
      }

      return extra
    },
    canSpin() {
      return this.history.length >= 2 &&
        this.altHistory[this.altHistory.length - 1] ==
          this.history[this.loopStart]
    },
  },
  methods: {
    goForward() {
      if (this.ensureTail()) {
        if (this.canSpin && this.beads != 0) {
          // continue going around the loop with the tail hidden
          this.showTail = false
          this.goForwardHelp()
        }
      } else {
        let reversed = this.goForwardHelp()
        if (!reversed && this.reversing) {
          this.showTail = false // dead end
        }
      }
    },
    goForwardHelp() {
      this.beads = Permute.swap(this.beads, this.hole, this.tail)
      let oldHole = this.hole
      if (this.reversing) {
        this.history.pop()
        if (this.history[0] == oldHole) {
          // reverse the loop
          this.history.reverse()
          this.history.push(this.history[0])
        } else {
          // not a loop
          if (this.history.length >= 2) {
            this.tail = this.history[this.history.length - 2] // keep going back
          } else {
            this.tail = oldHole
          }

          return true
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
      return false
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
        this.showTail = this.showTail || this.beads == 0 || this.deadEnd

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

      this.resetButtons()
      this.clickingButton = false
    },
    onLeftButtonDown() {
      this.focusIsClick = true
      this.resetButtons()
      this.clickingButton = true
    },
    onButtonDown(target) {
      this.onLeftButtonDown()
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
    },
    onSpinButtonDown() {
      this.onLeftButtonDown()
      if (!this.canSpin) {
        this.clickingButton = false
        return
      }

      if (this.history[0] == this.hole) {
        this.tail = this.history[1]
      } else {
        this.tail = SimpleGraph.onlyPath(
          this.graph,
          this.history[this.history.length - 2],
          this.hole,
        )
      }

      this.goForwardHelp()
      this.showTail = false
      this.spinButtonClicked = true
    },
    onSmallSpinButtonDown() {
      this.onLeftButtonDown()
      if (!this.canSpin) {
        this.clickingButton = false
        return
      }

      this.goBack()
      this.showTail = false
      this.smallSpinButtonClicked = true
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
    nextLevel(event) {
      if (this.hasWon) {
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
        this.hasWon = false
        let gameView = document.getElementById('game-view')
        this.showTail = gameView?.parentNode?.matches(':focus-within') ?? false
        this.beads = newState.beads
        this.history = [...newState.history]
        this.tail = this.getNextTail(this.history)
      },
      immediate: true,
    },
    graphId(newGraphId, oldGraphId) {
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
      let oldWon = oldBeads == 0, newWon = newBeads == 0
      if (newWon != oldWon) {
        if (newWon) {
          this.showTail = false
          this.hasWon = true
        }

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
        @buttonDown="onButtonDown"
        @spinButtonDown="onSpinButtonDown"
        @smallSpinButtonDown="onSmallSpinButtonDown"
      />
      <Board
        :key="graphId"
        :graphId="graphId"
        :beads="beads"
        :altHistory="altHistory"
        :historyLength="history.length"
        :tail="showTail ? tail : -1"
        :loopStart="loopStart"
        :hasWon="hasWon"
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
      <Cross
        :size="size"
        :hole="hole"
        :shown="showCross"
        :radius="100"
      />
      <SpinButtons
        v-if="canSpin"
        :size="size"
        :altHistory="altHistory"
        :loopStart="loopStart"
        :buttonY="spinButtonY"
        :smallButtonY="smallSpinButtonY"
        :buttonClicked="spinButtonClicked"
        :smallButtonClicked="smallSpinButtonClicked"
      />
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
</style>
