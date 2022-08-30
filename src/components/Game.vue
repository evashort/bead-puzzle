<script setup>
import seedrandom from 'seedrandom'
</script>

<script>
export default {
  data() {
    return {
      beads: [],
      history: [],
      chosenTail: null,
      // if clickTarget is null, clicking is treated as false no matter its
      // actual value
      clicking: false,
      clickTarget: null,
      animations: new Uint8Array(0),
      oldBeads: [],
    }
  },
  props: {
    startingBeads: Array,
    edges: Array,
  },
  emits: ['update:beads'],
  computed: {
    size() {
      return this.startingBeads.length + 1
    },
    matrix() {
      let matrix = new Uint8Array(this.size * this.size)
      for (let [a, b] of this.edges) {
        matrix[a * this.size + b] = matrix[b * this.size + a] = 1
      }

      return matrix
    },
    hole() {
      return this.history[this.history.length - 2]
    },
    tail() {
      return this.history[this.history.length - 1]
    },
    loopEnd() {
      if (this.hole == this.tail) {
        return this.history.length - 2
      }

      if (!this.matrix[this.hole * this.size + this.tail]) {
        return this.history.length - 2 // forbidden path
      }

      if (this.history.length <= 2) {
        return this.history.length - 1
      }

      if (this.tail == this.history[this.history.length - 3]) {
        return this.history.length - 2 // going back
      }

      if (this.hole == this.history[0] && this.tail == this.history[1]) {
        return this.history.length - 2 // continuing loop
      }

      return this.history.length - 1
    },
    loopStart() {
      let sentinel = this.history[this.loopEnd]
      for (let i = this.loopEnd - 2; i > 0; i--) {
        if (this.history[i] == sentinel) {
          return i
        }
      }

      return 0
    },
    historyIndices() {
      let result = new Uint16Array(this.size * this.size)
      for (let i = this.loopStart; i < this.loopEnd; i++) {
        let a = this.history[i]
        let b = this.history[i + 1]
        result[a * this.size + b] = result[b * this.size + a] = i + 1
      }

      return result
    },
    nodeXs() {
      let xs = new Float64Array(this.size)
      for (let i = 0; i < this.size; i++) {
        // avoid vertical edges because of rendering bug for masked paths
        xs[i] = 100 * Math.sin(2 * Math.PI * i / this.size + 0.02)
      }

      return xs
    },
    nodeYs() {
      let ys = new Float64Array(this.size)
      for (let i = 0; i < this.size; i++) {
        ys[i] = -100 * Math.cos(2 * Math.PI * i / this.size + 0.02)
      }

      return ys
    },
    goalAngles() {
      return [
        [],
        [90],
        [80, 100],
        [80, 15, -15],
        [80, 170, 100, 190],
        [80, 15, 105, 255, -15],
        [80, 15, 165, 105, 195, -15],
        [80, 40, 170, 105, 255, 195, -40],
      ]
    },
    goalXs() {
      let xs = new Float64Array(this.size)
      let angles = this.goalAngles[this.size]
      for (let i = 0; i < this.size; i++) {
        xs[i] = this.nodeXs[i] + 30 * Math.sin(angles[i] * Math.PI / 180)
      }

      return xs
    },
    goalYs() {
      let ys = new Float64Array(this.size)
      let angles = this.goalAngles[this.size]
      for (let i = 0; i < this.size; i++) {
        ys[i] = this.nodeYs[i] - 30 * Math.cos(angles[i] * Math.PI / 180)
      }

      return ys
    },
    tangents() {
      let count = this.loopEnd + 1 - this.loopStart
      let xs = new Float64Array(count)
      let ys = new Float64Array(count)
      if (this.history[this.loopStart] == this.history[this.loopEnd]) {
        let [x, y] = this.getTangent(
          this.history[this.loopEnd - 1],
          this.history[this.loopStart],
          this.history[this.loopStart + 1],
        )
        xs[0] = xs[count - 1] = x
        ys[0] = ys[count - 1] = y
      }

      for (let i = this.loopStart + 1; i < this.loopEnd; i++) {
        let [x, y] = this.getTangent(
          this.history[i - 1],
          this.history[i],
          this.history[i + 1],
        )
        xs[i - this.loopStart] = x
        ys[i - this.loopStart] = y
      }

      return [xs, ys]
    },
    edgePaths() {
      let controlLength = 30
      let edgePaths = {}
      let [dxs, dys] = this.tangents
      let offset = this.loopStart
      for (let a = 0; a < this.size; a++) {
        for (let b = a; b < this.size; b++) {
          let name = [a, b].toString()
          let x1 = this.nodeXs[a], y1 = this.nodeYs[a]
          if (a == b) {
            edgePaths[name] = `M ${x1} ${y1}`
            continue
          }

          let backName = [b, a].toString()
          let x2 = this.nodeXs[b], y2 = this.nodeYs[b]
          let i = this.historyIndices[a * this.size + b]
          if (i <= 0) {
            edgePaths[name] =
              `M ${x1} ${y1} C ${x1} ${y1}, ${x2} ${y2}, ${x2} ${y2}`
            edgePaths[backName] =
              `M ${x2} ${y2} C ${x2} ${y2}, ${x1} ${y1}, ${x1} ${y1}`
            continue
          }

          let dx1 = dxs[i - offset - 1], dy1 = dys[i - offset - 1]
          let dx2 = -dxs[i - offset], dy2 = -dys[i - offset]
          if ((this.history[i - 1] < this.history[i]) != (a < b)) {
            [dx1, dy1, dx2, dy2] = [dx2, dy2, dx1, dy1]
          }

          let x0 = x1 + dx1 * controlLength, y0 = y1 + dy1 * controlLength
          let x3 = x2 + dx2 * controlLength, y3 = y2 + dy2 * controlLength
          edgePaths[name] =
            `M ${x1} ${y1} C ${x0} ${y0}, ${x3} ${y3}, ${x2} ${y2}`
          edgePaths[backName] =
            `M ${x2} ${y2} C ${x3} ${y3}, ${x0} ${y0}, ${x1} ${y1}`
        }
      }

      return edgePaths
    },
    edgeTruncated() {
      let startNode = this.history[this.loopStart]
      if (this.history[this.loopEnd] == startNode) {
        return false
      }

      let next = this.history.indexOf(startNode, this.loopStart + 1)
      return next >= 0 && next < this.loopEnd
    },
    headRadius() {
      return 12
    },
    headHeight() {
      return this.headRadius * Math.sqrt(1.5)
    },
    headPath() {
      let r = this.headRadius, hr = 0.5 * this.headHeight
      return `M ${hr} ${-r} L ${-hr} ${0} L ${hr} ${r}`
    },
    showHead() {
      return this.hole != this.tail &&
        this.matrix[this.hole * this.size + this.tail]
    },
    crossRadius() {
      return 18
    },
    crossPath() {
      let d = this.crossRadius * Math.sqrt(0.5)
      return `M ${-d} ${-d} L ${d} ${d} M ${d} ${-d} L ${-d} ${d}`
    },
    showCross() {
      return this.clickTarget != null && this.clicking && (
        this.clickTarget == -1 || (
          this.hole != this.tail &&
            !this.matrix[this.hole * this.size + this.tail]
        )
      )
    },
    arrowEdge() {
      let a = this.hole, b = this.tail
      if (
        this.clickTarget != null && this.clickTarget >= 0 && !this.clicking
      ) {
        b = a
        a = this.clickTarget
      } else if (a == b && this.history.length >= 3) {
        a = this.history[this.history.length - 3]
      }

      if (this.matrix[a * this.size + b]) {
        return [a, b]
      }

      return[a, a]
    },
    arrowPath() {
      return this.edgePaths[this.arrowEdge.toString()]
    },
    beadRadius() {
      return 10
    },
    beadHeight() {
      return this.beadRadius * Math.sqrt(3)
    },
    beadClasses() {
      return this.beads.map(
        function(node, id, beads) {
          return {
            bead: true,
            tail: node == this.tail && this.hole != this.tail &&
              this.matrix[this.hole * this.size + this.tail],
            onPath: this.historyIndices[
              node * this.size + this.oldBeads[id]
            ] > 0,
            animate: this.animations[id] > 0,
            alternate: this.animations[id] % 2,
            reverse: this.animations[id] >= 3,
            undo: this.oldBeads[id] == this.hole,
            loop: this.hole == this.history[0],
            moving: this.oldBeads[id] == this.hole ||
              this.oldBeads[id] == this.tail,
            ghost: this.clickTarget != null && !this.clicking,
          }
        },
        this,
      )
    },
    beadOffsetPaths() {
      return this.beads.map(
        function(node, id, beads) {
          let edge =
            this.historyIndices[node * this.size + this.oldBeads[id]] <= 0 &&
            node == this.tail &&
            this.matrix[this.hole * this.size + this.tail] ?
            [this.hole, this.tail] :
            [this.oldBeads[id], node]
          let path = this.edgePaths[edge.toString()]
          return `path('${path}')`
        },
        this,
      )
    },
    normalBeadScale() {
      return 1
    },
    activeBeadScale() {
      return 5/3
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
    forcedLoop() {
      if (this.history.length <= 2) {
        return []
      }

      let loop = [...this.history]
      loop.pop()
      loop.pop()
      let seen = new Set(loop)
      let prev = loop[loop.length - 1]
      let node = this.hole
      while (node >= 0 && !seen.has(node)) {
        loop.push(node)
        let next = this.getForcedTail(prev, node)
        prev = node
        node = next
      }

      if (node >= 0) {
        loop = loop.slice(loop.indexOf(node))
        loop.push(node)
        return loop
      } else {
        return []
      }
    },
    clockwise() {
      let minA = Infinity, minB = Infinity
      let clockwise = false
      for (let i = 0; i < this.forcedLoop.length - 1; i++) {
        let node1 = this.forcedLoop[i], node2 = this.forcedLoop[i + 1]
        let y1 = this.getHeightRank(node1)
        let y2 = this.getHeightRank(node2)
        let minY = Math.min(y1, y2)
        let maxY = Math.max(y1, y2)
        if (minY < minA || (minY == minA && maxY < minB)) {
          minA = minY
          minB = maxY
          let x1 = this.getXRank(node1)
          let x2 = this.getXRank(node2)
          if (x1 == x2) {
            if (y1 < y2) {
              let node0 = this.forcedLoop[
                i <= 0 ? this.forcedLoop.length - 2 : i - 1
              ]
              let x0 = this.getXRank(node0)
              clockwise = x0 < x1
            } else {
              let node3 = this.forcedLoop[
                i >= this.forcedLoop.length - 2 ? 1 : i + 2
              ]
              let x3 = this.getXRank(node3)
              clockwise = x2 < x3
            }
          } else {
            clockwise = x1 < x2
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
      let start = hole * this.size
      let tail = -1
      for (let i = 0; i < this.size; i++) {
        if (i != prev && this.matrix[start + i]) {
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
        if (this.history.length >= 4 && this.hole == this.history[0]) {
          // continue going around the loop with the tail hidden
          this.goForwardHelp()
          this.history.push(this.tail)
        }
      } else if (this.matrix[this.hole * this.size + this.tail]) {
        this.goForwardHelp()
        this.history.push(this.getNextTail(this.history, this.chosenTail))
      }
    },
    goForwardHelp() {
      let id = this.beads.indexOf(this.tail)
      this.beads[id] = this.hole
      this.checkWin()
      this.animations[id] = 1 + this.animations[id] % 2
      this.oldBeads[id] = this.tail
      this.chosenTail = null
      this.clickTarget = null
      if (
        this.history.length >= 3 &&
        this.history[this.history.length - 3] == this.tail
      ) {
        let loop = this.history[0] == this.hole
        this.history.pop()
        this.history.pop()
        if (loop) {
          this.history.reverse()
          this.history.push(this.history[0])
        } else {
          this.animations[id] += 2
          this.chosenTail = this.hole // keep going back
        }
      }

      this.history = this.removeBeforeLoop(this.history)
    },
    removeBeforeLoop(history) {
      let hole = history[history.length - 1]
      for (let offset = history.length - 4; offset >= 0; offset--) {
        if (history[offset] == hole) {
          return history.slice(offset)
        }
      }

      return history
    },
    getNextTail(history, chosenTail) {
      // first choice: restore chosen tail
      if (chosenTail != null) {
        return chosenTail
      }

      let end = history.length - 1
      if (end >= 1 && history[end - 1] == history[end]) {
        end--
      }

      // second choice: continue the loop
      let hole = history[end]
      if (history[0] == hole && end >= 3) {
        return history[1]
      }

      // third choice: new tail creates the smallest possible loop
      let oldHole = history[end - 1]
      for (let i = end - 2; i >= 0; i--) {
        let tail = history[i]
        if (
          tail != oldHole && // going back shouldn't be the default.
                             // happens when old hole is start of loop.
          this.matrix[hole * this.size + tail]
        ) { return tail }
      }

      // fourth choice: iterate clockwise and choose the first edge
      for (let i = 1; i < this.size; i++) {
        let tail = (hole + i) % this.size
        if (
          tail != oldHole && // going back shouldn't be the default
          this.matrix[hole * this.size + tail]
        ) { return tail }
      }

      // fifth choice: dead end
      return hole
    },
    goBack() {
      this.clickTarget = null
      if (this.history.length > 2) {
        let hideTail = false
        if (this.hole == this.tail) {
          // tutorial levels have dead ends which cause the tail to be hidden
          // even when using the keyboard. it's confusing if going back
          // doesn't cause the tail to be shown again.
          let edges = 0
          for (let i = 0; i < this.size; i++) {
            edges += this.matrix[this.hole * this.size + i]
            if (edges > 1) {
              hideTail = true // not a dead end, ok to hide tail
              break
            }
          }
        }

        this.history.pop()
        let id = this.beads.indexOf(this.hole)
        this.beads[id] = this.tail
        this.checkWin()
        this.animations[id] = 3 + this.animations[id] % 2
        this.oldBeads[id] = this.hole
        if (this.history[0] == this.tail) {
          // ensure the entire loop is represented
          this.history.unshift(this.hole)
        }

        this.chosenTail = this.tail
        if (hideTail) {
          this.history[this.history.length - 1] = this.hole
        }
      }
    },
    selectLeft() {
      if (this.ensureTail() && this.hole != this.tail) {
        return
      }

      // iterate counterclockwise and choose the first edge
      for (let i = this.size - 1; i >= 0; i--) {
        let newTail = (this.tail + i) % this.size
        if (this.matrix[this.hole * this.size + newTail]) {
          this.history[this.history.length - 1] = newTail
          this.chosenTail = newTail
          this.clickTarget = null
          return
        }
      }
    },
    selectRight() {
      if (this.ensureTail() && this.hole != this.tail) {
        return
      }

      // iterate counterclockwise and choose the first edge
      for (let i = 1; i <= this.size; i++) {
        let newTail = (this.tail + i) % this.size
        if (this.matrix[this.hole * this.size + newTail]) {
          this.history[this.history.length - 1] = newTail
          this.chosenTail = newTail
          this.clickTarget = null
          return
        }
      }
    },
    ensureTail() {
      if (this.hole == this.tail) {
        this.clickTarget = null
        this.history[this.history.length - 1] =
          this.getNextTail(this.history, this.chosenTail)

        return true
      }

      return false
    },
    onMouseDown(event) {
      if (event.button != 0) {
        return
      }

      this.clickTarget = this.getClickTarget(event.offsetX, event.offsetY)
      this.clicking = true
      if (this.clickTarget == this.hole && this.history.length <= 2) {
        this.clickTarget = -1
        this.history[this.history.length - 1] = this.hole
      } else if (this.clickTarget != null && this.clickTarget >= 0) {
        let newTail = this.clickTarget == this.hole ?
          this.history[this.history.length - 3] : this.clickTarget
        this.history[this.history.length - 1] = newTail
        if (this.matrix[this.size * this.hole + newTail]) {
          this.chosenTail = newTail
        }
      } else if (this.clickTarget == -2 || this.clickTarget == -3) {
        this.history[this.history.length - 1] = this.hole
      }
    },
    clicked(event) {
      if (event.button != 0) {
        return
      }

      this.clicking = false
      let newTarget = this.getClickTarget(event.offsetX, event.offsetY)
      if (newTarget == this.hole && this.clickTarget == -1) {
      } else if (newTarget != this.clickTarget) {
        this.clicking = true
      } else if (
        this.clickTarget == this.hole && this.history.length >= 3 &&
          this.history[this.history.length - 3] == this.tail
      ) {
        let oldTarget = this.hole
        this.goBack()
        this.clickTarget = oldTarget
        this.history[this.history.length - 1] = this.hole
      } else if (this.clickTarget != null && this.clickTarget == this.tail) {
        if (this.matrix[this.hole * this.size + this.tail]) {
          let oldTarget = this.hole
          this.goForwardHelp()
          this.clickTarget = oldTarget
          this.history.push(this.tail)
        } else {
          this.history[this.history.length - 1] = this.hole
        }
      } else if (this.clickTarget == -2 && this.forcedLoop.length) {
        if (this.history[0] == this.hole) {
          this.history[this.history.length - 1] = this.history[1]
        } else {
          this.history[this.history.length - 1] = this.getForcedTail(
            this.history[this.history.length - 3],
            this.hole,
          )
        }
        this.goForwardHelp()
        this.history.push(this.tail)
        this.clickTarget = -2
      } else if (this.clickTarget == -3 && this.forcedLoop.length) {
        this.goBack()
        this.history[this.history.length - 1] = this.hole
        this.clickTarget = -3
      }
    },
    getClickTarget(offsetX, offsetY) {
      let gameView = document.getElementById('game-view')
      let x = offsetX / gameView.clientWidth * 240 - 120
      let y = offsetY / gameView.clientHeight * 240 - 120
      for (let i = 0; i < this.size; i++) {
        let dx = this.nodeXs[i] - x
        let dy = this.nodeYs[i] - y
        if (dx * dx + dy * dy < this.clickRadius * this.clickRadius) {
          return i
        }
      }

      if (this.forcedLoop.length) {
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
        this.history[this.history.length - 1] = this.hole
      }
    },
    onFocus() {
      if (
        this.clickTarget != -2 && this.clickTarget != -1 &&
          this.clickTarget != -3
      ) {
        this.ensureTail()
      }
    },
    onBlur() {
      this.clickTarget = null
      this.history[this.history.length - 1] = this.hole
    },
    checkWin() {
      this.$emit('update:beads', [...this.beads])
    },
  },
  watch: {
    startingBeads: {
      handler(newStartingBeads, oldStartingBeads) {
        this.beads = [...newStartingBeads]
        this.oldBeads = [...newStartingBeads]
        this.animations = new Uint8Array(this.beads.length)
        let beadSet = new Set(this.beads)
        let hole = 0
        for (; beadSet.has(hole); hole++) { }

        this.history = [hole, hole]
        this.chosenTail = null
        this.clickTarget = null
        this.checkWin()
      },
      immediate: true,
    },
  },
}
</script>

<template>
  <button
    class="tabStop"
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
    <svg class="gameView" id="game-view" viewBox="-120 -120 240 240" @mousedown="onMouseDown" @click.stop.prevent="clicked">
      <defs>
        <path
          id="head-path"
          :d="headPath"
          :style="{ 'offset-path': `path('${arrowPath}')`, 'offset-distance': `${100 * 0.5 * headHeight / 160}%` }"
          fill="none"
          stroke="black"
          stroke-width="12"
          stroke-linecap="round"
          stroke-linejoin="round"
        />
        <path
          id="cross-path"
          :d="crossPath"
          :transform="`translate(${this.nodeXs[this.hole]}, ${this.nodeYs[this.hole]})`"
          fill="none"
          stroke="black"
          stroke-width="12"
          stroke-linecap="round"
          stroke-linejoin="round"
        />
        <radialGradient r="0.55" id="checked-1"> <stop offset="70%" stop-color="black"/> <stop offset="100%" stop-color="#b51d14"/> </radialGradient>
        <radialGradient r="0.55" id="checked-2"> <stop offset="75%" stop-color="black"/> <stop offset="100%" stop-color="#ddb310"/> </radialGradient>
        <radialGradient r="0.55" id="checked-3"> <stop offset="72%" stop-color="black"/> <stop offset="100%" stop-color="#00b25d"/> </radialGradient>
        <radialGradient r="0.55" id="checked-4"> <stop offset="75%" stop-color="black"/> <stop offset="100%" stop-color="#00beff"/> </radialGradient>
        <radialGradient r="0.55" id="checked-5"> <stop offset="70%" stop-color="black"/> <stop offset="100%" stop-color="#4053d3"/> </radialGradient>
        <radialGradient r="0.55" id="checked-6"> <stop offset="74%" stop-color="black"/> <stop offset="100%" stop-color="#fb49b0"/> </radialGradient>
      </defs>
      <circle
        v-for="node in size"
        :fill="node >= 2 && beads[node - 2] == node - 1 ? `url('#checked-${node - 1}')` : 'black'"
        :r="clickRadius"
        :cx="nodeXs[node - 1]"
        :cy="nodeYs[node - 1]"
        :class="{touchCircle: true, checked: node >= 2 && beads[node - 2] == node - 1}"
      />
      <circle
        fill="black"
        :r="clickRadius"
        :cx="0"
        :cy="spinButtonY"
        :class="{touchCircle: true}"
      />
      <circle
        fill="black"
        :r="smallClickRadius"
        :cx="0"
        :cy="smallSpinButtonY"
        :class="{touchCircle: true}"
      />
      <path
        :opacity="showHead ? 1 : 0"
        class="head"
        :d="headPath"
        :style="{ 'offset-path': `path('${arrowPath}')`, 'offset-distance': `${100 * 0.5 * headHeight / 160}%` }"
        :class="{ghost: clickTarget != null && !clicking}"
        fill="none"
      />
      <path
        :opacity="showCross ? 1 : 0"
        class="head"
        :d="crossPath"
        :transform="`translate(${this.nodeXs[this.hole]}, ${this.nodeYs[this.hole]})`"
        :class="{ghost: clickTarget != null && !clicking}"
        fill="none"
      />
      <mask id="cross-mask">
        <rect x="-130" y="-130" width="260" height="260" fill="white"></rect>
        <use
          href="#cross-path"
          :opacity="showCross ? 1 : 0"
          :class="{ghost: clickTarget != null && !clicking}"
        />
      </mask>
      <mask id="head-mask">
        <rect x="-130" y="-130" width="260" height="260" fill="white"></rect>
        <use
          href="#head-path"
          :opacity="showHead ? 1 : 0"
          :class="{ghost: clickTarget != null && !clicking}"
        />
        <use
          href="#cross-path"
          :opacity="showCross ? 1 : 0"
          :class="{ghost: clickTarget != null && !clicking}"
        />
      </mask>
      <mask id="truncate-mask">
        <rect x="-130" y="-130" width="260" height="260" fill="white"></rect>
        <circle
          :cx="nodeXs[history[0]]"
          :cy="nodeYs[history[0]]"
          :r="edgeTruncated ? 25 : 0"
          fill="black"
          :style="{'transition': 'r 0.5s'}">
        </circle>
        <use
          href="#head-path"
          :opacity="showHead ? 1 : 0"
          :class="{ghost: clickTarget != null && !clicking}"
        />
        <use
          href="#cross-path"
          :opacity="showCross ? 1 : 0"
          :class="{ghost: clickTarget != null && !clicking}"
        />
      </mask>
      <path
        v-for="edge of edges"
        :key="`${edge.toString()},${size}`"
        :class="{ edge: true, active: (x => x > 0 && x < this.history.length - 1)(historyIndices[edge[0] * size + edge[1]]), arrow: (edge[0] == hole && edge[1] == tail) || (edge[0] == tail && edge[1] == hole) }"
        :d="edgePaths[edge.toString()]"
        fill="none"
        v-bind:mask="(edge[0] == arrowEdge[0] && edge[1] == arrowEdge[1]) || (edge[0] == arrowEdge[1] && edge[1] == arrowEdge[0]) ? 'url(#cross-mask)' : (edge[0] == history[0] && edge[1] == history[1]) || (edge[0] == history[1] && edge[1] == history[0]) ? 'url(#truncate-mask)' : 'url(#head-mask)'"
      />
      <template v-if="forcedLoop.length">
        <g
          :style="{transform: `translate(0,${spinButtonY}px) scale(${clockwise ? 1 : -1},1) scale(${clicking && clickTarget == -2 ? activeBeadScale : normalBeadScale})`}"
          :class="{spinIconGhost: clickTarget == -2 && !clicking}"
        >
          <path :d="spinPath" class="spinIcon shadow"/>
          <path :d="spinPath" class="spinIcon"/>
        </g>
        <g
          :style="{transform: `translate(0,${smallSpinButtonY}px) scale(${clockwise ? -1 : 1},1) scale(${clicking && clickTarget == -3 ? activeBeadScale : normalBeadScale})`}"
          :class="{spinIconGhost: clickTarget == -3 && !clicking}"
        >
          <path :d="smallSpinPath" class="spinIcon shadow"/>
          <path :d="smallSpinPath" class="spinIcon"/>
        </g>
      </template>
      <image v-if="size > 1" x="-6" y="-6" width="12" height="12" :class="beadClasses[0]"
        href="../assets/heart.svg"
        :style="{ 'transform': `rotate(90deg) scale(2.7) scale(${tail == beads[0] && hole != tail ? activeBeadScale : normalBeadScale})`, 'offset-path': beadOffsetPaths[0] }"
      />
      <image v-if="size > 2" x="-6" y="-6" width="12" height="12" :class="beadClasses[1]"
        href="../assets/butterfly.svg"
        :style="{ 'transform': `rotate(90deg) scale(2.8) scale(${tail == beads[1] && hole != tail ? activeBeadScale : normalBeadScale})`, 'offset-path': beadOffsetPaths[1] }"
      />
      <image v-if="size > 3" x="-6" y="-6" width="12" height="12" :class="beadClasses[2]"
        href="../assets/saturn.svg"
        :style="{ 'transform': `rotate(90deg) scale(3.35) scale(${tail == beads[2] && hole != tail ? activeBeadScale : normalBeadScale})`, 'offset-path': beadOffsetPaths[2] }"
      />
      <image v-if="size > 4" x="-6" y="-6" width="12" height="12" :class="beadClasses[3]"
        href="../assets/leaf.svg"
        :style="{ 'transform': `rotate(90deg) scale(2.5) scale(${tail == beads[3] && hole != tail ? activeBeadScale : normalBeadScale})`, 'offset-path': beadOffsetPaths[3] }"
      />
      <image v-if="size > 5" x="-6" y="-6" width="12" height="12" :class="beadClasses[4]"
        href="../assets/mushroom.svg"
        :style="{ 'transform': `rotate(90deg) scale(2.6) scale(${tail == beads[4] && hole != tail ? activeBeadScale : normalBeadScale})`, 'offset-path': beadOffsetPaths[4] }"
      />
      <image v-if="size > 6" x="-6" y="-6" width="12" height="12" :class="beadClasses[5]"
        href="../assets/flower.svg"
        :style="{ 'transform': `rotate(90deg) scale(2.5) scale(${tail == beads[5] && hole != tail ? activeBeadScale : normalBeadScale})`, 'offset-path': beadOffsetPaths[5] }"
      />
      <g v-if="size > 1" :transform="`translate(${goalXs[1]},${goalYs[1]})`">
        <image x="-4" y="-4" width="8" height="8"
          href="../assets/heart_outline.svg"
          :style="{ 'transform': `scale(2.7)` }"
        />
      </g>
      <g v-if="size > 2" :transform="`translate(${goalXs[2]},${goalYs[2]})`">
        <image x="-4" y="-4" width="8" height="8"
          href="../assets/butterfly_outline.svg"
          :style="{ 'transform': 'scale(2.8)' }"
        />
      </g>
      <g v-if="size > 3" :transform="`translate(${goalXs[3]},${goalYs[3]})`">
        <image x="-4" y="-4" width="8" height="8"
          href="../assets/saturn_outline.svg"
          :style="{ 'transform': 'scale(3.35)' }"
        />
      </g>
      <g v-if="size > 4" :transform="`translate(${goalXs[4]},${goalYs[4]})`">
        <image x="-4" y="-4" width="8" height="8"
          href="../assets/leaf_outline.svg"
          :style="{ 'transform': 'scale(2.5)' }"
        />
      </g>
      <g v-if="size > 5" :transform="`translate(${goalXs[5]},${goalYs[5]})`">
        <image x="-4" y="-4" width="8" height="8"
          href="../assets/mushroom_outline.svg"
          :style="{ 'transform': 'scale(2.6)' }"
        />
      </g>
      <g v-if="size > 6" :transform="`translate(${goalXs[6]},${goalYs[6]})`">
        <image x="-4" y="-4" width="8" height="8"
          href="../assets/flower_outline.svg"
          :style="{ 'transform': 'scale(2.5)' }"
        />
      </g>
    </svg>
  </button>
</template>

<style scoped>
.tabStop {
  background-color: inherit;
  border: none;
  font: inherit;
  padding: 0;
}
.gameView {
  width: 40rem;
  height: 40rem;
}
.touchCircle {
  stroke: var(--color-text);
  stroke-width: 0.5;
  stroke-opacity: 0.25;
}
.touchCircle.checked {
  stroke-width: 0.75;
  stroke-opacity: 1;
}
.head {
  stroke: var(--color-text);
  stroke-width: 4;
  stroke-linecap: round;
  stroke-linejoin: round;
}
.ghost {
  transition: opacity 0s 0.35s;
}
.spinIcon {
  stroke: var(--color-text);
  stroke-width: 3;
  stroke-linecap: round;
  stroke-linejoin: round;
  fill: none;
}
.spinIcon.shadow {
  stroke: black;
  stroke-width: 9;
}
.spinIconGhost {
  transition: transform 0s 0.05s;
}
.edge {
  stroke: var(--color-text);
  stroke-width: 4;
  stroke-linecap: round;
  transition: d 0.5s;
  stroke-dasharray: 4 12;
}
.edge.arrow {
  stroke-dasharray: 8 8;
  stroke-dashoffset: 2;
}
.edge.active {
  stroke-dasharray: none;
}
.outline {
  stroke-width: 3;
  stroke: var(--color-text);
}
/*
tail onPath undo loop reverse offset-rotate
0    0                        -90deg
0    1                0       auto
0    1                1       reverse
1    0      0                 reverse
1           1    0    0       auto
1           1    0    1       reverse
1           1    1            reverse
1    1      0                 auto
*/
.bead {
  offset-distance: 100%;
  offset-rotate: -90deg;
}
.bead.onPath {
  offset-rotate: auto;
}
.bead.onPath.reverse {
  offset-rotate: reverse;
}
.bead.animate {
  animation: slide 0.75s ease forwards;
}
@keyframes slide {
  from { offset-distance: 0%; }
  to { offset-distance: 100%; }
}
.bead.alternate {
  animation-name: slide2
}
@keyframes slide2 {
  from { offset-distance: 0%; }
  to { offset-distance: 100%; }
}
.bead.tail {
  offset-rotate: reverse;
}
.bead.tail.onPath {
  offset-rotate: auto;
}
.bead.tail.undo {
  offset-rotate: auto;
}
.bead.tail.undo.reverse {
  offset-rotate: reverse;
}
.bead.tail.undo.loop {
  offset-rotate: reverse;
}
.bead.ghost {
  transition: transform 0s 0.35s;
}
.bead.ghost.moving {
  /* this timing function approximates a delay, since actual delay caused
   * beads to stay BIG sometimes due to browser bug
   */
  transition: transform 0.06s cubic-bezier(1,0,1,0);
}
</style>
