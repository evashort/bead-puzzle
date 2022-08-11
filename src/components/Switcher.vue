<script setup>
import Game from './Game.vue'
import graphData from '../assets/graphs.json'
</script>

<script>
export default {
  data() {
    return {
      index: this.startingIndex,
      puzzleIndex: 0,
    }
  },
  props: {
    startingIndex: Number
  },
  computed: {
    graph() {
      return graphData.graphs[this.index]
    },
    nodes() {
      return this.graph.nodes
    },
    puzzle() {
      return this.graph.puzzles[this.puzzleIndex]
    },
    rotation() {
      return this.puzzle.rotation
    },
    beads() {
      return this.puzzle.beads
    },
    edges() {
      return this.graph.edges.map(
        function(edge, index, edges) {
          return [
            (edge[0] + this.rotation) % this.nodes,
            (edge[1] + this.rotation) % this.nodes,
          ]
        },
        this,
      )
    },
  },
  methods: {
  },
}
</script>

<template>
  <div style="text-align: center">
    <input type="number" v-model="index"/>
    <br/>
    <Game :startingBeads="beads" :edges="edges" :baseDustDuration="360" :dustCount="18"/>
  </div>
</template>
