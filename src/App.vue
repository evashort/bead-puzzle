<script setup>
import HelloWorld from './components/HelloWorld.vue'
import Game from './components/Game.vue'
</script>

<template>
  <HelloWorld msg="Hello World" />
  <Game :startingBeads="[2, 1, 3, 5, 4]" :edges="[[0, 1], [0, 2], [0, 4], [0, 5], [1, 3], [2, 3], [3, 4], [3, 5]]" :loops="[[0, 1, 3, 5], [0, 2, 3, 4], [0, 1, 3, 2], [5, 0, 4, 3]]"/>
</template>

<style>
@import './assets/base.css';

#app {
  text-align: center;
}
</style>
