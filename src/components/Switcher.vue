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
      {
        name: '📖 Tutorial',
        ids: [
          "VgA=",
          "SwA=",
          "7AA=",
        ],
      },
      {
        name: 'Part 1',
        ids: [
          "Hw==",
          "3wA=",
          "+B0=",
          "3gw=",
          "3ww=",
          "+J0B",
        ],
      },
      {
        name: '🔄 Loops',
        ids: [
          "7QA=",
          "fA0=",
          "cQ0=",
          "7gw=",
          "dJYB",
        ],
      },
      {
        name: '🪆 Recursion',
        ids: [
          "Hg==",
          "3gA=",
          "+A0=",
          "+JUB",
          "/gA=",
          "/gw=",
          "/owB",
          "7ww=",
          "7Qw=",
          "7YwB",
          "7owB",
          "bY0B",
          "xrMB",
          "eA0=",
          "eI0B",
        ],
      },
      {
        name: 'Part 4',
        ids: [
          "7Aw=",
          "VJYB",
          "cI0B",
          "VZYB",
          "6JYB",
          "pJYB",
        ],
      },
    ]
    let groupBoundaries = []
    let groupStart = 0
    for (let group of groups) {
      let groupStop = groupStart + group.ids.length
      groupBoundaries.push(
        {
          name: group.name,
          start: groupStart,
          stop: groupStop,
        },
      )
      groupStart = groupStop
    }

    groupBoundaries.push(
      {
        name: "Misc",
        start: groupStart,
        stop: graphData.graphs.length,
      },
    )

    let idGraphs = {}
    for (let graph of graphData.graphs) {
      for (let rotationPuzzles of graph.puzzles) {
        for (let [i, puzzle] of rotationPuzzles.entries()) {
          rotationPuzzles[i] = {
            start: puzzle,
            won: false,
            beads: puzzle,
            history: [Permute.findZero(puzzle)],
            tail: null,
          }
        }
      }

      idGraphs[graph.id] = graph
    }

    let graphs = []
    for (let group of groups) {
      for (let id of group.ids) {
        graphs.push(idGraphs[id])
        delete idGraphs[id]
      }
    }

    for (let graph of graphData.graphs) {
      if (Object.hasOwn(idGraphs, graph.id)) {
        graphs.push(graph)
      }
    }

    return {
      graphIndex: 0,
      rotationIndex: 0,
      variation: 0,
      groups: groupBoundaries,
      graphs: graphs,
      initialState: {
        beads: graphs[0].puzzles[0][0].beads,
        history: graphs[0].puzzles[0][0].history,
      },
      initialTail: null,
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
    puzzle() {
      return this.graph.puzzles[this.rotation][this.variation]
    },
    instructions() {
      // https://docs.microsoft.com/en-us/style-guide/a-z-word-list-term-collections/term-collections/keys-keyboard-shortcuts
      let fullInstructions = {
        'VgA=': `
### Pointing device
1. Select each bead to move it into the empty space.
### Keyboard
1. Navigate to the puzzle by selecting it with your pointing device or using the **Tab** key.
1. Select **Up arrow** or **W** to move each bead into the empty space.
### Winning
When every bead is where it belongs, a star will appear in the empty space and the **Next** button will be enabled.
`,
        'SwA=': `
### Pointing device
1. Select a bead to move it into the empty space.

You can select the empty space to undo.
### Keyboard
1. Use **Left arrow** and **Right arrow** or **A** and **D** to choose a bead.
1. Select **Up arrow** or **W** to move it into the empty space.

You can select **Down arrow** or **S** to undo.
`,
        '7AA=': `
### Pointing device
1. Select a bead to move it into the empty space. Two arrows will appear in the center.
1. Select the arrows to move the beads around the loop until the star appears.
### Keyboard
1. Select **Up arrow** or **W** to move the beads around the loop until the star appears.
`,
        'Hw==': `
This puzzle has 2 rotations.

Each rotation can be solved in 7 moves.

The rotations add replay value because they have different solutions.
`,
        '3wA=': `
Each rotation of this puzzle has many variations.

Each variation can be solved in 9 moves, but there's no reason to solve them all.

If you can win in less than 16 moves, you must be thinking ahead.
`,
      }
      if (Object.hasOwn(fullInstructions, this.graph.id)) {
        return `
## ${this.graph.name}
${fullInstructions[this.graph.id]}
`
      }

      let comments = {
        '/ww=': `
This puzzle is harder than the last one even though it has more paths for the beads to move along.

That's because its [state space](https://en.wikipedia.org/wiki/State_space) is twice as big.

I'll explain what a state space is at level 10.
`,
        '+B0=': `
Every puzzle starts as far from the goal as possible, so restarting will never get you closer to winning.
`,
        '3gw=': `
When you fold over one layer of an origami frog base, it becomes a diamond with no visible seams.

A bird base has the same shape but a seam is always visible (see level 8).
`,
        '+A0=': `
In this game, a *state* is an arrangement of beads.

The [state space](https://en.wikipedia.org/wiki/State_space)
is the set of all possible ways to arrange the beads while playing the game.

In this puzzle, there are [6! = 720](https://en.wikipedia.org/wiki/Factorial) ways to
[arrange](https://en.wikipedia.org/wiki/Permutation) the beads,
but only half of them can occur while playing, so the state space has size 360.
`,
        'eA0=': `
Here's another puzzle where the state space contains exactly half the possible bead arrangements.

Puzzles like this seem to have only even-length
[cycles](https://en.wikipedia.org/wiki/Cycle_%28graph_theory%29) (loops).
`,
        '7gw=': `
If you can solve level 7 (Pot) you can solve this one.

See the two spaces that are next to each other but not connected?

If one of those spaces was removed, the remaining spaces would form a pot shape.

Instead of removing a space, you can fill it with the correct bead and then pretend it doesn't exist.
`,
      }
      let comment = Object.hasOwn(comments, this.graph.id) ?
        comments[this.graph.id] :
        ''
      return `
## ${this.graph.name}
Minimum: ${this.graph.distance} moves

Without thinking ahead: ${Math.round(this.graph.difficulty)} moves

State space: ${this.graph.states} states

---

${comment}
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
        this.puzzle.won = true
      }
    },
    stateChanged(state) {
      this.puzzle.beads = state.beads
      this.puzzle.history = state.history
    },
    tailChanged(tail) {
      this.puzzle.tail = tail
    },
  },
  watch: {
    graphIndex(newGraphIndex, oldGraphIndex) {
      this.rotationIndex = 0
      this.variation = 0
      this.initialState = {
        beads: this.puzzle.beads,
        history: this.puzzle.history,
      }
      this.initialTail = this.puzzle.tail
    },
    rotationIndex(newRotationIndex, oldRotationIndex) {
      this.variation = 0
      this.initialState = {
        beads: this.puzzle.beads,
        history: this.puzzle.history,
      }
      this.initialTail = this.puzzle.tail
    },
    variation(newVariation, oldVariation) {
      this.initialState = {
        beads: this.puzzle.beads,
        history: this.puzzle.history,
      }
      this.initialTail = this.puzzle.tail
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
              {{graph.name || graph.id}}{{graph.puzzles.some(rp => rp.some(puzzle => puzzle.won)) ? ' ✅' : ''}}
            </label>
          </div>
        </fieldset>
      </div>
    </div>
    <dialog id="play">
      <div class="gameHolder">
        <Game
          :graph=idBytes
          :layout="Permute.rotateRight(graph.layout, rotation, nodes)"
          :state="initialState"
          :initialTail="initialTail"
          :autofocus="autofocus"
          @update:won="wonChanged"
          @update:state="stateChanged"
          @update:tail="tailChanged"
        />
        <button
          class="next"
          @click="nextLevel"
          :disabled="!puzzle.won || graphIndex >= graphs.length - 1"
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
                {{letter}}{{maxVariations > 1 ? ` (${graph.puzzles[rotations[i]].length})` : ''}}{{graph.puzzles[rotations[i]].some(puzzle => puzzle.won) ? ' ✅' : ''}}
              </label>
              <br/>
            </div>
          </fieldset>
          <fieldset v-if="maxVariations > 1">
            <legend>{{graph.puzzles[rotation].length}} variations</legend>
            <div
              v-for="[i, puzzle] of graph.puzzles[rotation].entries()"
              :key="[graph.id, letter, i].toString()"
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
                {{letter}}{{i + 1}}{{puzzle.won ? ' ✅' : ''}}
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
