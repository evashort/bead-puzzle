<script setup>
import Arrow from './Arrow.vue'
import Edge from './Edge.vue'
import { Visibility } from '../Visibility'
import Bead from './Bead.vue'
import Bezier from '../Bezier.js'
import SimpleGraph from '../SimpleGraph.js'
import Permute from '../Permute.js'
import Trophies from './Trophies.vue'
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
    hasWon: Boolean,
    controlLength: Number,
    gap: Number,
    radius: Number,
    holeRadius: Number,
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
        let [a, b] = edge
        let x1 = this.getX(a), y1 = this.getY(a)
        let x2 = this.getX(b), y2 = this.getY(b)
        let path = null
        let length = Math.sqrt((x2 - x1) * (x2 - x1) + (y2 - y1) * (y2 - y1))
        let [aPrime, bPrime] = this.edgePrimes[edge] ?? edge
        let l = this.controlLength
        if (l > 0) {
          let x0 = this.getX(aPrime), y0 = this.getY(aPrime)
          let x3 = this.getX(bPrime), y3 = this.getY(bPrime)
          let [tx1, ty1] =
            this.getTangent(x1 - x0, y1 - y0, x2 - x1, y2 - y1, l)
          let [tx2, ty2] =
            this.getTangent(x2 - x1, y2 - y1, x3 - x2, y3 - y2, l)
          let cx1 = x1 + tx1, cy1 = y1 + ty1, cx2 = x2 - tx2, cy2 = y2 - ty2
          path = `M${x1} ${y1}L${x1} ${y1}C${cx1} ${cy1},${cx2} ${cy2},${x2} ${y2}L${x2} ${y2}`
        } else {
          let aOrientation = this.beadOrientations[a]
          let aBias = this.beadOrientationIndices[a]
          let aBiased = aOrientation &&
            aBias == 1 - aOrientation.indexOf(b) && aOrientation[aBias] != a
          let [x0, y0] = aBiased ? this.getTurn(x1, y1, aOrientation[aBias]) :
            [x1, y1]
          let bOrientation = this.beadOrientations[b]
          let bBias = this.beadOrientationIndices[b]
          let bBiased = bOrientation &&
            bBias == 1 - bOrientation.indexOf(a) && bOrientation[bBias] != b
          let [x3, y3] = bBiased ? this.getTurn(x2, y2, bOrientation[bBias]) :
            [x2, y2]
          path = `M${x0} ${y0}L${x1} ${y1}C${x1} ${y1},${x2} ${y2},${x2} ${y2}L${x3} ${y3}`
        }
        result[edge] = {
          path: path,
          length: length,
        }
      }

      for (let a = 0; a < this.size; a++) {
        let x = this.getX(a), y = this.getY(a)
        result[[a, a]] = {
          path: `M${x} ${y}`,
          // if this length is used it's a bug but possibly a minor one where
          // falling back to an average-ish edge length is good enough.
          length: this.fallbackEdgeLength,
        }
      }

      return result
    },
    nodeXs() {
      let result = new Array(this.size)
      for (let i = 0; i < this.size; i++) {
        result[i] = this.radius * Math.sin(2 * Math.PI * i / this.size)
      }

      return result
    },
    nodeYs() {
      let result = new Array(this.size)
      for (let i = 0; i < this.size; i++) {
        result[i] = -this.radius * Math.cos(2 * Math.PI * i / this.size)
      }

      return result
    },
    fallbackEdgeLength() {
      return 1.5 * this.radius
    },
    trophyPath() {
      let a = this.trophyReversed ? this.trophyStart : this.trophyEnd
      let b = this.trophyReversed ? this.trophyEnd : this.trophyStart
      let x1 = this.getX(a), y1 = this.getY(a)
      let x3 = this.getX(this.hole), y3 = this.getY(this.hole)
      let x5 = this.getX(b), y5 = this.getY(b)
      let l = this.controlLength
      if (!(l > 0)) {
        let endLength = this.getEdgeLength(a, this.hole)
        let startLength = this.getEdgeLength(this.hole, b)
        return {
          d: `M${x1} ${y1}L${x3} ${y3}L${x5} ${y5}`,
          endLength: endLength + 0.11 * (this.trophyReversed ? -1 : 1),
          totalLength: endLength + startLength,
        }
      }

      let [a1Prime, b1Prime] = this.getEdgePrimes(a, this.hole)
      let [a2Prime, b2Prime] = this.getEdgePrimes(this.hole, b)
      let x0 = this.getX(a1Prime), y0 = this.getY(a1Prime)
      let x6 = this.getX(b2Prime), y6 = this.getY(b2Prime)
      let [tx1, ty1] = this.getTangent(x1 - x0, y1 - y0, x3 - x1, y3 - y1, l)
      let cx1 = x1 + tx1, cy1 = y1 + ty1
      let [tx5, ty5] = this.getTangent(x5 - x3, y5 - y3, x6 - x5, y6 - y5, l)
      let cx5 = x5 - tx5, cy5 = y5 - ty5
      if (a == b) {
        let endLength = Bezier.length(x1, y1, cx1, cy1, x3, y3, x3, y3)
        return {
          d: `M${x1} ${y1}C${cx1} ${cy1},${x3} ${y3},${x3} ${y3}S${cx5} ${cy5},${x5} ${y5}`,
          endLength: endLength + 0.11 * (this.trophyReversed ? -1 : 1),
          totalLength: 2 * endLength
        }
      } else if (b1Prime == b && a2Prime == a) {
        let x4 = x5, y4 = y5
        let [tx2, ty2] = this.getTangent(x3 - x1, y3 - y1, x4 - x3, y4 - y3, l)
        let cx2 = x3 - tx2, cy2 = y3 - ty2, cx4 = x3 + tx2, cy4 = y3 + ty2
        let endLength = Bezier.length(x1, y1, cx1, cy1, cx2, cy2, x3, y3)
        let startLength = Bezier.length(x3, y3, cx4, cy4, cx5, cy5, x5, y5)
        return {
          d: `M${x1} ${y1}C${cx1} ${cy1},${cx2} ${cy2},${x3} ${y3}S${cx5} ${cy5},${x5} ${y5}`,
          endLength: endLength,
          totalLength: endLength + startLength,
        }
      } else {
        let spliceLength = 15
        let spliceControlLength = 13

        let aLength = Math.sqrt((x3 - x1) * (x3 - x1) + (y3 - y1) * (y3 - y1))
        let aParameter = Bezier.estimateParameter(
          Math.sqrt((x3 - x1) * (x3 - x1) + (y3 - y1) * (y3 - y1)),
          b1Prime == this.hole ? 0 : length,
          aLength - spliceLength,
        )
        let x4 = this.getX(b1Prime), y4 = this.getY(b1Prime)
        let [tx2, ty2] = this.getTangent(x3 - x1, y3 - y1, x4 - x3, y4 - y3, l)
        let cx2 = x3 - tx2, cy2 = y3 - ty2
        let [[ax1, ax2, ax3, ax4], axRemoved] =
          Bezier.split(x1, cx1, cx2, x3, aParameter)
        let [[ay1, ay2, ay3, ay4], ayRemoved] =
          Bezier.split(y1, cy1, cy2, y3, aParameter)
        let aFactor = spliceControlLength /
          Math.sqrt((ax4 - ax3) * (ax4 - ax3) + (ay4 - ay3) * (ay4 - ay3))
        let sx1 = ax4, sx2 = sx1 + (ax4 - ax3) * aFactor
        let sy1 = ay4, sy2 = sy1 + (ay4 - ay3) * aFactor

        let bParameter = Bezier.estimateParameter(
          Math.sqrt((x5 - x3) * (x5 - x3) + (y5 - y3) * (y5 - y3)),
          a2Prime == this.hole ? 0 : length,
          spliceLength,
        )
        let x2 = this.getX(a2Prime), y2 = this.getY(a2Prime)
        let [tx4, ty4] = this.getTangent(x3 - x2, y3 - y2, x5 - x3, y5 - y3, l)
        let cx4 = x3 + tx4, cy4 = y3 + ty4
        let [bxRemoved, [bx1, bx2, bx3, bx4]] =
          Bezier.split(x3, cx4, cx5, x5, bParameter)
        let [byRemoved, [by1, by2, by3, by4]] =
          Bezier.split(y3, cy4, cy5, y5, bParameter)
        let bFactor = spliceControlLength /
          Math.sqrt((bx1 - bx2) * (bx1 - bx2) + (by1 - by2) * (by1 - by2))
        let sx4 = bx1, sx3 = sx4 + (bx1 - bx2) * bFactor
        let sy4 = by1, sy3 = sy4 + (by1 - by2) * bFactor

        let actualSpliceLength =
          Bezier.length(sx1, sy1, sx2, sy2, sx3, sy3, sx4, sy4)
        let endLength = Bezier.length(ax1, ay1, ax2, ay2, ax3, ay3, ax4, ay4)
        let startLength = Bezier.length(bx1, by1, bx2, by2, bx3, by3, bx4, by4)
        return {
          d: `M${ax1} ${ay1}C${ax2} ${ay2},${ax3} ${ay3},${ax4} ${ay4}C${sx2} ${sy2},${sx3} ${sy3},${sx4} ${sy4}C${bx2} ${by2},${bx3} ${by3},${bx4} ${by4}`,
          endLength: endLength + 0.5 * actualSpliceLength,
          totalLength: endLength + actualSpliceLength + startLength,
        }
      }
    },
    trophyReversed() {
      return this.beadStarts[0] != this.trophyEnd
    },
    trophyStart() {
      if (this.history.length >= 2) {
        return this.hasLoop ? this.history[1] :
          this.getOppositeEdge(this.history[this.history.length - 2], this.hole)
      } else {
        return this.getOppositeEdge(this.beadStarts[0], this.hole)
      }
    },
    trophyEnd() {
      return this.history.length >= 2 ? this.history[this.history.length - 2] :
        this.getOppositeEdge(this.trophyStart, this.hole)
    },
    trophyOffset() {
      let pushDistance = 0.64 * this.gap
      let pushDelta = this.trophyReversed ? -pushDistance : pushDistance
      if (this.tail == this.trophyEnd) {
        return this.trophyPath.endLength + pushDelta
      } else if (this.tail >= 0) {
        return this.trophyPath.endLength - pushDelta
      } else {
        return this.trophyPath.endLength
      }
    },
    trophyState() {
      return {
        path: this.trophyPath.d,
        totalLength: this.trophyPath.totalLength,
        hole: this.hole,
        reverse: this.trophyReversed,
        end: this.trophyEnd,
        won: this.beads == 0,
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
    hiddenEdge() {
      if (this.history.length <= 1) {
        return null
      }

      let start = this.controlLength > 0 ? 0 : this.activeStart
      return [this.history[start], this.history[start + 1]]
    },
    aHiddenEdge() {
      return this.hiddenEdge ? this.hiddenEdge.toString() : null
    },
    bHiddenEdge() {
      return this.hiddenEdge ? this.hiddenEdge.toReversed().toString() : null
    },
    altHiddenEdge() {
      return this.activeStart >= 1 && this.controlLength > 0 ?
        [this.history[this.activeStart], this.history[this.activeStart + 1]] :
        null
    },
    aAltHiddenEdge() {
      return this.altHiddenEdge ? this.altHiddenEdge.toString() : null
    },
    bAltHiddenEdge() {
      return this.altHiddenEdge ? this.altHiddenEdge.toReversed().toString() :
        null
    },
    endEdge() {
      return this.extra.length >= 1 + this.hasForwardTail ? [
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
      let start = this.controlLength > 0 ? 0 : this.activeStart
      let stop = this.controlLength > 0 ? this.altHistory.length :
        Math.min(this.history.length + 1, this.altHistory.length)
      let result = new Array(this.size).fill(null)
      for (let i = start; i < stop; i++) {
        result[this.altHistory[i]] = [
          this.altHistory[Math.min(i + 1, stop - 1)],
          this.altHistory[Math.max(i - 1, start)],
        ]
      }

      if (
        stop >= 2 &&
        this.altHistory[stop - 1] == this.history[start] &&
        this.history.indexOf(this.history[start], start + 1) < 0
      ) {
        // altHistory forms a simple loop (rather than a figure-8)
        result[this.history[start]] =
          [this.altHistory[start + 1], this.altHistory[stop - 2]]
      }

      if (this.hasLoop && this.tail >= 0 && !this.hasForwardTail) {
        // indicate that going forward would reverse the loop
        result[this.tail].reverse()
      }

      return result
    },
    beadOrientationIndices() {
      // for when the edges are straight and the beads have to pick a side,
      // which side of beadOrientations do they pick?
      let result = new Array(this.size).fill(-1)
      for (let i of this.history) {
        result[i] = 0
      }

      for (let i of this.extra) {
        result[i] = 1
      }

      if (this.hasLoop) {
        result[this.tail] = 1
      }

      return result
    },
    beadEdges() {
      let result = []
      for (let bead = 1; bead < this.size; bead++) {
        let b = Permute.findValue(this.beads, bead)
        let [a, c] = this.beadOrientations[b] ?? [b, b]
        let start = this.beadStarts[bead]
        let moving =
          start != b && (start == a || start == c || (a == b && b == c))
        let reverse = a != c && b != c && (start == c || a == b)
        result.push({
          a: reverse ? c : (moving ? start : a),
          b: b,
          reverse: reverse,
          moving: moving,
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
      let stop = this.history.length + (this.hasLoop || this.hasForwardTail)
      let result = {}
      for (let i = this.activeStart + 1; i < stop; i++) {
        let a = this.altHistory[i - 1], b = this.altHistory[i]
        result[this.sortedPair(a, b)] = true
      }

      return result
    },
    activeStart() {
      return Math.max(
        0,
        this.history.lastIndexOf(
          this.altHistory[this.altHistory.length - 1],
          -2,
        )
      )
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
      return this.nodeXs[i] ?? 0
    },
    getY(i) {
      return this.nodeYs[i] ?? 0
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
    getTurn(x, y, c) {
      // returns a point right next to (x, y) pointing towards c
      let dx = this.getX(c) - x, dy = this.getY(c) - y
      let factor = 0.1 / Math.sqrt(dx * dx + dy * dy)
      return [x + dx * factor, y + dy * factor]
    },
    getEdgePrimes(a, b) {
      let [aPrime, bPrime] = this.edgePrimes[this.sortedPair(a, b)] ?? [a, b]
      return this.swapIf(b < a, aPrime, bPrime)
    },
    getPrimeLength(edge, index) {
      return this.getEdgeLength(
        edge[index],
        (this.edgePrimes[edge] ?? edge)[index],
      )
    },
    getBeadPath(a, b) {
      return (
        this.edgePaths[this.sortedPair(a, b)] ?? this.edgePaths[[b, b]] ?? ''
      ).path
    },
    getEdgeLength(a, b) {
      let edgePath = this.edgePaths[this.sortedPair(a, b)]
      return edgePath ? edgePath.length : this.fallbackEdgeLength
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
    :gap="gap"
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
    :aPrimeLength="getPrimeLength(edge, 0)"
    :bPrimeLength="getPrimeLength(edge, 1)"
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
    :path="getBeadPath(bead.a, bead.b)"
    :pathLength="getEdgeLength(bead.a, bead.b)"
    :facingA="(bead.b < bead.a) != bead.reverse"
    :moveToA="bead.b < bead.a"
    :onPath="beadOrientations[bead.b] != null"
    :moving="bead.moving"
    :bead="i"
    :selected="bead.b == tail"
  />
  <Trophies
    :hasWon="hasWon"
    :state="trophyState"
    :offset="trophyOffset"
    :size="size"
    :radius="radius"
    :holeRadius="holeRadius"
  />
</template>
