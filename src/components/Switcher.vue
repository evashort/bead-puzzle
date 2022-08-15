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
    graphs() {
      return graphData.graphs
    },
    graph() {
      return this.graphs[this.index]
    },
    graphs_by_id() {
      let result = {}
      for (let graph of this.graphs) {
        result[graph.id] = graph
      }

      return result
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
  <div style="text-align: center;">
    {{graph.superior.map(id => graphs_by_id[id]?.name || id)}}
    <br/>
    <div style="height: 40rem; overflow-y: scroll; display: inline-block; text-align: start;">
      <fieldset>
        <legend>Easy</legend>
        <template v-for="i in 10">
          <input
            type="radio"
            :value="i - 1"
            v-model="index"
            :id="`puzzle-${i}`"
            name="puzzle"
          />
          <label :for="`puzzle-${i}`">
            {{i}} {{graphs[i - 1].name || graphs[i - 1].id}}
            {{graphs[i - 1].distance}}
          </label>
          <br/>
        </template>
      </fieldset>
      <fieldset>
        <legend>Hard</legend>
        <template v-for="i in graphs.length - 10">
          <input
            type="radio"
            :value="i + 9"
            v-model="index"
            :id="`puzzle-${i + 10}`"
            name="puzzle"
          />
          <label :for="`puzzle-${i + 10}`">
            {{i + 10}} {{graphs[i + 9].name || graphs[i + 9].id}}
            {{graphs[i + 9].distance}}
          </label>
          <br/>
        </template>
      </fieldset>
    </div>
    <Game :startingBeads="beads" :edges="edges" :baseDustDuration="360" :dustCount="18"/>
  </div>
</template>
