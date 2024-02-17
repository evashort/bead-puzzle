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
      oldBeads: [],

      // trophy state
      trophyAlternate: false,
      oldHole: 0,
      reversed: false,
      trophyPushed: false,
      trophyWasPushed: false,
      justWon: false,
      hasWon: false,
      trophyEnterPaused: false,
      trophyExitPaused: false,
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
  emits: ['update:won', 'update:state', 'update:tail'],
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
      return this.extra.length - 1
    },
    loopStart() {
      let sentinel = this.extra[this.loopEnd]
      for (let i = this.loopEnd - 2; i > 0; i--) {
        if (this.extra[i] == sentinel) {
          return i
        }
      }

      return 0
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
    edgePaths() {
      let controlLength = 30
      let edgePaths = {}
      for (let a = 0; a < this.size; a++) {
        edgePaths[[a, a].toString()] = `M ${this.nodeXs[a]} ${this.nodeYs[a]}`
      }

      for (let [baseA, baseB] of SimpleGraph.edges(this.graph)) {
        for (let [a, b] of [[baseA, baseB], [baseB, baseA]]) {
          let name = [a, b].toString()
          let x1 = this.nodeXs[a], y1 = this.nodeYs[a]
          let x2 = this.nodeXs[b], y2 = this.nodeYs[b]
          edgePaths[name] =
              `M ${x1} ${y1} C ${x1} ${y1}, ${x2} ${y2}, ${x2} ${y2}`
        }
      }

      if (!this.curvedPaths) {
        if (this.showTail && this.tail == this.extra[this.loopStart]) {
          let id = Permute.getValue(this.beads, this.tail) - 1
          let a = this.oldBeads[id]
          if (a != this.hole) {
            let b = this.tail
            let name = [a, b].toString()
            let c = this.hole
            let x1 = this.nodeXs[a], y1 = this.nodeYs[a]
            let x2 = this.nodeXs[b], y2 = this.nodeYs[b]
            let dx3 = this.nodeXs[c] - x2, dy3 = this.nodeYs[c] - y2
            let scale = 0.1 / Math.sqrt(dx3 * dx3 + dy3 * dy3)
            dx3 *= scale
            dy3 *= scale
            edgePaths[name] = 
                `M ${x1} ${y1} C ${x1} ${y1}, ${x2} ${y2}, ${x2} ${y2} l ${dx3} ${dy3}`
          }
        }

        return edgePaths
      }

      let endTangent = [0, 0]
      if (this.extra[this.loopStart] == this.extra[this.loopEnd]) {
        let a = this.extra[this.loopEnd - 1], b = this.extra[this.loopEnd]
        endTangent = this.getTangent(this.extra[this.loopStart + 1], b, a)
      }

      let lastTangent = [-endTangent[0], -endTangent[1]]
      for (let i = this.loopStart + 1; i <= this.loopEnd; i++) {
        let a = this.extra[i - 1], b = this.extra[i]
        let tangent = endTangent
        if (i < this.loopEnd) {
          tangent = this.getTangent(this.extra[i + 1], b, a)
        }

        let x1 = this.nodeXs[a], y1 = this.nodeYs[a]
        let x2 = this.nodeXs[b], y2 = this.nodeYs[b]
        let [dx1, dy1] = lastTangent, [dx2, dy2] = tangent
        let x0 = x1 + dx1 * controlLength, y0 = y1 + dy1 * controlLength
        let x3 = x2 + dx2 * controlLength, y3 = y2 + dy2 * controlLength
        edgePaths[[a, b].toString()] =
          `M ${x1} ${y1} C ${x0} ${y0}, ${x3} ${y3}, ${x2} ${y2}`
        edgePaths[[b, a].toString()] =
          `M ${x2} ${y2} C ${x3} ${y3}, ${x0} ${y0}, ${x1} ${y1}`
        lastTangent = [-tangent[0], -tangent[1]]
      }

      return edgePaths
    },
    terminatorRadius() {
      return this.curvedPaths ? 28 : 36
    },
    crossRadius() {
      return 18
    },
    crossPath() {
      let d = this.crossRadius * Math.sqrt(0.5)
      return `M ${-d} ${-d} L ${d} ${d} M ${d} ${-d} L ${-d} ${d}`
    },
    trophyExitStart() {
      if (this.reversed) {
        return this.oldHole
      } else if (this.history.length >= 2) {
        return this.history[this.history.length - 2]
      }

      return this.hole
    },
    trophyExitEnd() {
      if (
        this.history.length >= 3 && this.reversed &&
        this.oldHole == this.history[1]
      ) {
        return this.history[2]
      } else if (this.reversed) {
        return this.getIngress(this.oldHole, this.hole)
      } else if (this.history.length >= 3) {
        return this.history[this.history.length - 3]
      } else if (this.history.length >= 2) {
        let center = this.history[this.history.length - 2]
        return this.getIngress(center, this.hole)
      }

      return this.hole
    },
    trophyPushedStart() {
      return this.hole
    },
    trophyPushedEnd() {
      if (this.history.length >= 2) {
        if (this.hole == this.history[0]) {
          if (this.reversing) {
            return this.history[1]
          }

          return this.history[this.history.length - 2]
        } else if (this.reversing) {
          return this.getIngress(this.hole, this.history[this.history.length - 2])
        }

        return this.history[this.history.length - 2]
      }

      return this.getIngress(this.hole, this.tail)
    },
    trophyEnterStart() {
        if (this.reversed) {
        if (this.history.length >= 2) {
          return this.history[this.history.length - 2]
        } else {
          return this.getIngress(this.hole, this.oldHole)
        }
      } else if (this.history.length >= 2) {
        if (this.history[0] == this.hole) {
          return this.history[1]
        }

        let egress = this.history[this.history.length - 2]
        return this.getIngress(this.hole, egress)
      }

      return this.hole
    },
    trophyEnterEnd() {
      return this.hole
    },
    trophyExitPath() {
      let edge = [this.trophyExitStart, this.trophyExitEnd]
      let path = this.edgePaths[edge.toString()]
      return `path('${path}')`
    },
    trophyEnterPath() {
      let edge = this.trophyPushed ?
        [this.trophyPushedStart, this.trophyPushedEnd] :
        [this.trophyEnterStart, this.trophyEnterEnd]
      let path = this.edgePaths[edge.toString()]
      return `path('${path}')`
    },
    trophyExitClasses() {
      return {
        trophy: true,
        reverse: this.reversed,
        wasPushed: this.trophyWasPushed,
        unpaused: !this.trophyExitPaused,
      }
    },
    trophyEnterClasses() {
      return {
        trophy: true,
        enter: true,
        reverse: this.trophyPushed ? this.reversing : this.reversed,
        pushed: this.showTail,
        wasPushed: this.trophyPushed,
        unpaused: !this.trophyEnterPaused,
      }
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
    extra() {
      // extrapolate history to the future if there's no choice of moves
      if (this.history.length <= 1) {
        return this.showTail ? [this.hole, this.tail] : this.history
      }

      let loop = [...this.history]
      loop.pop()
      let seen = new Set(loop)
      let prev = loop[loop.length - 1]
      let node = this.hole
      while (node >= 0) {
        loop.push(node)
        if (seen.has(node)) {
          break
        }

        let next = this.getForcedTail(prev, node)
        prev = node
        node = next
      }

      if (
        loop.length == this.history.length &&
        !this.reversing &&
        this.showTail
      ) {
        loop.push(this.tail)
      }

      return loop
    },
    canSpin() {
      return this.history.length >= 2 && ( // must be 2 and not 3
        this.hole == this.history[0] || (
          this.extra[this.loopStart] == this.extra[this.loopEnd] && (
            this.extra.length > this.history.length + 1 ||
            this.getForcedTail(
              this.history[this.history.length - 2],
              this.hole,
            ) >= 0
          )
        )
      )
    },
    clockwise() {
      let minA = Infinity, minB = Infinity
      let clockwise = false
      for (let i = this.loopStart; i < this.loopEnd; i++) {
        let node1 = this.extra[i], node2 = this.extra[i + 1]
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
            let node0 = this.extra[
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
            let node3 = this.extra[
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
    getTangent(i, j, k) {
      let x1 = this.nodeXs[i], y1 = this.nodeYs[i]
      let x2 = this.nodeXs[j], y2 = this.nodeYs[j]
      let x3 = this.nodeXs[k], y3 = this.nodeYs[k]

      let dx1 = x2 - x1, dy1 = y2 - y1
      let len1 = Math.sqrt(dx1 * dx1 + dy1 * dy1)

      let dx2 = x3 - x2, dy2 = y3 - y2
      let len2 = Math.sqrt(dx2 * dx2 + dy2 * dy2)

      let dx3 = dx1 * len2 + dx2 * len1
      let dy3 = dy1 * len2 + dy2 * len1
      let len3 = Math.sqrt(dx3 * dx3 + dy3 * dy3)

      let factor = len3 > 0 ? 1 / len3 : 0
      return [dx3 * factor, dy3 * factor]
    },
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
    getForcedTail(prev, hole) {
      let tail = -1
      for (let i = 0; i < this.size; i++) {
        if (i != prev && SimpleGraph.hasEdge(this.graph, hole, i)) {
          if (tail != -1) { return -1 }
          tail = i
        }
      }

      return tail
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
      this.trophyWasPushed = this.showTail
      let id = Permute.getValue(this.beads, this.tail) - 1
      this.beads = Permute.swap(this.beads, this.hole, this.tail)
      this.oldBeads[id] = this.tail
      this.trophyAlternate = !this.trophyAlternate
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
      if (end >= 1) {
        let oldHole = history[end - 1]
        return this.getIngress(hole, oldHole)
      }

      // third choice: iterate clockwise and choose the first edge
      for (let tail of SimpleGraph.nodeEdges(this.graph, hole)) {
        if (tail > hole) {
          return tail
        }
      }

      for (let tail of SimpleGraph.nodeEdges(this.graph, hole)) {
        return tail
      }
    },
    goBack() {
      if (this.history.length >= 2) {
        let newHole = this.history[this.history.length - 2]
        this.trophyWasPushed = this.showTail &&
          this.history[this.history.length - 2] == this.tail
        // always show tail when undoing win because winning hides tail.
        //
        // tutorial levels have dead ends which cause the tail to be hidden
        // even when using the keyboard. it's confusing if going back
        // doesn't cause the tail to be shown again.
        this.showTail = this.showTail || this.won || this.deadEnd

        this.oldHole = this.hole
        this.reversed = true
        if (!this.reversing) {
          this.trophyPushed = false
        }

        this.tail = this.hole
        let id = Permute.getValue(this.beads, newHole) - 1
        this.beads = Permute.swap(this.beads, newHole, this.tail)
        this.oldBeads[id] = newHole
        this.trophyAlternate = !this.trophyAlternate
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
          this.tail = this.getForcedTail(
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
    getIngress(b, a) {
      let bestC = a
      let bestDistance = 0
      // among the c with the highest distance, choose the lowest one greater
      // than b or the lowest one if none are greater than b. we do it this way
      // so that when this function is used to choose the next tail after a
      // move, the player can press the right arrow key to cycle through all
      // the edges without wrapping around to the other side of b.
      for (let c of SimpleGraph.nodeEdges(this.graph, b)) {
        let distance = this.getAngleDistance(a, b, c)
        if (
          distance == bestDistance ? (c > b) > (bestC > b) :
          distance > bestDistance
        ) {
          bestC = c
          bestDistance = distance
        }
      }

      return bestC
    },
    getAngleDistance(a, b, c) {
      // distance from a to c around the perimeter of the circle without
      // passing b
      let aToC = (c - a + this.size) % this.size
      let aToB = (b - a + this.size) % this.size
      return aToB < aToC ? this.size - aToC : aToC
    },
  },
  watch: {
    state: {
      handler(newState, oldState) {
        this.won = false
        this.hasWon = false
        this.showTail = false
        this.beads = newState.beads
        this.oldBeads = new Array(this.size - 1)
        for (let i = 0; i < this.size - 1; i++) {
          this.oldBeads[i] = Permute.findValue(this.beads, i + 1)
        }

        this.history = [...newState.history]
        this.oldHole = this.hole
        this.tail = this.getNextTail(this.history)
      },
      immediate: true,
    },
    graphId(newGraphId, oldGraphId) {
      this.won = false
      this.hasWon = false
      this.showTail = false
    },
    initialTail: {
      handler(newInitialTail, oldInitialTail) {
        if (newInitialTail != null) {
          this.tail = newInitialTail
        }
      },
      immediate: true,
    },
    canAnimate(newCanAnimate, oldCanAnimate) {
      if (newCanAnimate) {
        this.trophyEnterPaused = true
        this.trophyExitPaused = true
      }
    },
    beads(newBeads, oldBeads) {
      let newWon = this.beads == 0
      this.justWon = false
      if (newWon != this.won) {
        if (newWon) {
          this.showTail = false
        } else {
          this.justWon = true
          this.hasWon = true
        }

        this.won = newWon
        this.$emit('update:won', newWon)
      }

      this.trophyPushed = this.showTail
      this.trophyEnterPaused = false
      this.trophyExitPaused = false
      this.$emit('update:state', { beads: this.beads, history: this.history })
    },
    tail(newTail, oldTail) {
      this.$emit('update:tail', newTail)
    },
    showTail(newShowTail, oldShowTail) {
      this.trophyEnterPaused = false
      if (newShowTail) {
        this.trophyPushed = true
      }
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
      <Holes
        :size="size"
        :beads="beads"
        :radius="100"
        :clickRadius="clickRadius"
        :smallClickRadius="smallClickRadius"
        :buttonY="spinButtonY"
        :smallButtonY="smallSpinButtonY"
      />
      <mask id="trophy-exit-mask">
        <circle
          :cx="nodeXs[trophyExitStart]"
          :cy="nodeYs[trophyExitStart]"
          :r="clickRadius"
          fill="white"
        >
        </circle>
      </mask>
      <mask id="trophy-enter-mask">
        <circle
          :cx="nodeXs[trophyEnterEnd]"
          :cy="nodeYs[trophyEnterEnd]"
          :r="clickRadius"
          fill="white"
        >
        </circle>
      </mask>
      <Board
        :key="graphId"
        :graphId="graphId"
        :beads="beads"
        :history="history"
        :tail="showTail ? tail : -1"
        :controlLength="30"
        :radius="100"
      />
      <Goal
        v-for="i in size - 1"
        :size="size"
        :bead="i"
        :radius="100"
      />
      <g v-if="hasWon || (won && trophyAlternate)" :mask="trophyAlternate ? 'url(#trophy-enter-mask)' : 'url(#trophy-exit-mask)'">
        <use :href="(trophyAlternate ? won : justWon) ? '#star' : '#star-small'" :class="trophyAlternate ? trophyEnterClasses : trophyExitClasses"
          :style="{ 'transform': 'scale(2.7) rotate(90deg)', 'offset-path': trophyAlternate ? trophyEnterPath : trophyExitPath}"
        />
      </g>
      <g v-if="hasWon || (won && !trophyAlternate)" :mask="trophyAlternate ? 'url(#trophy-exit-mask)' : 'url(#trophy-enter-mask)'">
        <use :href="(trophyAlternate ? justWon : won) ? '#star' : '#star-small'" :class="trophyAlternate ? trophyExitClasses : trophyEnterClasses"
          :style="{ 'transform': 'scale(2.7) rotate(90deg)', 'offset-path': trophyAlternate ? trophyExitPath : trophyEnterPath}"
        />
      </g>
      <g
        :transform="`translate(${nodeXs[hole]}, ${nodeYs[hole]})`"
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
.trophy {
  offset-rotate: auto;
  offset-distance: 100%;
}
.canAnimate .trophy.unpaused {
  animation: slide 0.75s ease forwards;
}
.canAnimate .trophy.wasPushed.unpaused {
  animation: wasPushed 0.75s ease forwards;
}
@keyframes wasPushed {
  from { offset-distance: calc(100% * 0.2); }
  to { offset-distance: 100%; }
}
.canAnimate .trophy.enter.unpaused {
  animation: slide2 0.75s ease forwards;
}
.trophy.enter.wasPushed {
  offset-distance: 0%;
}
.canAnimate .trophy.enter.wasPushed.unpaused {
  animation: unpushed 0.5s ease forwards;
}
@keyframes unpushed {
  from { offset-distance: calc(100% * 0.2); }
  to { offset-distance: 0%; }
}
.trophy.reverse {
  offset-rotate: reverse;
}
@keyframes pushed {
  from { offset-distance: 0%; }
  to { offset-distance: calc(100% * 0.2); }
}
.trophy.enter.pushed {
  offset-distance: calc(100% * 0.2);
}
.canAnimate .trophy.enter.pushed.unpaused {
  animation: pushed calc(0.75s * (1 - 0.2)) ease forwards;
}
</style>
