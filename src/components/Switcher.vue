<script setup>
import Game from './Game.vue'
import graphData from '../assets/graphs.json'
import Markdown from 'vue3-markdown-it'
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
      gameFocused: false,
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
    instructions() {
      // https://docs.microsoft.com/en-us/style-guide/a-z-word-list-term-collections/term-collections/keys-keyboard-shortcuts
      return {
        'pGA=': `
## Moving
### Pointing device
- Select each bead to move it into the empty space.
- Select the empty space to undo.
### Keyboard
- Navigate to the puzzle by selecting it with your pointing device or using the **Tab** key.
- Select **Up arrow** or **W** to move each bead into the empty space.
- Select **Down arrow** or **S** to undo.
`,
        'ZIA=': `
## Selecting
### Pointing device
- Select a bead to move it into the empty space.
### Keyboard
- Use **Left arrow** and **Right arrow** or **A** and **D** to select a bead.
- Select **Up arrow** or **W** to move it into the empty space.
`,
        'pkA=': `
## Spinning
### Pointing device
- Select a bead to move it into the empty space. Two arrows will appear in the center.
- Select the arrows to move the beads around the loop.
### Keyboard
- Select **Up arrow** or **W** to move the beads around the loop.
`,
      }[this.id]
    },
  },
  methods: {
    onFocus(event) {
      let gameButton = document.getElementById('gameButton')
      this.gameFocused = gameButton.contains(event.target)
    },
  },
  watch: {
    id(newId, oldId) {
      this.variation = 0
    },
  },
}
</script>

<template>
  <div :class="{switcher: true, small: !gameFocused}" @focusin.native="onFocus" >
    <div class="levels">
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
    <Game :startingBeads="startingBeads" :edges="edges" :small="!gameFocused" buttonId="gameButton"/>
    <div class="info">
      {{graph.name}}<br/>
      Minimum: {{graph.distance}} moves<br/>
      Without thinking ahead: {{Math.round(graph.difficulty)}} moves<br/>
      State space: {{graph.states}} states<br/>
      <button>hello</button>
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

<style scoped>
.switcher {
  display: grid;
  grid-template-columns: minmax(17rem, 1fr) minmax(27rem, calc(100vh - 0rem)) minmax(17rem, 1fr);
  grid-template-rows: minmax(27rem, 1fr);
  max-width: calc(100vh - 0rem + 2 * 27rem);
  width: 100%;
  height: 100%;
  margin: auto;
  grid-template-areas:
    "levels game info";
}
.switcher.small {
  grid-template-columns: minmax(17rem, 1fr) minmax(17rem, 1fr);
  grid-template-rows: auto minmax(17rem, 1fr);
  grid-template-areas:
    "levels game"
    "levels info";
  max-width: calc(2 * 27rem);
}
.levels {
  grid-area: levels;
  overflow-y: auto;
}
.info {
  grid-area: info;
  overflow-y: auto;
}
</style>
