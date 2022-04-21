<script setup>
import AnimProp from '../AnimProp.js'
import getControlVector from '../ControlVector.js'
import cubicBezier from '../CubicBezier.js'
</script>

<script>
import BezierEasing from 'bezier-easing'
// https://css-tricks.com/ease-out-in-ease-in-out/
const easeOut = BezierEasing(0, 0, 0.58, 1)
const colors = ['red', 'green', 'blue', 'indigo', 'pink']
export default {
  data() {
    return {
      oldNode: this.node,
      phase: new AnimProp(1, 500, easeOut, 1.5/500),
    }
  },
  props: {
    id: Number,
    node: Number,
    nodeCount: Number,
    loop: Array,
    dLength: Number,
  },
  computed: {
    transformation() {
      return `translate(${this.x} ${this.y})`
    },
    shape() {
      let radius = 0.1
      let yRadius = radius * Math.sqrt(0.75)
      return `M 0 ${-yRadius} L ${radius} ${yRadius} H ${-radius} Z`
    },
    x() {
      return this.xBezier(this.phase.value)
    },
    y() {
      return this.yBezier(this.phase.value)
    },
    color() {
      return colors[this.id]
    },
    xBezier() {
      return cubicBezier(
        this.oldNodeX,
        this.oldNodeX + this.d1.x,
        this.nodeX + this.d2.x,
        this.nodeX,
      )
    },
    yBezier() {
      return cubicBezier(
        this.oldNodeY,
        this.oldNodeY + this.d1.y,
        this.nodeY + this.d2.y,
        this.nodeY,
      )
    },
    d1() {
      return getControlVector(
        this.nodeX - this.oldNodeX,
        this.nodeY - this.oldNodeY,
        this.tailX - this.oldNodeX,
        this.tailY - this.oldNodeY,
        this.dLength,
      )
    },
    d2() {
      return getControlVector(
        this.oldNodeX - this.nodeX,
        this.oldNodeY - this.nodeY,
        this.headX - this.nodeX,
        this.headY - this.nodeY,
        this.dLength,
      )
    },
    headX() { return this.getNodeX(this.head) },
    headY() { return this.getNodeY(this.head) },
    nodeX() { return this.getNodeX(this.node) },
    nodeY() { return this.getNodeY(this.node) },
    oldNodeX() { return this.getNodeX(this.oldNode) },
    oldNodeY() { return this.getNodeY(this.oldNode) },
    tailX() { return this.getNodeX(this.tail) },
    tailY() { return this.getNodeY(this.tail) },
    head() {
      if (this.oldNode == this.node) {
        return this.node
      }

      let minus1 = this.getNthNode(-1)
      return this.oldNode == minus1 ? this.getNthNode(1) : minus1
    },
    tail() {
      if (this.oldNode == this.node) {
        return this.node
      }

      return this.oldNode == this.getNthNode(-1) ? this.getNthNode(-2) : this.getNthNode(2)
    },
  },
  methods: {
    getNthNode(offset) {
      let thisIndex = this.loop.indexOf(this.node)
      if (thisIndex < 0) {
        return this.node
      }

      return this.loop[(thisIndex + this.loop.length + offset) % this.loop.length]
    },
    getNodeX(node) {
      return Math.sin(2 * Math.PI * node / this.nodeCount)
    },
    getNodeY(node) {
      return -Math.cos(2 * Math.PI * node / this.nodeCount)
    },
  },
  watch: {
    node(newNode, oldNode) {
      let reverse = newNode == this.oldNode
      this.oldNode = oldNode
      if (reverse) {
        this.phase.set(1 - this.phase.value, 0)
      } else {
        this.phase.set(0, 0)
      }

      this.phase.set(1)
    },
    loop(newLoop, oldLoop) {
      this.oldNode = this.node
      this.phase.set(1, 0)
    },
  },
}
</script>

<template>
  <g :transform="transformation">
    <path :d="shape" :fill="color" />
  </g>
</template>
