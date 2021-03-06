<script>
export default {
  data() {
    let beadSet = new Set(this.startingBeads)
    let hole = 0
    for (; beadSet.has(hole); hole++) { }

    let size = this.startingBeads.length + 1
    let holeRow = new Uint8Array(size)
    for (let [a, b] of this.edges) {
      if (a == hole) {
        holeRow[b] = 1
      } else if (b == hole) {
        holeRow[a] = 1
      }
    }

    // iterate clockwise and choose the first edge
    for (let i = 1; i < size; i++) {
      let tail = (hole + i) % size
      if (holeRow[tail]) {
        return {
          beads: [...this.startingBeads],
          history: [hole, tail],
          animations: new Uint8Array(this.startingBeads.length),
          oldBeads: [...this.startingBeads],
          oldFirstEdge: [hole, tail],
          showTail: true,
        }
      }
    }
  },
  props: {
    startingBeads: Array,
    edges: Array
  },
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
      if (this.history.length <= 2) {
        return this.history.length - 1 - !this.showTail
      }

      if (this.tail == this.history[this.history.length - 3]) {
        return this.history.length - 2 // going back
      }

      if (this.hole == this.history[0] && this.tail == this.history[1]) {
        return this.history.length - 2 // continuing loop
      }

      return this.history.length - 1 - !this.showTail
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
      for (let edge of this.edges) {
        let [a, b] = edge
        let backEdge = edge.slice().reverse()
        let x1 = this.nodeXs[a], y1 = this.nodeYs[a]
        let x2 = this.nodeXs[b], y2 = this.nodeYs[b]
        let i = this.historyIndices[a * this.size + b]
        if (i <= 0) {
          edgePaths[edge.toString()] =
            `M ${x1} ${y1} C ${x1} ${y1}, ${x2} ${y2}, ${x2} ${y2}`
          edgePaths[backEdge.toString()] =
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
        edgePaths[edge.toString()] =
          `M ${x1} ${y1} C ${x0} ${y0}, ${x3} ${y3}, ${x2} ${y2}`
        edgePaths[backEdge.toString()] =
          `M ${x2} ${y2} C ${x3} ${y3}, ${x0} ${y0}, ${x1} ${y1}`
      }

      for (let node = 0; node < this.size; node++) {
        edgePaths[[node, node].toString()] =
          `M ${this.nodeXs[node]} ${this.nodeYs[node]}`
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
      return 10
    },
    headHeight() {
      return this.headRadius * Math.sqrt(1.5)
    },
    headPath() {
      let r = this.headRadius, hr = 0.5 * this.headHeight
      return `M ${hr} ${-r} L ${-hr} ${0} L ${hr} ${r}`
    },
    arrowPath() {
      return this.edgePaths[[this.hole, this.tail].toString()]
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
            tail: node == this.tail && this.showTail,
            onPath: this.historyIndices[
              node * this.size + this.oldBeads[id]
            ] > 0,
            animate: this.animations[id] > 0,
            alternate: this.animations[id] % 2,
            reverse: this.animations[id] >= 3,
            undo: this.oldBeads[id] == this.hole,
            loop: this.hole == this.history[0],
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
            node == this.tail ?
            [this.hole, this.tail] :
            [this.oldBeads[id], node]
          let path = this.edgePaths[edge.toString()]
          return `path('${path}')`
        },
        this,
      )
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
    goForward() {
      if (
        !this.showTail && (
          this.history[0] != this.hole || this.history[1] != this.tail ||
          this.history.length <= 2
        )
      ) {
        this.showTail = true
        return
      }

      this.goForwardHelp()
    },
    goForwardHelp() {
      this.oldFirstEdge = this.history.slice(0, 2)

      let id = this.beads.indexOf(this.tail)
      this.beads[id] = this.hole
      this.animations[id] = 1 + this.animations[id] % 2
      this.oldBeads[id] = this.tail

      // first choice: go back instead
      if (
        this.history.length >= 3 &&
        this.history[this.history.length - 3] == this.tail
      ) {
        this.history.pop()
        if (this.history.length <= 2) {
          // reached beginning, time to go forward again
          this.history.pop()
          this.animations[id] += 2
        } else if (this.history[0] == this.tail) {
          // reverse the loop
          this.history.pop()
          this.history.reverse()
          this.history.push(this.history[0])
          this.history.push(this.history[1])
          return
        } else {
          // default is to continue going back
          this.history[this.history.length - 1] =
            this.history[this.history.length - 3]
          this.animations[id] += 2
          return
        }
      }

      // second choice: new tail continues the most recent loop
      for (let offset = this.history.length - 4; offset >= 0; offset--) {
        if (this.history[offset] == this.tail) {
          // remove history before the loop
          this.history = this.history.slice(offset)
          this.history.push(this.history[1])
          return
        }
      }

      // third choice: new tail creates the smallest possible loop
      for (let i = this.history.length - 3; i >= 0; i--) {
        let newTail = this.history[i]
        if (
          newTail != this.hole && // going back shouldn't be the default.
                                  // happens when old hole is start of loop.
          this.matrix[this.tail * this.size + newTail]
        ) {
          this.history.push(newTail)
          return
        }
      }

      // fourth choice: iterate clockwise and choose the first edge
      for (let i = 1; i < this.size; i++) {
        let newTail = (this.tail + i) % this.size
        if (
          newTail != this.hole && // going back shouldn't be the default
          this.matrix[this.tail * this.size + newTail]
        ) {
          this.history.push(newTail)
          return
        }
      }
    },
    goBack() {
      this.oldFirstEdge = this.history.slice(0, 2)

      if (this.history.length > 2) {
        this.history.pop()
        let id = this.beads.indexOf(this.hole)
        this.beads[id] = this.tail
        this.animations[id] = 3 + this.animations[id] % 2
        this.oldBeads[id] = this.hole
        if (this.history[0] == this.tail) {
          // ensure the entire loop is represented
          this.history.unshift(this.hole)
        }
      }
    },
    selectLeft() {
      if (!this.showTail) {
        this.showTail = true
        return
      }

      this.oldFirstEdge = this.history.slice(0, 2)

      // iterate counterclockwise and choose the first edge
      for (let i = this.size - 1; i >= 0; i--) {
        let newTail = (this.tail + i) % this.size
        if (this.matrix[this.hole * this.size + newTail]) {
          this.history[this.history.length - 1] = newTail
          return
        }
      }
    },
    selectRight() {
      if (!this.showTail) {
        this.showTail = true
        return
      }

      this.oldFirstEdge = this.history.slice(0, 2)

      // iterate counterclockwise and choose the first edge
      for (let i = 1; i <= this.size; i++) {
        let newTail = (this.tail + i) % this.size
        if (this.matrix[this.hole * this.size + newTail]) {
          this.history[this.history.length - 1] = newTail
          return
        }
      }
    },
    showHideTail() {
      this.showTail = !this.showTail
    },
    clicked(event) {
      this.showTail = false
      let gameView = document.getElementById('game-view')
      let x = event.offsetX / gameView.clientWidth * 240 - 120
      let y = event.offsetY / gameView.clientHeight * 240 - 120
      for (let i = 0; i < this.size; i++) {
        if (this.matrix[this.size * this.hole + i] || i == this.hole) {
          let dx = this.nodeXs[i] - x
          let dy = this.nodeYs[i] - y
          if (dx * dx + dy * dy < 40 * 40) {
            if (i == this.hole) {
              this.goBack()
            } else {
              this.history[this.history.length - 1] = i
              this.goForwardHelp()
            }

            return
          }
        }
      }
    },
  }
}
</script>

<template>
  <button class="tabStop" @keydown.up.stop.prevent="goForward()" @keydown.down.stop.prevent="goBack()" @keydown.left.stop.prevent="selectLeft()" @keydown.right.stop.prevent="selectRight()" @keydown.space.stop.prevent="showHideTail()" @click.stop.prevent="clicked">
    <svg class="gameView" id="game-view" viewBox="-120 -120 240 240">
      <defs>
        <path
          id="head-path"
          :d="headPath"
          :style="{ 'offset-path': `path('${arrowPath}')`, 'offset-distance': `${100 * 0.5 * headHeight / 160}%` }"
          fill="none"
          stroke="black"
          stroke-width="18"
          stroke-linecap="round"
          stroke-linejoin="round"
        />
      </defs>
      <path
        v-if="showTail"
        class="head"
        :d="headPath"
        :style="{ 'offset-path': `path('${arrowPath}')`, 'offset-distance': `${100 * 0.5 * headHeight / 160}%` }"
        fill="none"
      />
      <mask id="head-mask">
        <rect x="-130" y="-130" width="260" height="260" fill="white"></rect>
        <use v-if="showTail" href="#head-path"></use>
      </mask>
      <mask id="truncate-mask">
        <rect x="-130" y="-130" width="260" height="260" fill="white"></rect>
        <circle
          :cx="nodeXs[oldFirstEdge[0]]"
          :cy="nodeYs[oldFirstEdge[0]]"
          :r="edgeTruncated ? 25 : 0"
          fill="black"
          :style="{'transition': 'r 0.5s'}">
        </circle>
        <use v-if="showTail" href="#head-path"></use>
      </mask>
      <path
        v-for="edge of edges"
        :class="{ edge: true, active: historyIndices[edge[0] * size + edge[1]] > 0, arrow: ((edge[0] == hole && edge[1] == tail) || (edge[0] == tail && edge[1] == hole)) && showTail }"
        :d="edgePaths[edge.toString()]"
        fill="none"
        v-bind:mask="((edge[0] == hole && edge[1] == tail) || (edge[0] == tail && edge[1] == hole)) && showTail ? 'none' : (edge[0] == oldFirstEdge[0] && edge[1] == oldFirstEdge[1]) || (edge[0] == oldFirstEdge[1] && edge[1] == oldFirstEdge[0]) ? 'url(#truncate-mask)' : 'url(#head-mask)'"
      />
      <image x="-5" y="-5" width="10" height="10" :class="beadClasses[0]"
        href="../assets/heart.svg"
        :style="{ 'transform': 'rotate(90deg) scale(2.7)', 'offset-path': beadOffsetPaths[0] }"
      />
      <image x="-5" y="-5" width="10" height="10" :class="beadClasses[1]"
        href="../assets/butterfly.svg"
        :style="{ 'transform': 'rotate(90deg) scale(2.8)', 'offset-path': beadOffsetPaths[1] }"
      />
      <image x="-5" y="-5" width="10" height="10" :class="beadClasses[2]"
        href="../assets/leaf.svg"
        :style="{ 'transform': 'rotate(90deg) scale(2.5)', 'offset-path': beadOffsetPaths[2] }"
      />
      <image x="-5" y="-5" width="10" height="10" :class="beadClasses[3]"
        href="../assets/mushroom.svg"
        :style="{ 'transform': 'rotate(90deg) scale(2.6)', 'offset-path': beadOffsetPaths[3] }"
      />
      <image x="-5" y="-5" width="10" height="10" :class="beadClasses[4]"
        href="../assets/flower.svg"
        :style="{ 'transform': 'rotate(90deg) scale(2.5)', 'offset-path': beadOffsetPaths[4] }"
      />
      <g v-for="(node, id) of beads">
        <circle
          :r="2 * beadRadius"
          fill="none"
          :class="{ ...beadClasses[id], outline: true }"
          :style="{ 'offset-path': beadOffsetPaths[id] }"
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
.head {
  stroke: var(--color-text);
  stroke-width: 6;
  stroke-linecap: round;
  stroke-linejoin: round;
}
.edge {
  stroke: var(--color-text);
  stroke-width: 4;
  stroke-linecap: round;
  transition: stroke-dasharray 0.5s, stroke-dashoffset 0.5s, stroke-width 0.5s, d 0.5s;
  stroke-dasharray: 4 12;
}
.edge.active {
  stroke-width: 3.5;
  stroke-dasharray: 16 0;
  stroke-dashoffset: 6;
}
.edge.arrow {
  stroke-width: 6;
  stroke-linecap: butt;
  transition: d 0.5s;
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
.bead.outline {
  stroke-width: 0;
  stroke: var(--color-text);
  stroke-linecap: round;
  stroke-linejoin: round;
  transition: stroke-width 0.5s;
}
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
.bead.outline.tail {
  stroke-width: 4;
  transition: none;
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
</style>
