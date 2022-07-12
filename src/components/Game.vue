<script setup>
import Edge from './Edge.vue'
import Bead from './Bead.vue'
</script>

<script>
export default {
  data() {
    return {
      beads: [...this.startingBeads],
      loopIndex: 0,
      spin: false
    }
  },
  props: {
    startingBeads: Array,
    edges: Array,
    loops: Array
  },
  computed: {
    edgeData() {
      let loop = this.loops[this.loopIndex]
      return this.edges.map(
        (edge, index, edges) => {
          let offset = loop.indexOf(edge[0])
          let prevBead = edge[0]
          let nextBead = edge[1]
          let active = false
          if (offset >= 0) {
            if (loop[(offset + 1) % loop.length] == edge[1]) {
              prevBead = loop[(offset + loop.length - 1) % loop.length]
              nextBead = loop[(offset + 2) % loop.length]
              active = true
            }
            else if (loop[(offset + loop.length - 1) % loop.length] == edge[1]) {
              prevBead = loop[(offset + 1) % loop.length]
              nextBead = loop[(offset + loop.length - 2) % loop.length]
              active = true
            }
          }
          return {
            prev: this.getBeadPosition(prevBead),
            start: this.getBeadPosition(edge[0]),
            stop: this.getBeadPosition(edge[1]),
            next: this.getBeadPosition(nextBead),
            active: active,
          }
        }
      )
    },
    hole() {
      let beadSet = new Set(this.beads)
      let hole = 0
      for (; hole <= beadSet.size && beadSet.has(hole); hole++) { }
      return hole
    },
  },
  methods: {
    getBeadPosition(index) {
      return {
        x: Math.sin(2 * Math.PI * index / (1 + this.beads.length)),
        y: -Math.cos(2 * Math.PI * index / (1 + this.beads.length))
      }
    },
    prevLoop() {
      do {
        this.loopIndex += this.loops.length - 1
        this.loopIndex %= this.loops.length
      } while (!this.loops[this.loopIndex].includes(this.hole))
    },
    nextLoop() {
      do {
        this.loopIndex++
        this.loopIndex %= this.loops.length
      } while (!this.loops[this.loopIndex].includes(this.hole))
    },
    counterclockwise() {
      let loop = this.loops[this.loopIndex]
      // important to cache this property so it doesn't change during the for loop
      let hole = this.hole
      if (this.spin) {
        for (let i = 0; i < this.beads.length; i++) {
          let loopIndex = loop.indexOf(this.beads[i])
          if (loopIndex >= 0) {
            this.beads[i] = loop[(loopIndex + loop.length - 1) % loop.length]
            if (this.beads[i] == hole) {
              this.beads[i] = loop[(loopIndex + loop.length - 2) % loop.length]
            }
          }
        }
      } else {
        let src = loop[(loop.indexOf(hole) + 1) % loop.length]
        this.beads[this.beads.indexOf(src)] = hole
      }
    },
    clockwise() {
      let loop = this.loops[this.loopIndex]
      // important to cache this property so it doesn't change during the for loop
      let hole = this.hole
      if (this.spin) {
        for (let i = 0; i < this.beads.length; i++) {
          let loopIndex = loop.indexOf(this.beads[i])
          if (loopIndex >= 0) {
            this.beads[i] = loop[(loopIndex + 1) % loop.length]
            if (this.beads[i] == hole) {
              this.beads[i] = loop[(loopIndex + 2) % loop.length]
            }
          }
        }
      } else {
        let src = loop[(loop.indexOf(hole) + loop.length - 1) % loop.length]
        this.beads[this.beads.indexOf(src)] = hole
      }
    },
    toggleSpin() {
      this.spin = !this.spin
    }
  }
}
</script>

<template>
  <button class="tabStop" @keydown.up.stop.prevent="prevLoop()" @keydown.down.stop.prevent="nextLoop()" @keydown.left.stop.prevent="counterclockwise()" @keydown.right.stop.prevent="clockwise()" @keydown.0.stop.prevent="toggleSpin()">
    <svg class="gameView" viewBox="-1.1 -1.1 2.2 2.2">
      <Edge v-for="edge of edgeData" :dLength="0.3" v-bind:x0="edge.prev.x" v-bind:y0="edge.prev.y" v-bind:x1="edge.start.x" v-bind:y1="edge.start.y" v-bind:x2="edge.stop.x" v-bind:y2="edge.stop.y" v-bind:x3="edge.next.x" v-bind:y3="edge.next.y" v-bind:active="edge.active" />
      <Bead v-for="(node, id) of beads" :dLength="0.3" v-bind:id="id" v-bind:node="node" :nodeCount="beads.length + 1" :loop="this.loops[this.loopIndex]" />
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
