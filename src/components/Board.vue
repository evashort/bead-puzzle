<script setup>
import Beads from './Beads.vue'
import Bezier from '../Bezier.js'
import Edges from './Edges.vue'
import Permute from '../Permute.js'
import SimpleGraph from '../SimpleGraph.js'
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
    altHistory: Array,
    historyLength: Number,
    tail: Number,
    loopStart: Number,
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
          let aTurn = this.beadTurns[a], bTurn = this.beadTurns[b]
          let [x0, y0] = this.getTurn(x1, y1, aTurn == b ? -1 : aTurn)
          let [x3, y3] = this.getTurn(x2, y2, bTurn == a ? -1 : bTurn)
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
      if (this.historyLength >= 2) {
        return this.hasLoop ? this.altHistory[1] :
          SimpleGraph.oppositeEdge(
            this.graph, this.altHistory[this.historyLength - 2], this.hole,
          )
      } else {
        return SimpleGraph.oppositeEdge(
          this.graph, this.beadStarts[0], this.hole,
        )
      }
    },
    trophyEnd() {
      return this.historyLength >= 2 ?
        this.altHistory[this.historyLength - 2] :
        SimpleGraph.oppositeEdge(this.graph, this.trophyStart, this.hole)
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
    hole() {
      return Permute.findZero(this.beads)
    },
    beadTurns() {
      // for when the edges are straight and the beads have to pick a side,
      // which edge do they pick?
      let result = new Array(this.size).fill(-1)
      for (let i = this.loopStart; i < this.historyLength - 1; i++) {
        result[this.altHistory[i]] = this.altHistory[i + 1]
      }

      if (this.altHistory.length > this.historyLength) {
        result[this.altHistory[this.historyLength]] = this.hole
      }

      if (this.hasLoop) {
        result[this.tail] = this.hole
      }

      return result
    },
    hasLoop() {
      return this.historyLength >= 2 &&
        this.altHistory[0] == this.altHistory[this.historyLength - 1]
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
      if (c >= 0) {
        let dx = this.getX(c) - x, dy = this.getY(c) - y
        let factor = 0.1 / Math.sqrt(dx * dx + dy * dy)
        return [x + dx * factor, y + dy * factor]
      } else {
        return [x, y]
      }
    },
    getEdgePrimes(a, b) {
      let [aPrime, bPrime] = this.edgePrimes[this.sortedPair(a, b)] ?? [a, b]
      return this.swapIf(b < a, aPrime, bPrime)
    },
    getEdgeLength(a, b) {
      let edgePath = this.edgePaths[this.sortedPair(a, b)]
      return edgePath ? edgePath.length : this.fallbackEdgeLength
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
        if (this.altHistory[this.loopStart] == this.altHistory[loopEnd]) {
          return this.altHistory[
            (i - this.loopStart) % (loopEnd - this.loopStart) + this.loopStart
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
  <Edges
    :graph="graph"
    :holeStart="beadStarts[0]"
    :altHistory="altHistory"
    :historyLength="historyLength"
    :tail="tail"
    :loopStart="loopStart"
    :curvedEdges="controlLength > 0"
    :gap="gap"
    :edgePaths="edgePaths"
    :edgePrimes="edgePrimes"
  />
  <Beads
    :beads="beads"
    :beadStarts="beadStarts"
    :altHistory="altHistory"
    :historyLength="historyLength"
    :tail="tail"
    :loopStart="loopStart"
    :curvedEdges="controlLength > 0"
    :edgePaths="edgePaths"
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
