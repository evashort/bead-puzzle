<script>
export default {
  props: {
    size: Number,
    a: Number,
    b: Number,
    aPrime: Number,
    bPrime: Number,
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
        [null],
        [null],
        [null, 'mushroom'],
        [null, 'butterfly', 'mushroom'],
        [null, 'heart', 'butterfly', 'mushroom'],
        [null, 'heart', 'butterfly', 'leaf', 'mushroom'],
        [null, 'heart', 'butterfly', 'leaf', 'mushroom', 'flower'],
        [null, 'heart', 'butterfly', 'mushroom', 'leaf', 'mushroom', 'flower'],
      ][this.size][this.bead]
    }
    },
    scale() {
      if (this.name) {
        return {
          heart: 2.7,
          butterfly: 2.8,
          saturn: 3.35,
          leaf: 2.5,
          mushroom: 2.6,
          flower: 2.5,
        }[this.name] * (this.selected ? 5/3 : 1)
      }

      return 1
    },
    beadClasses() {
      return {
        facingA: facingA,
        moveToA: moveToA,
        onPath: onPath,
        moving: moving,
      }
    },
  },
}
</script>

<template>
  <!-- using :key causes the element to be deleted and recreated when the bead
    changes, allowing the slide animation to play again. -->
  <use
    v-if="name"
    :href="`#${name}-bead`"
    :key="name"
    :class="beadClasses"
    :style="{ '--scale': scale }"
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
  animation: slide 0.75s ease forwards;
}
@keyframes slide {
  from { offset-distance: 0%; }
  to { offset-distance: 100%; }
}
.bead.moving.moveToA {
  /* use a different animation instead of "animation-direction: reverse" so
     that the animation plays again when changing direction */
  animation-name: slide-back;
}
@keyframes slide-back {
  from { offset-distance: 100%; }
  to { offset-distance: 0%; }
}
</style>
