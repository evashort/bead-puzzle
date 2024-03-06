<script>
export default {
  data() {
    return {
      animation: 0,
    }
  },
  props: {
    size: Number,
    path: String,
    pathLength: Number,
    facingA: Boolean,
    moveToA: Boolean,
    onPath: Boolean,
    moving: Boolean,
    bead: Number,
    destination: Number,
    selected: Boolean,
  },
  computed: {
    name() {
      return [
        [],
        [],
        ['mushroom'],
        ['butterfly', 'mushroom'],
        ['heart', 'butterfly', 'mushroom'],
        ['heart', 'butterfly', 'leaf', 'mushroom'],
        ['heart', 'butterfly', 'leaf', 'mushroom', 'flower'],
        ['heart', 'butterfly', 'saturn', 'leaf', 'mushroom', 'flower'],
      ][this.size][this.bead]
    },
    scale() {
      return {
        heart: 2.7,
        butterfly: 2.8,
        saturn: 3.35,
        leaf: 2.5,
        mushroom: 2.6,
        flower: 2.5,
      }[this.name] * (this.selected ? 5/3 : 1)
    },
    beadClasses() {
      return {
        bead: true,
        facingA: this.facingA,
        moveToA: this.moveToA,
        onPath: this.onPath,
        moving: this.animation,
        alternate: this.animation == 2,
      }
    },
    duration() {
      let seconds = 0.25 * 0.0075 * this.pathLength + 0.75 * 0.75
      return `${seconds}s`
    },
  },
  watch: {
    moving(newMoving, oldMoving) {
      if (!newMoving) {
        this.animation = 0
      }
    },
    destination(newDestination, oldDestination) {
      this.animation = 1 + (this.animation % 2)
    },
  },
}
</script>

<template>
  <use
    v-if="name"
    :href="`#${name}-bead`"
    :class="beadClasses"
    :style="{
      '--scale': scale,
      'offset-path': `path('${path}')`,
      '--duration': duration,
    }"
  />
</template>

<style scoped>
/*
facingA onPath offset-rotate
        0      -90deg
0       1      auto
1       1      reverse
moveToA moving offset-distance
0       0      100%
0       1      0% -> 100%
1       0      0%
1       1      100% -> 0%
*/
.bead {
  offset-distance: 100%;
  offset-rotate: -90deg;
  transform: rotate(90deg) scale(var(--scale));
}
.bead.onPath {
  offset-rotate: auto;
}
.bead.onPath.facingA {
  offset-rotate: reverse;
}
.bead.moveToA {
  offset-distance: 0%;
}
.bead.moving {
  animation: slide 0s ease forwards;
}
@keyframes slide {
  from { offset-distance: 0%; } to { offset-distance: 100%; }
}
.bead.moving.alternate {
  animation-name: slide-2;
}
@keyframes slide-2 {
  from { offset-distance: 0%; } to { offset-distance: 100%; }
}
.bead.moving.moveToA {
  animation-name: slide-back;
}
@keyframes slide-back {
  from { offset-distance: 100%; } to { offset-distance: 0%; }
}
.bead.moving.alternate.moveToA {
  animation-name: slide-back-2;
}
@keyframes slide-back-2 {
  from { offset-distance: 100%; } to { offset-distance: 0%; }
}
.canAnimate .bead.moving {
  animation-duration: var(--duration);
}
</style>
