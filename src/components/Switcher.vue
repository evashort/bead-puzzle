<script setup>
import Game from './Game.vue'
import graphData from '../assets/graphs.json'
import Markdown from 'vue3-markdown-it'
import base64js from 'base64-js'
import HistoryNum from '../HistoryNum.js'
import SimpleGraph from '../SimpleGraph.js'
import Permute from '../Permute.js'
import pako from 'pako'
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
        name: '🍪 Soft baked',
        ids: [
          "Hw==",
          "3wA=",
          "+B0=",
          "+J0D",
          "3gw=",
          "3ww=",
        ],
      },
      {
        name: '🍫 Tempered',
        ids: [
          "+Z0D",
          "3owB",
          "7ww=",
          "+J0B",
          "34wB",
          "74wB",
          "/JUB",
          "bY0B",
          "7owB",
        ],
      },
      {
        name: '🥯 Loops',
        ids: [
          "7QA=",
          "fA0=",
          "cQ0=",
          "7gw=",
          "dJYB",
        ],
      },
      {
        name: '🧅 Recursion',
        ids: [
          "Hg==",
          "3gA=",
          "+A0=",
          "+JUB",
          "+I0B",
          "Hw==.2",
          "/gA=",
          "/gw=",
          "/owB",
          "7Qw=",
          "7YwB",
          "xrMB",
        ],
      },
      {
        name: '🍭 Stick with it',
        ids: [
          "eA0=",
          "uJUB",
          "7Aw=",
          "VJYB",
          "VLcB",
          "bI0B",
        ],
      },
      {
        name: '🌰 Tough nut to crack',
        ids: [
          "VZYB",
          "rJYB",
          "6JYB",
          "4J4B",
          "cI0B",
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

    if (groupStart < graphData.graphs.length) {
      groupBoundaries.push(
        {
          name: "Misc",
          start: groupStart,
          stop: graphData.graphs.length,
        },
      )
    }

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
      showSettings: false,
      canAnimate: true,
      curvedPaths: true,
    }
  },
  mounted() {
    window.addEventListener('storage', this.storageChanged)
    console.assert(this.loadSaveFile(localStorage.getItem('save')))
  },
  computed: {
    graph() {
      return this.graphs[this.graphIndex]
    },
    idBytes() {
      return SimpleGraph.fromString(this.graph.id)
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
        '3ww=': `
This puzzle is harder than frog base even though it has more paths for the beads to move along.

That's because its [state space](https://en.wikipedia.org/wiki/State_space) is twice as big.

I'll explain what a state space is at level 10.
`,
        '+B0=': `
Every puzzle starts as far from the goal as possible, so restarting will never get you closer to winning.
`,
        '3gw=': `
When you fold over one layer of an origami frog base, it becomes a diamond with no visible seams.

A bird base has the same shape but a seam is always visible.
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
        'VJYB': `
You don't actually have to stick with it. You can stop playing if you're not having fun anymore.
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
    saveFile() {
      let startedVariations = 0
      let wonVariations = 0
      let eitherVariations = 0
      for (let graph of this.graphs) {
        for (let rotationPuzzles of graph.puzzles) {
          for (let puzzle of rotationPuzzles) {
            startedVariations += puzzle.history.length > 1
            wonVariations += puzzle.won
            eitherVariations += puzzle.won || puzzle.history.length > 1
          }
        }
      }

      let buffer = new ArrayBuffer(21 + 8 * eitherVariations + 4 * startedVariations)
      let view = new DataView(buffer)
      let offset = 0
      view.setUint16(offset, 0, true) // version = 0
      view.setUint16(offset += 2, 3, true) // total settings length
      view.setUint8(offset += 2, 0) // first setting type = flags
      view.setUint8(offset += 1, 1) // first setting length = 1
      view.setUint8(offset += 1, this.canAnimate + (this.curvedPaths << 1))
      let lastPlayedId = SimpleGraph.fromString(this.graph.id)
      let array = new Uint8Array(buffer)
      array.set(lastPlayedId, offset += 1)
      view.setUint16(offset += 4, this.graph.layouts[this.rotation], true)
      view.setUint16(offset += 2, this.puzzle.start, true)
      view.setUint16(offset += 2, eitherVariations, true)
      offset += 2
      let count = 0
      for (let graph of this.graphs) {
        let graphId = SimpleGraph.fromString(graph.id)
        for (let [rotation, rotationPuzzles] of graph.puzzles.entries()) {
          let layout = graph.layouts[rotation]
          for (let puzzle of rotationPuzzles) {
            if (puzzle.history.length > 1 && !puzzle.won) {
              array.set(graphId, offset + 8 * count)
              view.setUint16(offset + 4 + 8 * count, layout, true)
              view.setUint16(offset + 6 + 8 * count, puzzle.start, true)
              count++
            }
          }
        }
      }

      console.assert(count == eitherVariations - wonVariations)
      for (let graph of this.graphs) {
        let graphId = SimpleGraph.fromString(graph.id)
        for (let [rotation, rotationPuzzles] of graph.puzzles.entries()) {
          let layout = graph.layouts[rotation]
          for (let puzzle of rotationPuzzles) {
            if (puzzle.won && puzzle.history.length > 1) {
              array.set(graphId, offset + 8 * count)
              view.setUint16(offset + 4 + 8 * count, layout, true)
              view.setUint16(offset + 6 + 8 * count, puzzle.start, true)
              count++
            }
          }
        }
      }

      console.assert(count == startedVariations)
      for (let graph of this.graphs) {
        let graphId = SimpleGraph.fromString(graph.id)
        for (let [rotation, rotationPuzzles] of graph.puzzles.entries()) {
          let layout = graph.layouts[rotation]
          for (let puzzle of rotationPuzzles) {
            if (puzzle.won && puzzle.history.length <= 1) {
              array.set(graphId, offset + 8 * count)
              view.setUint16(offset + 4 + 8 * count, layout, true)
              view.setUint16(offset + 6 + 8 * count, puzzle.start, true)
              count++
            }
          }
        }
      }

      console.assert(count == eitherVariations)
      offset += 8 * eitherVariations
      view.setUint16(offset, startedVariations, true)
      offset += 2
      count = 0
      for (let graph of this.graphs) {
        let graphId = SimpleGraph.fromString(graph.id)
        let graphNodes = SimpleGraph.bytesToNodeCount(graphId)
        for (let rotationPuzzles of graph.puzzles) {
          for (let puzzle of rotationPuzzles) {
            if (puzzle.history.length > 1) {
              let historyLength = puzzle.history.length - 1
              view.setUint16(offset + 4 * count, puzzle.beads * 8 + historyLength, true)
              let historyNum = HistoryNum.historyToNumber(puzzle.history, graphNodes)
              view.setUint16(offset + 2 + 4 * count, historyNum, true)
              count++
            }
          }
        }
      }

      console.assert(count == startedVariations)
      offset += 4 * startedVariations
      view.setUint16(offset, wonVariations, true)
      offset += 2
      console.assert(offset == buffer.byteLength)
      return buffer
    },
    uncompressedSaveFile() {
      let zipped = new Uint8Array(this.saveFile)
      return base64js.fromByteArray(zipped).replaceAll('+', '-').replaceAll('/', '_')
    },
    compressedSaveFile() {
      let zipped = pako.deflate(this.saveFile)
      return base64js.fromByteArray(zipped).replaceAll('+', '-').replaceAll('/', '_')
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
    storageChanged(event) {
      if (event.key === null) {
        console.log('cleared')
      } else if (event.key == 'save') {
        console.assert(this.loadSaveFile(event.newValue))
      }
    },
    loadSaveFile(saveFile) {
      let zipped = base64js.toByteArray(saveFile)
      let array = pako.inflate(zipped)
      let buffer = array.buffer
      let view = new DataView(buffer)
      let offset = 0
      if (buffer.byteLength < 4) { return false }
      let version = view.getUint16(offset, true)
      if (version > 0) { return false }
      let settingsLength = view.getUint16(offset += 2, true)
      let settingsStop = (offset += 2) + settingsLength
      if (buffer.byteLength < settingsStop) { return false }
      while (offset < settingsStop) {
        let settingType = view.getUint8(offset)
        if (offset + 1 >= settingsStop) { return false }
        let settingLength = view.getUint8(offset += 1)
        offset += 1
        if (offset + settingLength > settingsStop) { return false }
        if (settingType == 0) {
          if (settingLength != 1) { return false }
          let flags = view.getUint8(offset)
          this.canAnimate = Boolean(flags & 0x1)
          this.curvedPaths = Boolean(flags & 0x2)
        }

        offset += settingLength
      }

      console.assert(offset == settingsStop)
      if (offset + 10 > buffer.byteLength) { return false }
      let idLength = 4
      for (; idLength > 0; idLength--) {
        if (array[offset + idLength - 1]) { break }
      }
      let lastPlayedBytes = array.slice(offset, offset + 4)
      let lastPlayedSize = SimpleGraph.bytesToNodeCount(lastPlayedBytes)
      let lastPlayedByteCount = Math.ceil(lastPlayedSize * (lastPlayedSize - 1) * 0.5 * 0.125)
      let lastPlayedId = SimpleGraph.toString(lastPlayedBytes.slice(0, lastPlayedByteCount))
      let lastPlayedLayout = view.getUint16(offset += 4, true)
      let lastPlayedStart = view.getUint16(offset += 2, true)
      for (let [i, graph] of this.graphs.entries()) {
        if (graph.id.split(".", 1)[0] != lastPlayedId) {
          continue
        }

        let rotation = graph.layouts.indexOf(lastPlayedLayout)
        if (rotation < 0) {
          continue
        }

        let variation = -1
        for (let [j, puzzle] of graph.puzzles[rotation].entries()) {
          if (puzzle.start == lastPlayedStart) {
            variation = j
            break
          }
        }

        if (variation < 0) {
          continue
        }

        this.graphIndex = i
        this.rotationIndex = this.rotations.indexOf(rotation)
        this.variation = variation
        break
      }

      let eitherVariations = view.getUint16(offset += 2, true)
      let variationsStop = (offset += 2) + 8 * eitherVariations
      if (buffer.byteLength < variationsStop) { return false }
      let variationIndices = {}
      for (let i = 0; i < eitherVariations; i++) {
        let idBytes = array.slice(offset, offset + 4)
        let idSize = SimpleGraph.bytesToNodeCount(idBytes)
        let idByteCount = Math.ceil(idSize * (idSize - 1) * 0.5 * 0.125)
        let id = SimpleGraph.toString(idBytes.slice(0, idByteCount))
        let layout = view.getUint16(offset + 4, true)
        let start = view.getUint16(offset + 6, true)
        variationIndices[[id, layout, start].toString()] = i
        offset += 8
      }

      console.assert(offset == variationsStop)
      if (offset + 2 > buffer.byteLength) { return false }
      let startedVariations = view.getUint16(offset, true)
      variationsStop = (offset += 2) + 4 * startedVariations
      if (buffer.byteLength < variationsStop) { return false }
      let states = []
      let histories = []
      for (let i = 0; i < startedVariations; i++) {
        states.push(view.getUint16(offset + 4 * i, true))
        histories.push(view.getUint16(offset + 4 * i + 2, true))
      }

      offset = variationsStop
      if (offset + 2 > buffer.byteLength) { return false }
      let wonVariations = view.getUint16(offset, true)
      for (let graph of this.graphs) {
        let id = graph.id.split('.', 1)[0]
        let nodes = SimpleGraph.bytesToNodeCount(SimpleGraph.fromString(id))
        for (let [i, layout] of graph.layouts.entries()) {
          for (let puzzle of graph.puzzles[i]) {
            let key = [id, layout, puzzle.start].toString()
            let index = variationIndices[key]
            puzzle.won = index >= eitherVariations - wonVariations
            if (index < states.length) {
              let historyLength = states[index] % 8
              puzzle.beads = (states[index] - historyLength) / 8
              puzzle.history = HistoryNum.numberToHistory(
                histories[index],
                historyLength,
                nodes,
                Permute.findZero(puzzle.beads),
              )
            } else {
              puzzle.beads = puzzle.start
              puzzle.history = [Permute.findZero(puzzle.beads)]
            }
          }
        }
      }

      this.initialState = {
        beads: this.puzzle.beads,
        history: this.puzzle.history,
      }
      return (offset += 2) == buffer.byteLength
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
    compressedSaveFile(newCompressedSaveFile, oldCompressedSaveFile) {
      localStorage.setItem('save', newCompressedSaveFile)
    },
  },
}
</script>

<template>
  <div :class="{switcher: true, playing: playing}">
    <button
      class="back"
      @click="playing = false"
    >
      <!-- https://github.com/FortAwesome/Font-Awesome/tree/6.x/svgs/solid -->
      <img src="../assets/arrow-left.svg"/>
      Back
    </button>
    <div class="sidebar">
      <div class="navigation">
        <button :disabled="!showSettings" class="tab" @click="showSettings = false">
          <img src="../assets/list.svg"/>
          Levels
        </button>
        <button :disabled="showSettings" class="tab" @click="showSettings = true">
          <img src="../assets/gear.svg"/>
          Settings
        </button>
        <button class="close" @click="playing = true">
          <img src="../assets/xmark.svg"/>
          <img src="../assets/play.svg"/>
        </button>
      </div>
      <div class="levels" v-if="!showSettings">
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
              @input="graphIndex = $event.target.value"
              :checked="graphIndex == group.start + j"
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
      <div class="settings" v-if="showSettings">
        <input type="checkbox" id="setting-0" name="settings" v-model="canAnimate">
        &nbsp;
        <label for="setting-0">Animation</label>
        <br/>
        <input type="checkbox" id="setting-1" name="settings" v-model="curvedPaths">
        &nbsp;
        <label for="setting-1">Curved paths</label>
        <pre style="white-space: pre-wrap; overflow-wrap: break-word;">

{{uncompressedSaveFile.replaceAll('-', '\u2011')}}

{{compressedSaveFile.replaceAll('-', '\u2011')}}
</pre>
      </div>
    </div>
    <dialog id="play">
      <div class="gameHolder">
        <Game
          :graphId="SimpleGraph.toString(SimpleGraph.applyLayout(idBytes, graph.layouts[rotationIndex]))"
          :state="initialState"
          :initialTail="initialTail"
          :autofocus="autofocus"
          :curvedPaths="curvedPaths"
          :canAnimate="canAnimate"
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
                @input="rotationIndex = $event.target.value"
                :checked="rotationIndex == i"
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
                @input="variation = $event.target.value"
                :checked="variation == i"
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
.settings {
  overflow-y: auto;
  padding: 0.75rem 1rem;
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
