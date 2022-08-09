<script setup>
import HelloWorld from './components/HelloWorld.vue'
import Game from './components/Game.vue'
</script>

<template>
  <HelloWorld msg="Hello World" />
  <Game :startingBeads="[1, 2, 0, 5, 4]" :edges="[[0, 1],[0, 2],[0, 5],[1, 2],[1, 3],[2, 3],[3, 4],[4, 5]]" :baseDustDuration="360" :dustCount="18"/>
</template>

<style>
@import './assets/base.css';

#app {
  text-align: center;
}
</style>
