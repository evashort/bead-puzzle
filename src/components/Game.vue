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
          history: [hole, tail]
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
        xs[i] = Math.sin(2 * Math.PI * i / this.size + 0.00001)
      }

      return xs
    },
    nodeYs() {
      let ys = new Float64Array(this.size)
      for (let i = 0; i < this.size; i++) {
        ys[i] = -Math.cos(2 * Math.PI * i / this.size + 0.00001)
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
      let controlLength = 0.3
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

      return edgePaths
    },
    nodePaths() {
      let paths = new Array(this.size)
      for (let node = 0; node < this.size; node++) {
        paths[node] = `M ${this.nodeXs[node]} ${this.nodeYs[node]} v -1e-5`
      }

      for (let i = this.loopStart; i < this.loopEnd; i++) {
        let a = this.history[i], b = this.history[i + 1]
        paths[a] = this.edgePaths[[b, a].toString()]
      }

      return paths
    },
    headRadius() {
      return 0.1
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
      return 0.1
    },
    beadHeight() {
      return this.beadRadius * Math.sqrt(3)
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
    getFromNode(node) {
      if (
        this.history.length >= 3 &&
        node == this.history[this.history.length - 3]
      ) {
        return this.hole
      }

      let row = new Uint8Array(
        this.matrix,
        this.size * node * this.matrix.BYTES_PER_ELEMENT,
        this.size,
      )
      return row.indexOf(1) // arbitrary edge
    },
    goForward() {
      this.beads[this.beads.indexOf(this.tail)] = this.hole

      // first choice: go back instead
      if (
        this.history.length >= 3 &&
        this.history[this.history.length - 3] == this.tail
      ) {
        this.history.pop()
        if (this.history.length <= 2) {
          // reached beginning, time to go forward again
          this.history.pop()
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
      if (this.history.length > 2) {
        this.history.pop()
        this.beads[this.beads.indexOf(this.hole)] = this.tail
        if (this.history[0] == this.tail) {
          // ensure the entire loop is represented
          this.history.unshift(this.hole)
        }
      }
    },
    selectLeft() {
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
      // iterate counterclockwise and choose the first edge
      for (let i = 1; i <= this.size; i++) {
        let newTail = (this.tail + i) % this.size
        if (this.matrix[this.hole * this.size + newTail]) {
          this.history[this.history.length - 1] = newTail
          return
        }
      }
    }
  }
}
</script>

<template>
  <button class="tabStop" @keydown.up.stop.prevent="goForward()" @keydown.down.stop.prevent="goBack()" @keydown.left.stop.prevent="selectLeft()" @keydown.right.stop.prevent="selectRight()">
    <svg class="gameView" viewBox="-1.2 -1.2 2.4 2.4">
      <path class="head"
        :d="headPath"
        :style="{ 'offset-path': `path('${arrowPath}')`, 'offset-distance': `${100 * 0.5 * headHeight / 1.6}%` }"
        fill="none"
      />
      <mask id="head-mask">
        <rect x="-1.3" y="-1.3" width="2.6" height="2.6" fill="white"></rect>
        <path
          :d="headPath"
          :style="{ 'offset-path': `path('${arrowPath}')`, 'offset-distance': `${100 * 0.5 * headHeight / 1.6}%` }"
          fill="none"
          stroke="black"
          stroke-width="0.18"
          stroke-linecap="round"
          stroke-linejoin="round"
        />
      </mask>
      <path
        v-for="edge of edges"
        :class="{ edge: true, active: historyIndices[edge[0] * size + edge[1]] > 0, arrow: (edge[0] == this.hole && edge[1] == this.tail) || (edge[0] == this.tail && edge[1] == this.hole) }"
        :d="edgePaths[edge.toString()]"
        fill="none"
        v-bind:mask="(edge[0] == this.hole && edge[1] == this.tail) || (edge[0] == this.tail && edge[1] == this.hole) ? 'none' : 'url(#head-mask)'"
      />
      <g v-for="(node, id) of beads">
        <path
          :d="`M ${0.5 * beadHeight} 0 L ${-0.5 * beadHeight} ${beadRadius} V ${-beadRadius} Z`"
          :fill="['red', 'green', 'blue', 'indigo', 'pink'][id]"
          :class="{bead: true, tail: node == tail, animate: ![-1, history.length - 1].includes(history.indexOf(node)) }"
          :style="{ 'offset-path': `path('${nodePaths[node]}')` }"
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
  stroke-width: 0.06;
  stroke-linecap: round;
  stroke-linejoin: round;
}
.edge {
  stroke: var(--color-text);
  stroke-width: 0.04;
  stroke-linecap: round;
  transition: stroke-dasharray 0.5s, stroke-dashoffset 0.5s, stroke-width 0.5s, d 0.5s;
  stroke-dasharray: 0.04 0.12;
}
.edge.active {
  stroke-width: 0.035;
  stroke-dasharray: 0.16 0;
  stroke-dashoffset: 0.06;
}
.edge.arrow {
  stroke-width: 0.06;
  stroke-linecap: butt;
  transition: d 0.5s;
}
.bead {
  stroke-width: 0;
  stroke: var(--color-text);
  stroke-linecap: round;
  stroke-linejoin: round;
  transition: stroke-width 0.5s;
  offset-distance: 100%;
}
.bead.animate {
  animation: slide 2s ease forwards;
}
@keyframes slide {
  from { offset-distance: 0%; }
  to { offset-distance: 100%; }
}
.bead.tail {
  stroke-width: 0.04;
  transition: none;
}
</style>
