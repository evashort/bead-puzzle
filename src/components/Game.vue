<script>
export default {
  data() {
    return {
      beads: [...this.startingBeads],
      lastMove: 2
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
        x: Math.sin(2 * Math.PI * index / this.beads.length) * (
          this.beads[index] == 0 ? 0.3 : 1
        ),
        y: -Math.cos(2 * Math.PI * index / this.beads.length) * (
          this.beads[index] == 0 ? 0.3 : 1
        )
      }
    },
    moveUp() {
      let dest = this.beads.indexOf(0)
      this.beads[dest] = this.beads[2]
      this.beads[2] = 0
      this.lastMove = dest
    },
    moveDown() {
      let dest = this.beads.indexOf(0)
      this.beads[dest] = this.beads[0]
      this.beads[0] = 0
      this.lastMove = dest
    },
    moveLeft() {
      let dest = this.beads.indexOf(0)
      if (dest == 3) {
        this.beads[dest] = this.beads[this.lastMove]
        this.beads[this.lastMove] = 0
      } else {
        this.beads[dest] = this.beads[1]
        this.beads[1] = 0
      }

      this.lastMove = dest
    },
    moveRight() {
      let dest = this.beads.indexOf(0)
      if (dest == 1) {
        this.beads[dest] = this.beads[this.lastMove]
        this.beads[this.lastMove] = 0
      } else {
        this.beads[dest] = this.beads[3]
        this.beads[3] = 0
      }

      this.lastMove = dest
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
