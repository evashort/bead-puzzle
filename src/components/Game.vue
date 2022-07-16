<script setup>
import Edge from './Edge.vue'
import Bead from './Bead.vue'
</script>

<script>
export default {
  data() {
    let beadSet = new Set(this.startingBeads)
    let hole = 0
    for (; beadSet.has(hole); hole++) { }
    let size = this.getSize()
    let matrix = this.getMatrix()
    // iterate clockwise and choose the first edge
    for (let i = 1; i < size; i++) {
      let tail = (hole + i) % size
      if (matrix[hole * size + tail]) {
        return {
          beads: [...this.startingBeads],
          history: [hole, tail]
        }
      }
    }

  },
  props: {
    startingBeads: Array,
    edges: Array
  },
  computed: {
    edgeData() {
      return this.edges.map(
        (edge, index, edges) => {
          return {
            prev: this.getBeadPosition(edge[0]),
            start: this.getBeadPosition(edge[0]),
            stop: this.getBeadPosition(edge[1]),
            next: this.getBeadPosition(edge[1]),
            active: (edge[0] == this.hole && edge[1] == this.tail) || (edge[0] == this.tail && edge[1] == this.hole),
          }
        }
      )
    },
    size() {
      return this.getSize()
    },
    matrix() {
      return this.getMatrix()
    },
    hole() {
      return this.history[this.history.length - 2]
    },
    tail() {
      return this.history[this.history.length - 1]
    }
  },
  methods: {
    getSize() {
      return this.startingBeads.length + 1
    },
    getMatrix() {
      let size = this.startingBeads.length + 1
      let matrix = new Uint8Array(size * size)
      for (let [a, b] of this.edges) {
        matrix[a * size + b] = matrix[b * size + a] = 1
      }

      return matrix
    },
    getBeadPosition(index) {
      return {
        x: Math.sin(2 * Math.PI * index / (1 + this.beads.length)),
        y: -Math.cos(2 * Math.PI * index / (1 + this.beads.length))
      }
    },
    goForward() {
      this.beads[this.beads.indexOf(this.tail)] = this.hole

      // first choice: new tail continues the most recent loop
      for (let offset = this.history.length - 2; offset >= 0; offset--) {
        if (this.history[offset] == this.tail) {
          // remove history before the loop
          this.history = this.history.slice(offset)
          this.history.push(this.history[1])
          return
        }
      }

      // second choice: new tail creates the smallest possible loop
      for (let i = this.history.length - 3; i >= 0; i--) {
        let newTail = this.history[i]
        if (
          newTail != this.hole && // going back shouldn't be the default
          this.matrix[this.tail * this.size + newTail]
        ) {
          this.history.push(newTail)
          return
        }
      }

      // third choice: iterate clockwise and choose the first edge
      for (let i = 1; i < this.size; i++) {
        let newTail = (this.tail + i) % this.size
        if (
          newTail != this.hole && // going back shouldn't be the default
          this.matrix[this.tail * this.size + newTail]
        ) {
          this.history.push(newTail)
          return
        }
      }
    },
    goBack() {
      if (this.history.length > 2) {
        this.history.pop()
        this.beads[this.beads.indexOf(this.hole)] = this.tail
        if (this.history[0] == this.tail) {
          // ensure the entire loop is represented
          this.history.unshift(this.hole)
        }
      }
    },
    selectLeft() {
      // iterate counterclockwise and choose the first edge
      for (let i = this.size - 1; i >= 0; i--) {
        let newTail = (this.tail + i) % this.size
        if (this.matrix[this.hole * this.size + newTail]) {
          this.history[this.history.length - 1] = newTail
          return
        }
      }
    },
    selectRight() {
      // iterate counterclockwise and choose the first edge
      for (let i = 1; i <= this.size; i++) {
        let newTail = (this.tail + i) % this.size
        if (this.matrix[this.hole * this.size + newTail]) {
          this.history[this.history.length - 1] = newTail
          return
        }
      }
    }
  }
}
</script>

<template>
  <button class="tabStop" @keydown.up.stop.prevent="goForward()" @keydown.down.stop.prevent="goBack()" @keydown.left.stop.prevent="selectLeft()" @keydown.right.stop.prevent="selectRight()">
    <svg class="gameView" viewBox="-1.1 -1.1 2.2 2.2">
      <Edge v-for="edge of edgeData" :dLength="0.3" v-bind:x0="edge.prev.x" v-bind:y0="edge.prev.y" v-bind:x1="edge.start.x" v-bind:y1="edge.start.y" v-bind:x2="edge.stop.x" v-bind:y2="edge.stop.y" v-bind:x3="edge.next.x" v-bind:y3="edge.next.y" v-bind:active="edge.active" />
      <Bead v-for="(node, id) of beads" :dLength="0.3" v-bind:id="id" v-bind:node="node" :nodeCount="beads.length + 1" />
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
</style>
