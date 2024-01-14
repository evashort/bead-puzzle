<script>
export default {
  props: {
    size: Number,
    path: String,
    facingA: Boolean,
    moveToA: Boolean,
    onPath: Boolean,
    moving: Boolean,
    bead: Number,
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
        moving: this.moving,
      }
    },
  },
}
</script>

<template>
  <use
    v-if="name"
    :href="`#${name}-bead`"
    :class="beadClasses"
    :style="{ '--scale': scale, 'offset-path': `path('${path}')` }"
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
.canAnimate .bead.moving {
  animation: slide 0.75s ease forwards;
}
@keyframes slide {
  from { offset-distance: 0%; }
  to { offset-distance: 100%; }
}
.canAnimate .bead.moving.moveToA {
  /* use a different animation instead of "animation-direction: reverse" so
     that the animation plays again when changing direction */
  animation-name: slide-back;
}
@keyframes slide-back {
  from { offset-distance: 100%; }
  to { offset-distance: 0%; }
}
</style>
