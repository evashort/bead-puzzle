<script setup>
import Arrow from './Arrow.vue'
import Edge from './Edge.vue'
import SimpleGraph from '../SimpleGraph.js'
import { Visibility } from '../Visibility'
</script>

<script>
export default {
  props: {
    graph: Uint8Array,
    holeStart: Number,
    altHistory: Array,
    historyLength: Number,
    tail: Number,
    loopStart: Number,
    curvedEdges: Boolean,
    gap: Number,
    edgePaths: Object,
    edgePrimes: Object,
  },
  computed: {
    size() {
      return SimpleGraph.bytesToNodeCount(this.graph)
    },
    hole() {
      return this.altHistory[this.historyLength - 1]
    },
    aArrowEdge() {
      return [this.hole, this.tail].toString()
    },
    bArrowEdge() {
      return [this.tail, this.hole].toString()
    },
    aOldArrowEdge() {
      return [this.holeStart, this.hole].toString()
    },
    bOldArrowEdge() {
      return [this.hole, this.holeStart].toString()
    },
    hiddenEdge() {
      if (this.historyLength <= 1) {
        return null
      }

      let start = this.curvedEdges ? 0 : this.loopStart
      return [this.altHistory[start], this.altHistory[start + 1]]
    },
    aHiddenEdge() {
      return this.hiddenEdge ? this.hiddenEdge.toString() : null
    },
    bHiddenEdge() {
      return this.hiddenEdge ? this.hiddenEdge.toReversed().toString() : null
    },
    altHiddenEdge() {
      return this.loopStart >= 1 && this.curvedEdges ? [
        this.altHistory[this.loopStart],
        this.altHistory[this.loopStart + 1],
      ] : null
    },
    aAltHiddenEdge() {
      return this.altHiddenEdge ? this.altHiddenEdge.toString() : null
    },
    bAltHiddenEdge() {
      return this.altHiddenEdge ? this.altHiddenEdge.toReversed().toString() :
        null
    },
    endEdge() {
      return (
        this.altHistory.length > this.historyLength + this.hasForwardTail ? [
          this.altHistory[this.altHistory.length - 1],
          this.altHistory[this.altHistory.length - 2],
        ] : null
      )
    },
    aEndEdge() {
      return this.endEdge ? this.endEdge.toString() : null
    },
    bEndEdge() {
      return this.endEdge ? this.endEdge.toReversed().toString() :
        null
    },
    activeEdges() {
      let stop = Math.min(
        this.historyLength + this.hasForwardTail,
        this.altHistory.length,
      )
      let result = {}
      for (let i = this.loopStart + 1; i < stop; i++) {
        let a = this.altHistory[i - 1], b = this.altHistory[i]
        result[b < a ? [b, a] : [a, b]] = true
      }

      return result
    },
    hasForwardTail() {
      return this.tail >= 0 && (
        this.historyLength <= 1 ||
        this.tail != this.altHistory[this.historyLength - 2]
      )
    },
  },
  methods: {
    getPrimeLength(edge, index) {
      let a = edge[index], b = (this.edgePrimes[edge] ?? edge)[index]
      let edgePath = this.edgePaths[b < a ? [b, a] : [a, b]]
      return edgePath ? edgePath.length : this.edgePaths[[0, 0]].length
    },
    toVisibility(hidden, delay) {
      return hidden ? (delay ? Visibility.DelayHidden : Visibility.Hidden) :
        (delay ? Visibility.DelayShown : Visibility.Shown)
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
      edge == aHiddenEdge ? holeStart == edge[0] && loopStart == 0 :
        holeStart == edge[0] && hole != edge[1] && activeEdges[edge],
    )"
    :b="toVisibility(
      edge == bHiddenEdge || edge == bAltHiddenEdge || edge == bEndEdge,
      edge == bHiddenEdge ? holeStart == edge[1] && loopStart == 0 :
        holeStart == edge[1] && hole != edge[0] && activeEdges[edge],
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
</template>
