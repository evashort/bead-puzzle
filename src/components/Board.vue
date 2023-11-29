<script setup>
import Edge from './Edge.vue'
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
      for (let i = 0; i < this.history.length - 1; i++) {
        let a = this.history[i], b = this.history[i + 1]
        let aPrime = i > 0 ? this.history[i - 1] : a
        let bPrime = i < this.history.length - 2 ? this.history[i + 2] : b
        if (b < a) {
          // destructuring gives the wrong result for some reason
          // [a, b] = [b, a]
          // [aPrime, bPrime] = [bPrime, aPrime]
          let temp = a; a = b; b = temp
          temp = aPrime; aPrime = bPrime; bPrime = temp
        }

        result[[a, b].toString()] = [aPrime, bPrime]
      }

      return result
    },
    edgePaths() {
      let result = {}
      for (let [a, b] of SimpleGraph.edges(this.graph)) {
        let key = [a, b].toString()
        let [aPrime, bPrime] = this.edgePrimes[key] ?? [a, b]
        let x0 = this.getX(aPrime), y0 = this.getY(aPrime)
        let x1 = this.getX(a), y1 = this.getY(a)
        let x2 = this.getX(b), y2 = this.getY(b)
        let x3 = this.getX(bPrime), y3 = this.getY(bPrime)
        let l = this.controlLength
        let [tx1, ty1] = this.getTangent(x1 - x0, y1 - y0, x2 - x1, y2 - y1, l)
        let [tx2, ty2] = this.getTangent(x2 - x1, y2 - y1, x3 - x2, y3 - y2, l)
        let cx1 = x1 + tx1, cy1 = y1 + ty1, cx2 = x2 - tx2, cy2 = y2 - ty2
        result[key] = `M${x1} ${y1}C${cx1} ${cy1},${cx2} ${cy2},${x2} ${y2}`
      }

      return result
    },
    edgeBeads() {
      let result = {}
      for (let bead = 1; bead < this.size; bead++) {
        let a = this.beadStarts[bead - 1]
        let b = Permute.findValue(this.beads, bead)
        let moveToA = b < a
        if (moveToA) {
          [a, b] = [b, a]
        }

        let moving = a != b
        if (a == b) {
          for (a = 0; a < b; a++) {
            if (SimpleGraph.hasEdge(this.graph, a, b) && !Object.hasOwn(result, [a, b].toString())) {
              break
            }
          }
        }

        if (a == b) {
          moveToA = true
          for (b = a + 1; b < this.size; b++) {
            if (SimpleGraph.hasEdge(this.graph, a, b) && !Object.hasOwn(result, [a, b].toString())) {
              break
            }
          }
        }

        result[[a, b].toString()] = {
          bead: bead,
          moveToA: moveToA,
          moving: moving,
        }
      }

      return result
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
    }
  }
}
</script>

<template>
  <Edge
    v-for="(path, key) in edgePaths"
    :key="key"
    :size="size"
    :path="path"
    :facingA="edgeBeads[key]?.moveToA ?? false"
    :moveToA="edgeBeads[key]?.moveToA ?? false"
    :onPath="false"
    :moving="edgeBeads[key]?.moving ?? false"
    :bead="edgeBeads[key]?.bead ?? 0"
    :selected="false"
    :controlLength="controlLength"
  />
</template>
