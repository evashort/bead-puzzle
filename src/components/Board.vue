<script setup>
import Edge from './Edge.vue'
import Bead from './Bead.vue'
import SimpleGraph from '../SimpleGraph.js'
import Permute from '../Permute.js'
</script>

<script>
export default {
  data() {
    let size = SimpleGraph.bytesToNodeCount(
      SimpleGraph.fromString(this.graphId)
    )
    let beadStarts = []
    for (let bead = 1; bead < size; bead++) {
      beadStarts.push(Permute.findValue(this.beads, bead))
    }
    return {
      beadStarts: beadStarts,
    }
  },
  props: {
    graphId: String,
    beads: Number,
    history: Array,
    tail: Number,
    controlLength: Number,
    radius: Number,
  },
  computed: {
    graph() {
      return SimpleGraph.fromString(this.graphId)
    },
    size() {
      return SimpleGraph.bytesToNodeCount(this.graph)
    },
    edgePrimes() {
      let result = {}
      for (let i = 0; i < this.altHistory.length - 1; i++) {
        let a = this.loopHistory(i), b = this.loopHistory(i + 1)
        let aPrime = this.loopHistory(i - 1)
        let bPrime = this.loopHistory(i + 2)
        result[this.sortedPair(a, b)] = this.swapIf(b < a, aPrime, bPrime)
      }

      return result
    },
    edgePaths() {
      let result = {}
      for (let edge of SimpleGraph.edges(this.graph)) {
        let [aPrime, bPrime] = this.edgePrimes[edge] ?? edge
        let x0 = this.getX(aPrime), y0 = this.getY(aPrime)
        let x1 = this.getX(edge[0]), y1 = this.getY(edge[0])
        let x2 = this.getX(edge[1]), y2 = this.getY(edge[1])
        let x3 = this.getX(bPrime), y3 = this.getY(bPrime)
        let l = this.controlLength
        let [tx1, ty1] = this.getTangent(x1 - x0, y1 - y0, x2 - x1, y2 - y1, l)
        let [tx2, ty2] = this.getTangent(x2 - x1, y2 - y1, x3 - x2, y3 - y2, l)
        let cx1 = x1 + tx1, cy1 = y1 + ty1, cx2 = x2 - tx2, cy2 = y2 - ty2
        result[edge] = `M${x1} ${y1}C${cx1} ${cy1},${cx2} ${cy2},${x2} ${y2}`
      }

      for (let a = 0; a < this.size; a++) {
        let x = this.getX(a), y = this.getY(a)
        result[[a, a]] = `M${x} ${y}`
      }

      return result
    },
    truncatedEdge() {
      if (
        this.history.length >= 2 && !(
          this.hasLoop && this.tail == this.history[1]
        )
      ) {
        return [this.history[0], this.history[1]]
      }

      return null
    },
    edgeOrder() {
      let result = []
      if (this.truncatedEdge) {
        result.push(this.truncatedEdge.toSorted())
      }

      let seen = new Set(result.map(String))
      for (let edge of SimpleGraph.edges(this.graph)) {
        if (!seen.has(edge.toString())) {
          result.push(edge)
        }
      }

      return result
    },
    beadOrientations() {
      let result = {}
      for (let i = 0; i < this.altHistory.length; i++) {
        result[this.altHistory[i]] = [
          this.altHistory[Math.min(i + 1, this.altHistory.length - 1)],
          this.altHistory[Math.max(i - 1, 0)],
        ]
      }

      if (
        this.altHistory.length >= 2 &&
        this.altHistory[this.altHistory.length - 1] == this.history[0] &&
        this.history.indexOf(this.history[0], 1) < 0
      ) {
        // altHistory forms a simple loop (rather than a figure-8)
        result[this.history[0]] =
          [this.altHistory[1], this.altHistory[this.altHistory.length - 2]]
      }

      if (this.hasLoop && this.tail >= 0 && !this.hasForwardTail) {
        // indicate that going forward would reverse the loop
        result[this.tail].reverse()
      }

      return result
    },
    beadEdges() {
      let result = []
      for (let bead = 1; bead < this.size; bead++) {
        let b = Permute.findValue(this.beads, bead)
        let [a, c] = this.beadOrientations[b] ?? [b, b]
        let start = this.beadStarts[bead - 1]
        let reverse = start == c || a == b
        if (reverse) {
          a = c
        }

        let moving = start == a || a == b
        if (moving) {
          a = start
        }
        result.push({
          a: a,
          b: b,
          reverse: reverse && a != b,
          moving: moving && a != b,
        })
      }

      return result
    },
    extra() {
      if (this.history.length <= 1) {
        return this.hasForwardTail ? [this.tail] : []
      } else if (
        this.hasLoop && (this.tail == this.history[1] || !this.hasForwardTail)
      ) {
        return []
      }

      let last = this.history[this.history.length - 1]
      let next = this.hasForwardTail ? this.tail :
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
    altHistory() {
      return this.extra.length ? this.history.concat(this.extra) : this.history
    },
    activeEdges() {
      let start = this.history.lastIndexOf(
        this.altHistory[this.altHistory.length - 1],
        -2,
      )
      let stop = this.history.length + (this.hasLoop || this.hasForwardTail)
      let result = {}
      for (let i = 1; i < this.altHistory.length; i++) {
        let a = this.altHistory[i - 1], b = this.altHistory[i]
        result[this.sortedPair(a, b)] = i > start && i < stop
      }

      return result
    },
    hasLoop() {
      return this.history.length >= 2 &&
        this.history[0] == this.history[this.history.length - 1]
    },
    hasForwardTail() {
      return this.tail >= 0 && (
        this.history.length <= 1 ||
        this.tail != this.history[this.history.length - 2]
      )
    },
  },
  methods: {
    getX(i) {
      return this.radius * Math.sin(2 * Math.PI * i / this.size)
    },
    getY(i) {
      return -this.radius * Math.cos(2 * Math.PI * i / this.size)
    },
    getTangent(dx1, dy1, dx2, dy2, length) {
      // returns a vector with the given length, pointing in the average
      // direction of the two input vectors
      let len1 = Math.sqrt(dx1 * dx1 + dy1 * dy1)
      let len2 = Math.sqrt(dx2 * dx2 + dy2 * dy2)
      let dx3 = dx1 * len2 + dx2 * len1
      let dy3 = dy1 * len2 + dy2 * len1
      let len3 = Math.sqrt(dx3 * dx3 + dy3 * dy3)
      let factor = len3 > 0 ? length / len3 : 0
      return [dx3 * factor, dy3 * factor]
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
    loopHistory(i) {
      if (i < 0) {
        let loopEnd = this.altHistory.indexOf(this.altHistory[0], 1)
        if (loopEnd >= 0) {
          return this.altHistory[(i + 1) % loopEnd + loopEnd - 1]
        } else {
          return this.altHistory[0]
        }
      } else if (i >= this.altHistory.length) {
        let loopEnd = this.altHistory.length - 1
        let loopStart =
          this.altHistory.lastIndexOf(this.altHistory[loopEnd], -2)
        if (loopStart >= 0) {
          return this.altHistory[
            (i - loopStart) % (loopEnd - loopStart) + loopStart
          ]
        } else {
          return this.altHistory[loopEnd]
        }
      } else {
        return this.altHistory[i]
      }
    },
    sortedPair(a, b) {
      return b < a ? [b, a] : [a, b]
    },
    swapIf(condition, a, b) {
      return condition ? [b, a] : [a, b]
    },
  },
  watch: {
    beads(newBeads, oldBeads) {
      let newBeadStarts = []
      for (let bead = 1; bead < this.size; bead++) {
        let start = Permute.findValue(oldBeads, bead)
        let end = Permute.findValue(newBeads, bead)
        if (end != start) {
          newBeadStarts.push(start)
        } else {
          newBeadStarts.push(this.beadStarts[bead - 1])
        }
      }

      this.beadStarts = newBeadStarts
    },
    extra(newExtra, oldExtra) {
      if (newExtra.toString() == oldExtra.toString()) {
        // this watcher gets triggered too much because two Javascript arrays
        // are never equal
        return
      }

      let newBeadStarts = false
      for (let a of newExtra) {
        let bead = Permute.getValue(this.beads, a)
        let orientation = this.beadOrientations[a] ?? [a, a]
        // this condition determines whether the bead's edge will change due to
        // extra changing, see beadEdges()
        if (!orientation.includes(this.beadStarts[bead - 1])) {
          // if so, prevent the slide animation from being replayed
          newBeadStarts = newBeadStarts || this.beadStarts.slice()
          newBeadStarts[bead - 1] = a
        }
      }

      this.beadStarts = newBeadStarts || this.beadStarts
    },
  },
}
</script>

<template>
  <Edge
    v-for="edge of edgeOrder"
    :key="edge.toString()"
    :path="edgePaths[edge]"
    :onPath="activeEdges[edge.toString()] ?? false"
    :hideStart="truncatedEdge && edge.toString() == truncatedEdge.toString()"
    :hideEnd="truncatedEdge && edge.toString() == truncatedEdge.toReversed().toString()"
  />
  <!-- including edge in the key allows the slide animation to play again when
    the bead moves to a different edge. including i in the key allows the slide
    animation to play again when a different bead moves onto the edge. -->
  <Bead
    v-for="(bead, i) in beadEdges"
    :key="`${i}:${sortedPair(bead.a, bead.b)}`"
    :size="size"
    :path="edgePaths[sortedPair(bead.a, bead.b)]"
    :facingA="(bead.b < bead.a) != bead.reverse"
    :moveToA="bead.b < bead.a"
    :onPath="Object.hasOwn(activeEdges, sortedPair(bead.a, bead.b))"
    :moving="bead.moving"
    :bead="i"
    :selected="bead.b == tail"
  />
</template>
