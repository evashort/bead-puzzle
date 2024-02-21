<script setup>
import Arrow from './Arrow.vue'
import Edge from './Edge.vue'
import { Visibility } from '../Visibility'
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
    for (let bead = 0; bead < size; bead++) {
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
        result[edge] = {
          path: `M${x1} ${y1}C${cx1} ${cy1},${cx2} ${cy2},${x2} ${y2}`,
          length: Math.sqrt((x2 - x1) * (x2 - x1) + (y2 - y1) * (y2 - y1)),
        }
      }

      for (let a = 0; a < this.size; a++) {
        let x = this.getX(a), y = this.getY(a)
        result[[a, a]] = {
          path: `M${x} ${y}`,
          length: 0,
        }
      }

      return result
    },
    trophyPath() {
      let end = null, start = null
      if (this.history.length >= 2) {
        end = this.history[this.history.length - 2]
        start = this.hasLoop ? this.history[1] :
          this.getOppositeEdge(end, this.hole)
      } else {
        start = this.getOppositeEdge(this.beadStarts[0], this.hole)
        end = this.getOppositeEdge(start, this.hole)
      }

      let [a1Prime, b1Prime] = this.getEdgePrimes(end, this.hole)
      let [a2Prime, b2Prime] = this.getEdgePrimes(this.hole, start)
      let x0 = this.getX(a1Prime), y0 = this.getY(a1Prime)
      let x1 = this.getX(end), y1 = this.getY(end)
      let x2 = this.getX(a2Prime), y2 = this.getY(a2Prime)
      let x3 = this.getX(this.hole), y3 = this.getY(this.hole)
      let x4 = this.getX(b1Prime), y4 = this.getY(b1Prime)
      let x5 = this.getX(start), y5 = this.getY(start)
      let x6 = this.getX(b2Prime), y6 = this.getY(b2Prime)
      let l = this.controlLength
      let [tx1, ty1] = this.getTangent(x1 - x0, y1 - y0, x3 - x1, y3 - y1, l)
      let [tx2, ty2] = this.getTangent(x3 - x1, y3 - y1, x4 - x3, y4 - y3, l)
      let cx1 = x1 + tx1, cy1 = y1 + ty1, cx2 = x3 - tx2, cy2 = y3 - ty2
      let [tx4, ty4] = this.getTangent(x3 - x2, y3 - y2, x5 - x3, y5 - y3, l)
      let [tx5, ty5] = this.getTangent(x5 - x3, y5 - y3, x6 - x5, y6 - y5, l)
      let cx4 = x3 + tx4, cy4 = y3 + ty4, cx5 = x5 - tx5, cy5 = y5 - ty5
      let endLength = this.getBezierLength(x1, y1, cx1, cy1, cx2, cy2, x3, y3)
      console.log(endLength)
      return {
        d: `M${x1} ${y1}C${cx1} ${cy1},${cx2} ${cy2},${x3} ${y3}C${cx4} ${cy4},${cx5} ${cy5},${x5} ${y5}`,
        length: endLength,
      }
    },
    aArrowEdge() {
      return [this.hole, this.tail].toString()
    },
    bArrowEdge() {
      return [this.tail, this.hole].toString()
    },
    aOldArrowEdge() {
      return [this.beadStarts[0], this.hole].toString()
    },
    bOldArrowEdge() {
      return [this.hole, this.beadStarts[0]].toString()
    },
    aHiddenEdge() {
      return this.history.length >= 2 ?
        [this.history[0], this.history[1]].toString() : null
    },
    bHiddenEdge() {
      return this.history.length >= 2 ?
        [this.history[1], this.history[0]].toString() : null
    },
    altHiddenEdge() {
      let start = this.history.lastIndexOf(
        this.altHistory[this.altHistory.length - 1],
        -2,
      )
      return start >= 1 ? [this.history[start], this.history[start + 1]] : null
    },
    aAltHiddenEdge() {
      return this.altHiddenEdge ? this.altHiddenEdge.toString() : null
    },
    bAltHiddenEdge() {
      return this.altHiddenEdge ? this.altHiddenEdge.toReversed().toString() :
        null
    },
    endEdge() {
      return this.extra.length >= 1 + (this.tail >= 0) ? [
        this.altHistory[this.altHistory.length - 1],
        this.altHistory[this.altHistory.length - 2],
      ] : null
    },
    aEndEdge() {
      return this.endEdge ? this.endEdge.toString() : null
    },
    bEndEdge() {
      return this.endEdge ? this.endEdge.toReversed().toString() :
        null
    },
    hole() {
      return Permute.findZero(this.beads)
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
        let start = this.beadStarts[bead]
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
    getEdgePrimes(a, b) {
      return (
        b < a ? this.edgePrimes[[b, a]]?.toReversed() : this.edgePrimes[[a, b]]
      ) ?? [a, b]
    },
    getBezierLength(ax, ay, bx, by, cx, cy, dx, dy, error=0.1) {
      let abLength = Math.sqrt((bx - ax) * (bx - ax) + (by - ay) * (by - ay))
      let bcLength = Math.sqrt((cx - dx) * (cx - dx) + (cy - dy) * (cy - dy))
      let cdLength = Math.sqrt((dx - cx) * (dx - cx) + (dy - cy) * (dy - cy))
      let lowerBound = Math.sqrt((dx - ax) * (dx - ax) + (dy - ay) * (dy - ay))
      let upperBound = abLength + bcLength + cdLength
      if (upperBound - lowerBound < error) {
        // overestimate so the trophy rests after the bend when not pushed, so
        // it doesn't snap rotate when pushed forward
        return upperBound
      }

      let b1x = 0.5 * (ax + bx), bcx = 0.5 * (bx + cx), c2x = 0.5 * (cx + dx)
      let c1x = 0.5 * (b1x + bcx), b2x = 0.5 * (bcx + c2x)
      let d1a2x = 0.5 * (c1x + b2x)
      let b1y = 0.5 * (ay + by), bcy = 0.5 * (by + cy), c2y = 0.5 * (cy + dy)
      let c1y = 0.5 * (b1y + bcy), b2y = 0.5 * (bcy + c2y)
      let d1a2y = 0.5 * (c1y + b2y)
      let l1 = this.getBezierLength(
        ax, ay, b1x, b1y, c2x, c1y, d1a2x, d1a2y, 1 * error
      )
      let l2 = this.getBezierLength(
        d1a2x, d1a2y, b2x, b2y, c2x, c2y, dx, dy, 1 * error
      )
      return l1 + l2
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
    toVisibility(hidden, delay) {
      return hidden ? (delay ? Visibility.DelayHidden : Visibility.Hidden) :
        (delay ? Visibility.DelayShown : Visibility.Shown)
    },
    getOppositeEdge(a, b) {
      let bestC = a
      let bestDistance = -Infinity
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
      if (a >= 0 && a != b) {
        // distance from a to c around the perimeter of the circle without
        // passing b
        let aToC = (c - a + this.size) % this.size
        let aToB = (b - a + this.size) % this.size
        return aToB < aToC ? this.size - aToC : aToC
      } else {
        // so that getOppositeEdge returns the first c greater than b when a
        // is null, see comment in getOppositeEdge
        return -1
      }
    },
  },
  watch: {
    beads(newBeads, oldBeads) {
      let newBeadStarts = []
      for (let bead = 0; bead < this.size; bead++) {
        let start = Permute.findValue(oldBeads, bead)
        let end = Permute.findValue(newBeads, bead)
        if (end != start) {
          newBeadStarts.push(start)
        } else {
          newBeadStarts.push(this.beadStarts[bead])
        }
      }

      this.beadStarts = newBeadStarts
    },
  },
}
</script>

<template>
  <Edge
    v-for="edge in SimpleGraph.edges(graph)"
    :key="edge.toString()"
    :path="edgePaths[edge].path"
    :length="edgePaths[edge].length"
    :onPath="activeEdges[edge] ?? false"
    :gap="28"
    :a="toVisibility(
      edge == aHiddenEdge || edge == aAltHiddenEdge || edge == aEndEdge,
      edge == aHiddenEdge ? beadStarts[0] == edge[0] :
        beadStarts[0] == edge[0] && hole != edge[1] && activeEdges[edge],
    )"
    :b="toVisibility(
      edge == bHiddenEdge || edge == bAltHiddenEdge || edge == bEndEdge,
      edge == bHiddenEdge ? beadStarts[0] == edge[1] :
        beadStarts[0] == edge[1] && hole != edge[0] && activeEdges[edge],
    )"
    :masked="edge == aAltHiddenEdge || edge == bAltHiddenEdge"
    :arrow="edge == aArrowEdge || edge == bArrowEdge"
  />
  <Arrow
    v-for="edge in SimpleGraph.edges(graph)"
    :key="edge.toString()"
    :path="edgePaths[edge].path"
    :length="edgePaths[edge].length"
    :onPath="activeEdges[edge] ?? false"
    :aArrow="edge == aArrowEdge"
    :bArrow="edge == bArrowEdge"
    :aOldArrow="edge == aOldArrowEdge"
    :bOldArrow="edge == bOldArrowEdge"
    :suppressOldArrow="tail >= 0"
  />
  <!-- including bead.b in the key allows the slide animation to play again
    when the bead moves. including i in the key allows the slide animation to
    play again when a different bead moves into the old spot. -->
  <Bead
    v-for="(bead, i) in beadEdges"
    :key="`${i}:${bead.b}`"
    :size="size"
    :path="edgePaths[sortedPair(bead.a, bead.b)].path"
    :facingA="(bead.b < bead.a) != bead.reverse"
    :moveToA="bead.b < bead.a"
    :onPath="Object.hasOwn(activeEdges, sortedPair(bead.a, bead.b))"
    :moving="bead.moving"
    :bead="i"
    :selected="bead.b == tail"
  />
  <path :d="trophyPath.d" fill="none" stroke="red"/>
  <circle fill="red" r="10" :style="{'offset-path': `path('${trophyPath.d}')`, 'offset-distance': `${trophyPath.length}px`}"/>
</template>
