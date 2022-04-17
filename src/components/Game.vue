<script>
export default {
  data() {
    let graph = new Int8Array(
      this.startingBeads.length * this.startingBeads.length
    )
    for (let edge of this.edges) {
      graph[edge[0] + this.startingBeads.length * edge[1]] = 1
      graph[edge[1] + this.startingBeads.length * edge[0]] = 1
    }

    return {
      beads: [...this.startingBeads],
      graph: graph,
      loopIndex: 0
    }
  },
  props: {
    startingBeads: Array,
    edges: Array,
    loops: Array
  },
  computed: {
    beadData() {
      return this.beads.map(
        (bead, index, beads) => {
          return {
            id: bead,
            color: ['', 'red', 'green', 'blue', 'indigo', 'pink'][bead],
            position: this.getBeadPosition(index)
          }
        }
      ).filter(x => x.id > 0)
    },
    edgeData() {
      let loop = this.loops[this.loopIndex]
      return this.edges.map(
        (edge, index, edges) => {
          let loopStart = loop.indexOf(edge[0])
          return {
            start: this.getBeadPosition(edge[0]),
            stop: this.getBeadPosition(edge[1]),
            class: loopStart < 0 ? 'inactiveEdge' : (
              this.loops[this.loopIndex][(loopStart + 1) % loop.length] == edge[1]
              || this.loops[this.loopIndex][(loopStart + loop.length - 1) % loop.length] == edge[1]
              ? 'activeEdge' : 'inactiveEdge'
            )
          }
        }
      )
    }
  },
  methods: {
    getBeadPosition(index) {
      return {
        x: Math.sin(2 * Math.PI * index / this.beads.length),
        y: -Math.cos(2 * Math.PI * index / this.beads.length)
      }
    },
    prevLoop() {
      let dest = this.beads.indexOf(0)
      do {
        this.loopIndex += this.loops.length - 1
        this.loopIndex %= this.loops.length
      } while (!this.loops[this.loopIndex].includes(dest))
    },
    nextLoop() {
      let dest = this.beads.indexOf(0)
      do {
        this.loopIndex++
        this.loopIndex %= this.loops.length
      } while (!this.loops[this.loopIndex].includes(dest))
    },
    counterclockwise() {
      let dest = this.beads.indexOf(0)
      let loop = this.loops[this.loopIndex]
      let src = loop[(loop.indexOf(dest) + 1) % loop.length]
      this.beads[dest] = this.beads[src]
      this.beads[src] = 0
    },
    clockwise() {
      let dest = this.beads.indexOf(0)
      let loop = this.loops[this.loopIndex]
      let src = loop[(loop.indexOf(dest) + loop.length - 1) % loop.length]
      this.beads[dest] = this.beads[src]
      this.beads[src] = 0
    }
  }
}
</script>

<template>
  <button class="tabStop" @keydown.up="prevLoop()" @keydown.down="nextLoop()" @keydown.left="counterclockwise()" @keydown.right="clockwise()">
    <svg class="gameView" viewBox="-1.2 -1.2 2.4 2.4">
      <line v-for="edge of edgeData" v-bind:x1="edge.start.x" v-bind:y1="edge.start.y" v-bind:x2="edge.stop.x" v-bind:y2="edge.stop.y" v-bind:class="edge.class" />
      <circle v-for="bead of beadData" v-bind:cx="1.1 * bead.position.x" v-bind:cy="1.1 * bead.position.y" r=".1" v-bind:fill="bead.color" />
    </svg>
  </button>
</template>

<style scoped>
.tabStop {
  background-color: inherit;
  border: none;
  font: inherit;
  padding: 0;
}

.gameView {
  width: 40rem;
  height: 40rem;
}

.activeEdge {
  stroke: var(--color-text);
  stroke-width: 0.05;
}

.inactiveEdge {
  stroke: var(--color-border-hover);
  stroke-width: 0.05;
}
</style>
