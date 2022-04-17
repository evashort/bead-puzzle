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
      graph: graph
    }
  },
  props: {
    startingBeads: Array,
    edges: Array,
  },
  computed: {
    beadData() {
      return this.beads.map(
        (bead, index, beads) => {
          return {
            id: bead,
            color: ['', 'red', 'green', 'blue'][bead],
            position: this.getBeadPosition(index)
          }
        }
      ).filter(x => x.id > 0)
    },
    edgeData() {
      return this.edges.map(
        (edge, index, edges) => {
          return {
            start: this.getBeadPosition(edge[0]),
            stop: this.getBeadPosition(edge[1])
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
    moveUp() {
      let dest = this.beads.indexOf(0)
      let src = (dest + 2) % this.beads.length
      if (this.graph[src + this.beads.length * dest]) {
        this.beads[dest] = this.beads[src]
        this.beads[src] = 0
      }
    },
    moveDown() {
      let dest = this.beads.indexOf(0)
      let src = (dest + this.beads.length - 2) % this.beads.length
      if (this.graph[src + this.beads.length * dest]) {
        this.beads[dest] = this.beads[src]
        this.beads[src] = 0
      }
    },
    moveLeft() {
      let dest = this.beads.indexOf(0)
      let src = (dest + 1) % this.beads.length
      if (this.graph[src + this.beads.length * dest]) {
        this.beads[dest] = this.beads[src]
        this.beads[src] = 0
      }
    },
    moveRight() {
      let dest = this.beads.indexOf(0)
      let src = (dest + this.beads.length - 1) % this.beads.length
      if (this.graph[src + this.beads.length * dest]) {
        this.beads[dest] = this.beads[src]
        this.beads[src] = 0
      }
    },
  }
}
</script>

<template>
  <button class="tabStop" @keydown.up="moveUp()" @keydown.down="moveDown()" @keydown.left="moveLeft()" @keydown.right="moveRight()">
    <svg class="gameView" viewBox="-1.2 -1.2 2.4 2.4">
      <line v-for="edge of edgeData" v-bind:x1="edge.start.x" v-bind:y1="edge.start.y" v-bind:x2="edge.stop.x" v-bind:y2="edge.stop.y" class="edge" />
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

.edge {
  stroke: var(--color-text);
  stroke-width: 0.05;
}
</style>
