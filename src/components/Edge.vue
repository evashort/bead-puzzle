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
    controlLength: Number,
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
        bead: true,
        facingA: this.facingA,
        moveToA: this.moveToA,
        onPath: this.onPath,
        moving: this.moving,
      }
    },
    x0() { return this.getX(this.aPrime) },
    y0() { return this.getY(this.aPrime) },
    x1() { return this.getX(this.a) },
    y1() { return this.getY(this.a) },
    x2() { return this.getX(this.b) },
    y2() { return this.getY(this.b) },
    x3() { return this.getX(this.bPrime) },
    y3() { return this.getY(this.bPrime) },
    path() {
      let x1 = this.x1, y1 = this.y1, x2 = this.x2, y2 = this.y2
      let x0 = this.x0, y0 = this.y0, x3 = this.x3, y3 = this.y3
      let l = this.controlLength
      let [tx1, ty1] = this.getTangent(x1 - x0, y1 - y0, x2 - x1, y2 - y1, l)
      let [tx2, ty2] = this.getTangent(x2 - x1, y2 - y1, x3 - x2, y3 - y2, l)
      let cx1 = x1 + tx1, cy1 = y1 + ty1, cx2 = x2 - tx2, cy2 = y2 - ty2
      return `M ${x1} ${y1} C ${cx1} ${cy1}, ${cx2} ${cy2}, ${x2} ${y2}`
    },
  },
  methods: {
    getX(i) {
      return 100 * Math.sin(2 * Math.PI * i / this.size)
    },
    getY(i) {
      return -100 * Math.cos(2 * Math.PI * i / this.size)
    },
    getTangent(dx1, dy1, dx2, dy2, length) {
      // returns a vector with the given length, pointing in the average
      // direction of the two input vectors
      let len1 = Math.sqrt(dx1 * dx1 + dy1 * dy1)
      let len2 = Math.sqrt(dx2 * dx2 + dy2 * dy2)
      let dx3 = dx1 * len2 + dx2 * len1
      let dy3 = dy1 * len2 + dy2 * len1
      let len3 = Math.sqrt(dx3 * dx3 + dy3 * dy3)
      let factor = len3 > 0 ? length / len3 : 0
      return [dx3 * factor, dy3 * factor]
    },
  },
}
</script>

<template>
  <path
    :class="['edge']"
    :d="path"
  />
  <!-- using :key causes the element to be deleted and recreated when the bead
       changes, allowing the slide animation to play again. -->
  <use
    v-if="name"
    :href="`#${name}-bead`"
    :key="name"
    :class="beadClasses"
    :style="{ '--scale': scale, 'offset-path': `path('${path}')` }"
  />
</template>

<style scoped>
.edge {
  fill: none;
  stroke: var(--color-text);
  stroke-width: 4;
  stroke-linecap: round;
  stroke-dasharray: 4 12;
}

.canAnimate .edge {
  transition: d 0.5s;
}

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
