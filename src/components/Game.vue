<script>
export default {
  data() {
    return {
      beads: [...this.startingBeads]
    }
  },
  props: {
    startingBeads: Array,
  },
  computed: {
    beadData() {
      return this.beads.map(
        (bead, index, beads) => {
          return {
            id: bead,
            color: ['', 'red', 'green', 'blue'][bead],
            x: Math.sin(2 * Math.PI * index / beads.length),
            y: -Math.cos(2 * Math.PI * index / beads.length)
          }
        }
      ).filter(x => x.id > 0)
    }
  },
  methods: {
    moveTop() {
      let dest = this.beads.indexOf(0)
      this.beads[dest] = this.beads[0]
      this.beads[0] = 0
    },
    moveBottom() {
      let dest = this.beads.indexOf(0)
      this.beads[dest] = this.beads[2]
      this.beads[2] = 0
    },
    moveLeft() {
      let dest = this.beads.indexOf(0)
      if (dest != 1) {
        this.beads[dest] = this.beads[3]
        this.beads[3] = 0
      }
    },
    moveRight() {
      let dest = this.beads.indexOf(0)
      if (dest != 3) {
        this.beads[dest] = this.beads[1]
        this.beads[1] = 0
      }
    },
  }
}
</script>

<template>
  <button class="tabStop" @keydown.up="moveTop()" @keydown.down="moveBottom()" @keydown.left="moveLeft()" @keydown.right="moveRight()">
    <svg class="gameView" viewBox="-1 -1 2 2">
      <circle v-for="bead of beadData" v-bind:cx="0.9 * bead.x" v-bind:cy="0.9 * bead.y" r=".1" v-bind:fill="bead.color" />
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
