<script setup>
import Trophy from './Trophy.vue'
</script>

<script>
export default {
  data() {
    return {
      firstKey: 0,
      oldPath: "",
      oldTotalLength: 0,
      oldHole: 0,
      oldReverse: false,
      exitViaStart: false,
    }
  },
  props: {
    state: Object,
    offset: Number,
    size: Number,
    radius: Number,
    holeRadius: Number,
  },
  computed: {
    trophies() {
      return [this.oldTrophy, this.trophy, this.hiddenTrophy]
    },
    trophy() {
      return {
        key: (this.firstKey + 1) % 6,
        path: this.state.path,
        offset: this.offset,
        totalLength: this.state.totalLength,
        reverse: this.state.reverse,
        hole: this.state.hole,
        visible: true,
      }
    },
    oldTrophy() {
      return {
        key: this.firstKey % 6,
        path: this.oldPath,
        offset: this.exitViaStart ? Infinity : 0,
        totalLength: this.oldTotalLength,
        reverse: this.oldReverse,
        hole: this.oldHole,
        visible: this.oldPath ? true : false,
      }
    },
    hiddenTrophy() {
      return {
        key: (this.firstKey + 2) % 6,
        path: "M0 0",
        offset: Infinity,
        totalLength: 0,
        reverse: false,
        hole: 0,
        visible: false,
      }
    },
  },
  watch: {
    state(newState, oldState) {
      if (newState.hole != oldState.hole) {
        this.oldHole = oldState.hole
        this.oldPath = oldState.path
        this.oldTotalLength = oldState.totalLength
        this.oldReverse = oldState.reverse
        this.exitViaStart = (newState.hole == oldState.end) != oldState.reverse
        this.firstKey += 1
        this.firstKey %= 6
      }
    },
  }
}
</script>

<template>
  <Trophy
    v-for="trophy in trophies"
    :key="trophy.key"
    :path="trophy.path"
    :offset="trophy.offset"
    :totalLength="trophy.totalLength"
    :reverse="trophy.reverse"
    :hole="trophy.hole"
    :size="size"
    :radius="radius"
    :holeRadius="holeRadius"
    :visible="trophy.visible"
  />
</template>
