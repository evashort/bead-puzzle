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
  },
  computed: {
    graph() {
      return SimpleGraph.fromString(this.graphId)
    },
    size() {
      return SimpleGraph.bytesToNodeCount(this.graph)
    },
    edges() {
      let result = {}
      for (let b = 0; b < this.size; b++) {
        for (let a = 0; a < b; a++) {
          if (SimpleGraph.hasEdge(this.graph, a, b)) {
            result[[a, b].toString()] = [a, b]
          }
        }
      }

      return result
    },
    edgeBeads() {
      let result = {}
      for (let bead = 1; bead < this.size; bead++) {
        let a = this.beadStarts[bead - 1]
        let b = Permute.findValue(this.beads, bead)
        if (b < a) {
          [a, b] = [b, a]
        }

        result[[a, b].toString()] = bead
      }
    }
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
    v-for="([a, b], key) in this.edges"
    :key="key"
    :size="size"
    :a="a"
    :b="b"
    :aPrime="a"
    :bPrime="b"
    :facingA="false"
    :moveToA="false"
    :onPath="false"
    :moving="false"
    :bead="edgeBeads[key] ?? 0"
    :selected="false"
  />
</template>
