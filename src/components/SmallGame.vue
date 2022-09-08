<script setup>
</script>

<script>
export default {
  props: {
    beads: Array,
    edges: Array,
    colorIds: Int8Array,
  },
  computed: {
    size() {
      return this.beads.length + 1
    },
    nodeXs() {
      let xs = new Float64Array(this.size)
      for (let i = 0; i < this.size; i++) {
        // avoid vertical edges because of rendering bug for masked paths
        xs[i] = 38 * Math.sin(2 * Math.PI * i / this.size + 0.02)
      }

      return xs
    },
    nodeYs() {
      let ys = new Float64Array(this.size)
      for (let i = 0; i < this.size; i++) {
        ys[i] = -38 * Math.cos(2 * Math.PI * i / this.size + 0.02)
      }

      return ys
    },
    won() {
      for (let [id, node] of this.beads.entries()) {
        if (node != id + 1) { return false }
      }

      return true
    },
    beadScale() {
      return 0.94
    }
  },
}
</script>

<template>
  <svg class="smallView" viewBox="-48 -48 96 96">
    <defs>
      <image id="check" x="-10" y="-10" width="20" height="20"
        href="../assets/checkmark.svg"
      />
    </defs>
    <rect class="blackground" x="-47.75" y="-47.75" width="95.5" height="95.5"/>
    <path
      v-for="[a, b] of edges"
      class="edge"
      :d="`M ${nodeXs[a]} ${nodeYs[a]} L ${nodeXs[b]} ${nodeYs[b]}`"
    />
    <g v-if="colorIds[0] >= 0" :transform="`translate(${nodeXs[beads[colorIds[0]]]},${nodeYs[beads[colorIds[0]]]})`">
      <image x="-4" y="-4" width="8" height="8"
        href="../assets/heart_outline.svg"
        :style="{ 'transform': `scale(2.7) scale(${beadScale})` }"
      />
    </g>
    <g v-if="colorIds[1] >= 0" :transform="`translate(${nodeXs[beads[colorIds[1]]]},${nodeYs[beads[colorIds[1]]]})`">
      <image x="-4" y="-4" width="8" height="8"
        href="../assets/butterfly_outline.svg"
        :style="{ 'transform': `scale(2.8) scale(${beadScale})` }"
      />
    </g>
    <g v-if="colorIds[2] >= 0" :transform="`translate(${nodeXs[beads[colorIds[2]]]},${nodeYs[beads[colorIds[2]]]})`">
      <image x="-4" y="-4" width="8" height="8"
        href="../assets/saturn_outline.svg"
        :style="{ 'transform': `scale(3.35) scale(${beadScale})` }"
      />
    </g>
    <g v-if="colorIds[3] >= 0" :transform="`translate(${nodeXs[beads[colorIds[3]]]},${nodeYs[beads[colorIds[3]]]})`">
      <image x="-4" y="-4" width="8" height="8"
        href="../assets/leaf_outline.svg"
        :style="{ 'transform': `scale(2.5) scale(${beadScale})` }"
      />
    </g>
    <g v-if="colorIds[4] >= 0" :transform="`translate(${nodeXs[beads[colorIds[4]]]},${nodeYs[beads[colorIds[4]]]})`">
      <image x="-4" y="-4" width="8" height="8"
        href="../assets/mushroom_outline.svg"
        :style="{ 'transform': `scale(2.6) scale(${beadScale})` }"
      />
    </g>
    <g v-if="colorIds[5] >= 0" :transform="`translate(${nodeXs[beads[colorIds[5]]]},${nodeYs[beads[colorIds[5]]]})`">
      <image x="-4" y="-4" width="8" height="8"
        href="../assets/flower_outline.svg"
        :style="{ 'transform': `scale(2.5) scale(${beadScale})` }"
      />
    </g>
    <g
      v-for="(node, id) in beads"
      :transform="`translate(${nodeXs[node]},${nodeYs[node]})`"
    >
      <use v-if="node == id + 1" href="#check"/>
    </g>
    <g :transform="`translate(${nodeXs[0]},${nodeYs[0]})`">
      <use v-if="won" href="#check"/>
    </g>
  </svg>
</template>

<style scoped>
.smallView {
  width: 100%;
  height: 100%;
}
.edge {
  fill: none;
  stroke: var(--color-text);
  stroke-width: 2.5;
  stroke-linecap: round;
}
.blackground
{
  fill: black;
  stroke: var(--color-text);
  stroke-width: 0.5;
  stroke-opacity: 0.25;
}
</style>
