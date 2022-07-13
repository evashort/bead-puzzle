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
    let count = this.startingBeads.length + 1
    let firstTail
    let firstScore = count
    for (let edge of this.edges) {
      let tail
      if (edge[0] == hole) {
        tail = edge[1]
      } else if (edge[1] == hole) {
        tail = edge[0]
      } else {
        continue
      }

      let score = (tail - hole + count) % count
      if (score < firstScore) {
        firstScore = score
        firstTail = tail
      }
    }

    return {
      beads: [...this.startingBeads],
      history: [hole, firstTail]
    }
  },
  props: {
    startingBeads: Array,
    edges: Array
  },
  computed: {
    edgeData() {
      let hole = this.history[this.history.length - 2]
      let tail = this.history[this.history.length - 1]
      return this.edges.map(
        (edge, index, edges) => {
          return {
            prev: this.getBeadPosition(edge[0]),
            start: this.getBeadPosition(edge[0]),
            stop: this.getBeadPosition(edge[1]),
            next: this.getBeadPosition(edge[1]),
            active: (edge[0] == hole && edge[1] == tail) || (edge[0] == tail && edge[1] == hole),
          }
        }
      )
    },
  },
  methods: {
    getBeadPosition(index) {
      return {
        x: Math.sin(2 * Math.PI * index / (1 + this.beads.length)),
        y: -Math.cos(2 * Math.PI * index / (1 + this.beads.length))
      }
    },
    goForward() {
      let hole = this.history[this.history.length - 2]
      let tail = this.history[this.history.length - 1]
      this.beads[this.beads.indexOf(tail)] = hole
      let oldTail = hole
      hole = tail
      for (let removeCount = this.history.length - 2; removeCount >= 0; removeCount--) {
        if (this.history[removeCount] == hole) {
          this.history = this.history.slice(removeCount)
          this.history.push(this.history[1])
          return
        }
      }

      let possibleTails = new Set()
      for (let edge of this.edges) {
        if (edge[0] == hole) {
          possibleTails.add(edge[1])
        } else if (edge[1] == hole) {
          possibleTails.add(edge[0])
        }
      }

      possibleTails.delete(oldTail)

      for (let i = this.history.length - 3; i >= 0; i--) {
        if (possibleTails.has(this.history[i])) {
          this.history.push(this.history[i])
          return
        }
      }

      let count = this.beads.length + 1
      let inLowerHalf = 4 * hole > count && 4 * hole <= 3 * count
      let sign = inLowerHalf ? 1 : -1
      let firstTail = oldTail
      let firstScore = count
      for (let tail of possibleTails) {
        let score = ((tail - hole) * sign + count) % count
        if (score < firstScore) {
          firstScore = score
          firstTail = tail
        }
      }

      this.history.push(firstTail)
    },
    goBack() {
      if (this.history.length > 2) {
        this.history.pop()
        let hole = this.history[this.history.length - 2]
        let tail = this.history[this.history.length - 1]
        this.beads[this.beads.indexOf(hole)] = tail
        if (this.history[0] == tail) {
          // ensure the entire loop is represented
          this.history.unshift(hole)
        }
      }
    },
    selectLeft() {
      let hole = this.history[this.history.length - 2]
      let count = this.beads.length + 1
      let oldTail = this.history[this.history.length - 1]
      let oldScore = (oldTail - hole + count) % count
      let newTail = oldTail
      let newScore = 0
      let maxTail
      let maxScore = 0
      for (let edge of this.edges) {
        let tail
        if (edge[0] == hole) {
          tail = edge[1]
        } else if (edge[1] == hole) {
          tail = edge[0]
        } else {
          continue
        }

        let score = (tail - hole + count) % count
        if (score < oldScore && score > newScore) {
          newScore = score
          newTail = tail
        } else if (score > maxScore) {
          maxScore = score
          maxTail = tail
        }
      }

      this.history[this.history.length - 1] = newTail == oldTail ? maxTail : newTail
    },
    selectRight() {
      let hole = this.history[this.history.length - 2]
      let count = this.beads.length + 1
      let oldTail = this.history[this.history.length - 1]
      let oldScore = (oldTail - hole + count) % count
      let newTail = oldTail
      let newScore = count
      let minTail
      let minScore = count
      for (let edge of this.edges) {
        let tail
        if (edge[0] == hole) {
          tail = edge[1]
        } else if (edge[1] == hole) {
          tail = edge[0]
        } else {
          continue
        }

        let score = (tail - hole + count) % count
        if (score > oldScore && score < newScore) {
          newScore = score
          newTail = tail
        } else if (score < minScore) {
          minScore = score
          minTail = tail
        }
      }

      this.history[this.history.length - 1] = newTail == oldTail ? minTail : newTail
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
