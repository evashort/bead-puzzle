<script setup>
import Bead from './Bead.vue'
import Permute from '../Permute.js'
</script>

<script>
export default {
  props: {
    beads: Number,
    beadStarts: Array,
    altHistory: Array,
    historyLength: Number,
    tail: Number,
    loopStart: Number,
    curvedEdges: Boolean,
    edgePaths: Object,
  },
  computed: {
    size() {
      return this.beadStarts.length
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
    beadOrientations() {
      let start = this.curvedEdges ? 0 : this.loopStart
      let stop = this.curvedEdges ? this.altHistory.length :
        Math.min(this.historyLength + 1, this.altHistory.length)
      let result = new Array(this.size).fill(null)
      for (let i = start; i < stop; i++) {
        result[this.altHistory[i]] = [
          this.altHistory[Math.min(i + 1, stop - 1)],
          this.altHistory[Math.max(i - 1, start)],
        ]
      }

      if (
        this.historyLength >= 2 && this.loopStart == 0 &&
        this.altHistory[this.altHistory.length - 1] == this.altHistory[0]
      ) {
        // altHistory forms a simple loop (rather than a figure-8)
        result[this.altHistory[0]] =
          [this.altHistory[1], this.altHistory[this.altHistory.length - 2]]
      }

      if (
        this.historyLength >= 2 &&
        this.tail == this.altHistory[this.historyLength - 2] &&
        this.altHistory[this.historyLength - 1] == this.altHistory[0]
      ) {
        // indicate that going forward would reverse the loop
        result[this.tail].reverse()
      }

      return result
    },
  },
  methods: {
    getBeadPath(a, b) {
      let edgePath = this.edgePaths[b < a ? [b, a] : [a, b]]
      return (edgePath ?? this.edgePaths[[b, b]] ?? { path: '' }).path
    },
    getEdgeLength(a, b) {
      let edgePath = this.edgePaths[b < a ? [b, a] : [a, b]]
      return edgePath ? edgePath.length : this.edgePaths[[0, 0]].length
    },
  },
}
</script>

<template>
  <Bead
    v-for="(bead, i) in beadEdges"
    :key="i"
    :size="size"
    :path="getBeadPath(bead.a, bead.b)"
    :pathLength="getEdgeLength(bead.a, bead.b)"
    :facingA="(bead.b < bead.a) != bead.reverse"
    :moveToA="bead.b < bead.a"
    :onPath="beadOrientations[bead.b] != null"
    :moving="bead.moving"
    :bead="i"
    :destination="bead.b"
    :selected="bead.b == tail"
  />
</template>
