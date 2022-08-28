<script setup>
import Game from './Game.vue'
import graphData from '../assets/graphs.json'
</script>

<script>
export default {
  data() {
    let groups = [
      { name: '📖 Tutorial', stop: 3 },
      { name: '🍰 Piece of cake', stop: 14 },
      { name: '🍪 Soft baked', stop: 25 },
      { name: '🥨 Stick with it', stop: 35 },
      { name: '🥜 Crunch time', stop: 46 },
      { name: '🌰 Tough nut to crack', stop: 57 },
      { name: '🪵 Logjam', stop: 67 },
      { name: '🪨 Rocky road', stop: 78 },
      { name: '💎 Pure pressure', stop: 89 },
    ]
    let start = 0
    for (let group of groups) {
      group.start = start
      start = group.stop
    }

    let idGraphs = {}
    for (let graph of graphData.graphs) {
      idGraphs[graph.id] = graph
    }

    return {
      id: this.startingId,
      variation: 0,
      groups: groups,
      graphs: graphData.graphs,
      idGraphs: idGraphs,
      beads: [],
    }
  },
  props: {
    startingId: String,
  },
  computed: {
    graph() {
      return this.idGraphs[this.id]
    },
    nodes() {
      return this.graph.nodes
    },
    puzzle() {
      return this.graph.puzzles[this.variation]
    },
    rotation() {
      return this.puzzle.rotation
    },
    startingBeads() {
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
  watch: {
    id(newId, oldId) {
      this.variation = 0
    },
  },
}
</script>

<template>
  <div style="text-align: center;">
    {{graph.loop ? 'Loop' : ''}}
    {{graph.superior.map(id => idGraphs[id]?.name || id)}}
    <br/>
    <div style="height: 40rem; overflow-y: scroll; display: inline-block; text-align: start;">
      <fieldset v-for="group in groups">
        <legend>{{group.name}}</legend>
        <template
          v-for="(graph, j) in graphs.slice(group.start, group.stop)"
          :key="graph.id"
        >
          <input
            type="radio"
            :value="graph.id"
            v-model="id"
            :id="`level-${group.start + j}`"
            name="level"
          />
          <label :for="`level-${group.start + j}`">
            {{group.start + j + 1}} {{graph.name || graph.id}}
            {{graph.distance}} {{Math.round(graph.difficulty)}}
          </label>
          <br/>
        </template>
      </fieldset>
    </div>
    <Game v-model:beads="beads" :startingBeads="startingBeads" :edges="edges" :baseDustDuration="360" :dustCount="18"/>
    <div style="height: 40rem; overflow-y: scroll; display: inline-block; text-align: start;">
      {{graph.name}}<br/>
      Minimum: {{graph.distance}} moves<br/>
      Brute force: {{Math.round(graph.difficulty)}} moves<br/>
      State space: {{graph.states}} states<br/>
      {{beads}}
      <fieldset>
        <legend>{{graph.puzzles.length}} variations</legend>
        <template
          v-for="(puzzle, i) in graph.puzzles"
          :key="[graph.id, i]"
        >
          <input
            type="radio"
            :value="i"
            v-model="variation"
            :id="`variation-${i}`"
            name="variation"
          />
          <label :for="`variation-${i}`">
            V{{i}}
          </label>
          <br/>
        </template>
      </fieldset>
    </div>
  </div>
</template>
