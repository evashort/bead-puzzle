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
      gameFocused: false,
    }
  },
  props: {
    headerHeight: String,
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
    onFocus(event) {
      let nextButton = document.getElementById('nextButton')
      if (nextButton.contains(event.target)) {
        return
      }

      let gameArea = document.getElementById('gameArea')
      this.gameFocused = gameArea.contains(event.target)
    },
    nextLevel() {
      this.graphIndex++
      document.getElementById('gameButton').focus()
    },
    wonChanged(won) {
      if (won) {
        this.graph.won = true
      }
    },
    focusGame(event) {
      if (event.target.value == this.graphIndex || event.pageX != 0 || event.pageY != 0) {
        document.getElementById('gameButton').focus()
      }
    }
  },
  watch: {
    graphIndex(newGraphIndex, oldGraphIndex) {
      this.variation = 0
    },
  },
}
</script>

<template>
  <div :class="{switcher: true, small: !gameFocused}" @focusin.native="onFocus" :style="{'--header-height': headerHeight}">
    <div class="levels">
      <fieldset v-for="group in groups">
        <legend>{{group.name}}</legend>
        <template
          v-for="(graph, j) in graphs.slice(group.start, group.stop)"
          :key="graph.id"
        >
          <input
            type="radio"
            :value="group.start + j"
            v-model="graphIndex"
            :id="`level-${group.start + j}`"
            name="level"
            @click="focusGame"
          />
          <label :for="`level-${group.start + j}`">
            {{group.start + j + 1}}
            {{graph.name || graph.id}}{{graph.won ? ' ✅' : ''}}
          </label>
          <br/>
        </template>
      </fieldset>
    </div>
    <div class="game" id="gameArea">
      <Markdown v-if="gameFocused" class="instructions" :source="instructions" />
      <Game
        :startingBeads="startingBeads"
        :edges="edges"
        :small="!gameFocused"
        buttonId="gameButton"
        @update:won="wonChanged"
      />
      <button
        id="nextButton"
        @click="nextLevel"
        :class="{next: true}"
        :disabled="!graph.won || graphIndex >= graphs.length - 1"
      >
        Next{{graph.won && graphIndex < graphs.length - 1 ? `: Level ${graphIndex + 2} ${graphs[graphIndex + 1].name}` : ''}}
      </button>
    </div>
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
  grid-template-columns: minmax(17rem, 1fr) minmax(27rem, min(100vh - var(--header-height), 40rem)) minmax(17rem, 1fr);
  grid-template-rows: minmax(27rem, 1fr);
  max-width: calc(clamp(27rem, 100vh - var(--header-height), 40rem) + 2 * 27rem);
  width: 100%;
  height: 100%;
  margin: auto;
  grid-template-areas:
    "levels game info";
}
.switcher.small {
  grid-template-columns: minmax(17rem, 1fr) minmax(17rem, 1fr);
  grid-template-rows: minmax(15rem, auto) minmax(17rem, 1fr);
  grid-template-areas:
    "levels game"
    "levels info";
  max-width: calc(2 * 27rem);
}
.levels {
  grid-area: levels;
  overflow-y: auto;
}
.game {
  grid-area: game;
  overflow-y: auto;
  display: grid;
  grid-template-rows: auto minmax(auto, 1fr) auto;
  grid-template-areas:
    "instructions"
    "game"
    "next";
}
.small .game {
  display: flex;
  justify-content: space-around;
}
.instructions {
  grid-area: instructions;
}
.next {
  grid-area: next;
  height: var(--header-height);
}
.small .next {
  position: absolute;
  right: 0;
  top: 0;
  height: auto;
  margin-top: 0;
  max-width: 7rem;
}
.info {
  grid-area: info;
  overflow-y: auto;
}
</style>
