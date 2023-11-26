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
    id: Number,
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
      ][this.size][this.id]
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
  <use
    :href="`#${name}-bead`"
    :key="name"
    :class="beadClasses"
    :style="{ '--scale': scale }"
  />
</template>

<style scoped>
/*
tail onPath undo reverse offset-rotate
0    0                   -90deg
0    1           0       auto
0    1           1       reverse
1                        reverse
*/
.bead {
  offset-distance: 100%;
  offset-rotate: auto;
  transform: rotate(90deg) scale(var(--scale));
}
.bead.tail {
  offset-rotate: reverse;
}
.canAnimate .bead.animate {
  animation: slide 0.75s ease forwards;
}
@keyframes slide {
  from { offset-distance: 0%; }
  to { offset-distance: 100%; }
}
.canAnimate .bead.alternate {
  animation-name: slide2;
}
@keyframes slide2 {
  from { offset-distance: 0%; }
  to { offset-distance: 100%; }
}
</style>
