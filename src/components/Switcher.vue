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

    return {
      graphIndex: 0,
      variation: 0,
      groups: groups,
      graphs: graphData.graphs,
      autofocus: false,
      playing: false,
    }
  },
  computed: {
    graph() {
      return this.graphs[this.graphIndex]
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
1. Select each bead to move it into the empty space.
1. Select the empty space to undo.
### Keyboard
1. Navigate to the puzzle by selecting it with your pointing device or using the **Tab** key.
1. Select **Up arrow** or **W** to move each bead into the empty space.
1. Select **Down arrow** or **S** to undo.
`,
        'ZIA=': `
## Selecting
### Pointing device
1. Select a bead to move it into the empty space.
### Keyboard
1. Use **Left arrow** and **Right arrow** or **A** and **D** to select a bead.
1. Select **Up arrow** or **W** to move it into the empty space.
`,
        'pkA=': `
## Spinning
### Pointing device
1. Select a bead to move it into the empty space. Two arrows will appear in the center.
1. Select the arrows to move the beads around the loop.
### Keyboard
1. Select **Up arrow** or **W** to move the beads around the loop.
`,
      }[this.graph.id]
    },
  },
  methods: {
    focusGame() {
      let gameHolder = document.getElementById('gameHolder')
      gameHolder.close()
      // TODO: does this work in time? or should we try putting it in mount()?
      this.autofocus = true
      gameHolder.show()
    },
    nextLevel() {
      this.graphIndex++
      this.focusGame()
    },
    levelClicked(event) {
      if (event.pageX == 0 && event.pageY == 0) {
        // Keyboard events are handled by levelPressed because Chrome doesn't
        // fire a click event unless the radio button selection has changed.
        return
      }
      let playArea = document.getElementById('gameHolder').parentNode
      let sidebarOnly = window.getComputedStyle(playArea).display == 'none'
      if (sidebarOnly) {
        this.playing = true
      }
    },
    levelPressed() {
      let playArea = document.getElementById('gameHolder').parentNode
      let sidebarOnly = window.getComputedStyle(playArea).display == 'none'
      if (sidebarOnly) {
        this.playing = true
      } else {
        this.focusGame()
      }
    },
    wonChanged(won) {
      if (won) {
        this.graph.won = true
      }
    },
  },
  watch: {
    graphIndex(newGraphIndex, oldGraphIndex) {
      this.variation = 0
    },
    playing(newPlaying, oldPlaying) {
      if (newPlaying && !oldPlaying) {
        this.focusGame()
      }
    },
  },
}
</script>

<template>
  <div :class="{switcher: true, playing: playing}">
    <button
      class="back"
      @click="this.playing = false"
    >
      Back
    </button>
    <div class="sidebar">
      <div class="navigation">
        <button class="close" @click="this.playing = true">
        </button>
      </div>
      <div class="levels">
        <fieldset v-for="group in groups">
          <legend>{{group.name}}</legend>
          <div
            v-for="(graph, j) in graphs.slice(group.start, group.stop)"
            :key="graph.id"
            class="radioHolder"
          >
            <input
              type="radio"
              :value="group.start + j"
              v-model="graphIndex"
              :id="`level-${group.start + j}`"
              name="level"
              @click="levelClicked"
              @keyup.space.stop.prevent="levelPressed"
              @keyup.enter.stop.prevent="levelPressed"
            />
            <label :for="`level-${group.start + j}`">
              {{group.start + j + 1}}
              {{graph.name || graph.id}}{{graph.won ? ' ✅' : ''}}
            </label>
          </div>
        </fieldset>
      </div>
    </div>
    <div class="play">
      <dialog id="gameHolder">
        <Game
          :startingBeads="startingBeads"
          :edges="edges"
          :autofocus="autofocus"
          @update:won="wonChanged"
        />
        <button
          class="next"
          @click="nextLevel"
          :disabled="!graph.won || graphIndex >= graphs.length - 1"
        >
          Next
        </button>
      </dialog>
      <div class="info">
        {{graph.name}}<br/>
        <Markdown class="instructions" :source="instructions" />
        Minimum: {{graph.distance}} moves<br/>
        Without thinking ahead: {{Math.round(graph.difficulty)}} moves<br/>
        State space: {{graph.states}} states<br/>
        <fieldset>
          <legend>{{graph.puzzles.length}} variations</legend>
          <div
            v-for="(puzzle, i) in graph.puzzles"
            :key="[graph.id, i].toString()"
            class="radioHolder"
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
          </div>
        </fieldset>
      </div>
    </div>
  </div>
</template>

<style scoped>
.switcher {
  display: grid;
  grid-template-columns: 1fr;
  grid-template-rows: 100vh;
}
.switcher.playing {
  display: block;
  min-width: 15rem;
}
.sidebar {
  display: grid;
  grid-template-rows: auto 1fr;
}
.playing .sidebar {
  display: none;
}
fieldset {
  border-width: 1px;
  border-style: none;
  border-top-style: solid;
  border-color: var(--color-text);
}
.radioHolder {
  display: flex;
}
.radioHolder input {
  appearance: none;
  display: block;
	margin: 0;
  width: 100%;
  margin-right: -100%;
  border-radius: 2px;
}
.radioHolder:nth-child(odd) input {
  background-color: black;
}
.radioHolder:nth-child(even) input {
  background-color: var(--color-background-mute);
}
.radioHolder input:checked:not(:active) {
  background-color: lightgray;
}
.radioHolder input:focus:checked:not(:active) {
  background-color: var(--color-text);
}
.radioHolder input:focus:not(:checked) {
  border: solid var(--color-text);
}
.radioHolder input:active {
  border: solid var(--color-text);
}
.radioHolder label {
  padding: 0 0.5rem;
}
.radioHolder input:checked:not(:active)+label {
  color: black;
}
.levels {
  overflow-y: auto;
}
.levels:focus {
  z-index: 1; /* make scroll focus border visible in firefox */
}
.close::before {
  content: "Play";
}
.play {
  overflow-y: auto;
  display: none;
}
.playing .play {
  display: initial;
}
dialog {
  background-color: inherit;
  color: inherit;
  position: static;
  width: auto;
  height: auto;
  border: none;
  padding: 0;
  margin: 0;
}
#gameHolder {
  min-height: 15rem;
  overflow: hidden;
  position: relative; /* allow children to have position: absolute */
  display: block; /* closing the dialog doesn't do anything */
}
.info {
  overflow-y: auto;
  z-index: 1; /* make scroll focus border visible in firefox */
}
.back {
  position: absolute;
  display: none;
  z-index: 1;
}
.playing .back {
  display: initial;
}
.next {
  position: absolute;
  right: 0;
  bottom: 0;
}
@media (min-width: 35rem) {
  .switcher {
    grid-template-columns: 3fr 7fr;
  }
  .play {
    display: initial;
  }
  .close::before {
    content: "Close";
  }
}
@media (min-width: 60rem) {
  .switcher {
    grid-template-columns: 3fr 11fr;
  }
  .play {
    display: grid;
    grid-template-columns: 7fr 4fr;
    grid-template-rows: 100vh;
    overflow-y: visible;
  }
}
</style>
