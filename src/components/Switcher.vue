<script setup>
import Game from './Game.vue'
import graphData from '../assets/graphs.json'
import Markdown from 'vue3-markdown-it'
import base64js from 'base64-js'
import SimpleGraph from '../SimpleGraph.js'
import Permute from '../Permute.js'
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
      rotationIndex: 0,
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
    idBytes() {
      return base64js.toByteArray(this.graph.id)
    },
    nodes() {
      return SimpleGraph.bytesToNodeCount(this.idBytes)
    },
    rotations() {
      let rotations = []
      for (let [i, puzzles] of this.graph['puzzles'].entries()) {
        if (puzzles.length > 0) {
          rotations.push(i)
        }
      }
      return rotations
    },
    letters() {
      return this.rotations.map(i => 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'[i])
    },
    rotation() {
      return this.rotations[this.rotationIndex]
    },
    letter() {
      return this.letters[this.rotationIndex]
    },
    maxVariations() {
      let maxVariations = 0
      for (let puzzles of this.graph['puzzles']) {
        if (puzzles.length > maxVariations) {
          maxVariations = puzzles.length
        }
      }

      return maxVariations
    },
    startingBeads() {
      let index = this.graph.puzzles[this.rotation][this.variation]
      let start = Permute.fromIndex(index, this.nodes)
      let beads = []
      for (let i = 1; i < this.nodes; i++) {
        beads.push(start.indexOf(i))
      }

      return beads
    },
    edges() {
      let index = this.graph['layout']
      let layout = Permute.fromIndex(index, this.nodes)
      return SimpleGraph.bytesToEdges(this.idBytes).map(
        function(edge, index, edges) {
          return [
            (layout.indexOf(edge[0]) + this.rotation) % this.nodes,
            (layout.indexOf(edge[1]) + this.rotation) % this.nodes,
          ]
        },
        this,
      )
    },
    instructions() {
      // https://docs.microsoft.com/en-us/style-guide/a-z-word-list-term-collections/term-collections/keys-keyboard-shortcuts
      let fullInstructions = {
        'DoA=': `
### Pointing device
1. Select each bead to move it into the empty space.
### Keyboard
1. Navigate to the puzzle by selecting it with your pointing device or using the **Tab** key.
1. Select **Up arrow** or **W** to move each bead into the empty space.
### Winning
When every bead is where it belongs, a star will appear in the empty space and the **Next** button will be enabled.
`,
        'A8A=': `
### Pointing device
1. Select a bead to move it into the empty space.

You can select the empty space to undo.
### Keyboard
1. Use **Left arrow** and **Right arrow** or **A** and **D** to choose a bead.
1. Select **Up arrow** or **W** to move it into the empty space.

You can select **Down arrow** or **S** to undo.
`,
        'NwA=': `
### Pointing device
1. Select a bead to move it into the empty space. Two arrows will appear in the center.
1. Select the arrows to move the beads around the loop until the star appears.
### Keyboard
1. Select **Up arrow** or **W** to move the beads around the loop until the star appears.
`,
        'fA==': `
This puzzle has 2 rotations.

Each rotation can be solved in 7 moves.

The rotations add replay value because they have different solutions.
`,
        'H4A=': `
Each rotation of this puzzle has many variations.

Each variation can be solved in 8 moves, but there's no reason to solve them all.

If you can win in less than 27 moves, you must be thinking ahead.
`,
      }
      if (Object.hasOwn(fullInstructions, this.graph.id)) {
        return `
## ${this.graph.name}
${fullInstructions[this.graph.id]}
`
      }

      let comments = {
        'H8A=': `
This puzzle is harder than the last one even though there are more paths for the beads to move along.

That's because its [state space](https://en.wikipedia.org/wiki/State_space) is twice as big.

I'll explain what a state space is when we get to level 10.

---
`,
        'N0A=': `
This is the last puzzle that has a [loop going all the way around](https://en.wikipedia.org/wiki/Hamiltonian_path)
and a shortcut that skips one space.

Once you find a strategy for solving this puzzle, other puzzles like it become boring, so I removed them.

---
`,
        'H7g=': `
Every puzzle starts as far from the goal as possible, so restarting will never get you closer to winning.

---
`,
        'A/w=': `
When you fold over one layer of an origami frog base, it becomes a diamond with no visible seams.

A bird base has the same shape but a seam is always visible (see level 13).

---
`,
        'D7g=': `
In this game, a *state* is an arrangement of beads.

The [state space](https://en.wikipedia.org/wiki/State_space)
is the set of all possible ways to arrange the beads while playing the game.

In this puzzle, there are [6! = 720](https://en.wikipedia.org/wiki/Factorial) ways to
[arrange](https://en.wikipedia.org/wiki/Permutation) the beads,
but only half of them can occur while playing, so the state space has size 360.

---
`,
        'Drg=': `
Here's another puzzle where the state space contains exactly half the possible bead arrangements.

Puzzles like this seem to have only even-length
[cycles](https://en.wikipedia.org/wiki/Cycle_%28graph_theory%29) (loops).

---
`,
      }
      let comment = Object.hasOwn(comments, this.graph.id) ?
        comments[this.graph.id] :
        ''
      return `
## ${this.graph.name}
${comment}

Minimum: ${this.graph.distance} moves

Without thinking ahead: ${Math.round(this.graph.difficulty)} moves

State space: ${this.graph.states} states
`
    },
  },
  methods: {
    focusGame() {
      let play = document.getElementById('play')
      play.close()
      this.autofocus = true
      play.show()
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

      let play = document.getElementById('play')
      let alwaysVisible = window.getComputedStyle(play).getPropertyValue('--always-visible')
      if (!alwaysVisible) {
        this.playing = true
      }
    },
    levelPressed() {
      let play = document.getElementById('play')
      let alwaysVisible = window.getComputedStyle(play).getPropertyValue('--always-visible')
      if (alwaysVisible) {
        this.focusGame()
      } else {
        this.playing = true
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
      this.rotationIndex = 0
      this.variation = 0
    },
    rotationIndex(newRotationIndex, oldRotationIndex) {
      this.variation = 0
    },
    playing(newPlaying, oldPlaying) {
      let play = document.getElementById('play')
      if (newPlaying) {
        this.autofocus = true
        play.show()
      } else {
        play.close()
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
      <!-- https://github.com/FortAwesome/Font-Awesome/tree/6.x/svgs/solid -->
      <img src="../assets/arrow-left.svg"/>
      Back
    </button>
    <div class="sidebar">
      <div class="navigation">
        <button disabled class="tab">
          <img src="../assets/list.svg"/>
          Levels
        </button>
        <button class="tab">
          <img src="../assets/gear.svg"/>
          Settings
        </button>
        <button class="close" @click="this.playing = true">
          <img src="../assets/xmark.svg"/>
          <img src="../assets/play.svg"/>
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
    <dialog id="play">
      <div class="gameHolder">
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
          <img src="../assets/forward-step.svg"/>
          Next
        </button>
      </div>
      <div class="info">
        <Markdown class="instructions" :source="instructions" />
        <div class="columns">
          <fieldset v-if="letters.length > 1">
            <legend>{{letters.length}} rotations</legend>
            <div
              v-for="(letter, i) in letters"
              :key="[graph.id, i].toString()"
              class="radioHolder"
            >
              <input
                type="radio"
                :value="i"
                v-model="rotationIndex"
                :id="`rotation-${letter}`"
                name="rotation"
              />
              <label :for="`rotation-${letter}`">
                {{letter}}{{maxVariations > 1 ? ` (${graph.puzzles[rotations[i]].length})` : ''}}
              </label>
              <br/>
            </div>
          </fieldset>
          <fieldset v-if="maxVariations > 1">
            <legend>{{graph.puzzles[rotation].length}} variations</legend>
            <div
              v-for="i in graph.puzzles[rotation].length"
              :key="[graph.id, letter, i - 1].toString()"
              class="radioHolder"
            >
              <input
                type="radio"
                :value="(i - 1)"
                v-model="variation"
                :id="`variation-${i - 1}`"
                name="variation"
              />
              <label :for="`variation-${i - 1}`">
                {{letter}}{{(i)}}
              </label>
              <br/>
            </div>
          </fieldset>
        </div>
      </div>
    </dialog>
  </div>
</template>

<style scoped>
.switcher {
  display: grid;
  grid-template-columns: 1fr 0fr;
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
.navigation {
  display: flex;
}
.navigation button {
  flex: 1;
}
.tab {
  border-radius: 6px 6px 0 0;
  border-bottom-color: transparent;
  border-left-style: none;
}
.tab:disabled {
  background: inherit;
  color: inherit;
}
.tab:disabled img {
  filter: invert();
}
button {
  font: inherit;
  line-height: 1.6;
}
button::first-line {
  line-height: 2;
}
button img {
  height: 1.5rem;
  padding: 0rem 0.2rem;
  vertical-align: -16%;
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
.close::after {
  content: " Play";
}
.close img:first-child {
  display: none;
}
#play {
  overflow-y: auto;
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
.gameHolder {
  min-height: 15rem;
  max-height: 100vh;
  overflow: hidden;
  position: relative; /* allow children to have position: absolute */
}
.info {
  overflow-y: auto;
  z-index: 1; /* make scroll focus border visible in firefox */
}
.instructions {
  padding: 0rem 0.75rem;
}
.columns {
  display: grid;
  grid-auto-flow: column;
}
.back {
  position: absolute;
  display: none;
  z-index: 1;
  min-width: 5.5rem;
}
.playing .back {
  display: initial;
}
.next {
  position: absolute;
  right: 0;
  bottom: 0;
  min-width: 5.5rem;
}
@media (min-width: 35rem) {
  .switcher {
    grid-template-columns: 3fr 7fr;
  }
  #play {
    --always-visible: 1;
    display: block;
  }
  .close::after {
    content: " Close";
  }
  .close img:first-child {
    display: initial;
  }
  .close img:nth-child(2) {
    display: none;
  }
}
@media (min-width: 60rem) {
  .switcher {
    grid-template-columns: 3fr 11fr;
  }
  #play {
    display: grid;
    grid-template-columns: 7fr 4fr;
    grid-template-rows: 100vh;
    overflow-y: visible;
  }
  .playing #play {
    display: block;
  }
}
</style>
