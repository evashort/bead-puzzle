<script setup>
import AnimProp from '../AnimProp.js'
import getControlVector from '../ControlVector.js'
import { cubicBezier, cubicBezierSlope } from '../CubicBezier.js'
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
      stickyAngle: 0,
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
      return `translate(${this.x} ${this.y}) rotate(${this.stickyAngle * 180 / Math.PI})`
    },
    shape() {
      let radius = 0.1
      let yRadius = radius * Math.sqrt(0.75)
      return `M 0 ${-yRadius} L ${radius} ${yRadius} H ${-radius} Z`
    },
    angle() {
      if (this.indexInLoop < 0) { return null }
      return (this.counterclockwise ? Math.PI : 0) + Math.atan2(
        this.xBezierSlope(this.phase.value),
        -this.yBezierSlope(this.phase.value),
      )
    },
    x() {
      if (this.xBezier === null) { return this.nodeX }
      return this.xBezier(this.phase.value)
    },
    y() {
      if (this.yBezier === null) { return this.nodeY }
      return this.yBezier(this.phase.value)
    },
    color() {
      return colors[this.id]
    },
    xBezier() {
      if (this.indexInLoop < 0) { return null }
      return cubicBezier(
        this.otherX,
        this.otherX + this.d1.x,
        this.nodeX + this.d2.x,
        this.nodeX,
      )
    },
    yBezier() {
      if (this.indexInLoop < 0) { return null }
      return cubicBezier(
        this.otherY,
        this.otherY + this.d1.y,
        this.nodeY + this.d2.y,
        this.nodeY,
      )
    },
    xBezierSlope() {
      if (this.indexInLoop < 0) { return null }
      return cubicBezierSlope(
        this.otherX,
        this.otherX + this.d1.x,
        this.nodeX + this.d2.x,
        this.nodeX,
      )
    },
    yBezierSlope() {
      if (this.indexInLoop < 0) { return null }
      return cubicBezierSlope(
        this.otherY,
        this.otherY + this.d1.y,
        this.nodeY + this.d2.y,
        this.nodeY,
      )
    },
    d1() {
      if (this.indexInLoop < 0) { return null }
      return getControlVector(
        this.nodeX - this.otherX,
        this.nodeY - this.otherY,
        this.tailX - this.otherX,
        this.tailY - this.otherY,
        this.dLength,
      )
    },
    d2() {
      if (this.indexInLoop < 0) { return null }
      return getControlVector(
        this.otherX - this.nodeX,
        this.otherY - this.nodeY,
        this.headX - this.nodeX,
        this.headY - this.nodeY,
        this.dLength,
      )
    },
    headX() { return this.getNodeX(this.head) },
    headY() { return this.getNodeY(this.head) },
    nodeX() { return this.getNodeX(this.node) },
    nodeY() { return this.getNodeY(this.node) },
    otherX() { return this.getNodeX(this.other) },
    otherY() { return this.getNodeY(this.other) },
    tailX() { return this.getNodeX(this.tail) },
    tailY() { return this.getNodeY(this.tail) },
    head() {
      if (this.indexInLoop < 0) { return null }
      return this.counterclockwise ? this.getNthNode(-1) : this.getNthNode(1)
    },
    other() {
      if (this.indexInLoop < 0) { return null }
      return this.counterclockwise ? this.oldNode : this.getNthNode(-1)
    },
    tail() {
      if (this.indexInLoop < 0) { return null }
      return this.counterclockwise ? this.getNthNode(2) : this.getNthNode(-2)
    },
    counterclockwise() {
      if (this.indexInLoop < 0) { return null }
      return this.oldNode == this.getNthNode(1)
    },
    indexInLoop() {
      return this.loop.indexOf(this.node)
    }
  },
  methods: {
    getNthNode(offset) {
      if (this.indexInLoop < 0) { return null }
      return this.loop[(this.indexInLoop + this.loop.length + offset) % this.loop.length]
    },
    getNodeX(node) {
      if (node === null) { return null }
      return Math.sin(2 * Math.PI * node / this.nodeCount)
    },
    getNodeY(node) {
      if (node === null) { return null }
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
    angle: {
      handler(newAngle, oldAngle) {
        if (newAngle !== null) {
          this.stickyAngle = newAngle
        }
      },
      immediate: true,
    },
  },
}
</script>

<template>
  <g :transform="transformation">
    <path :d="shape" :fill="color" />
  </g>
</template>
