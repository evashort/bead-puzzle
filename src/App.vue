<script setup>
import HelloWorld from './components/HelloWorld.vue'
import Game from './components/Game.vue'
</script>

<template>
  <HelloWorld msg="Hello World" />
  <Game :startingBeads="[2, 1, 3, 5, 4]" :edges="[[0, 1], [2, 3], [3, 4], [4, 5], [0, 5], [0, 2], [0, 4], [1, 3], [1, 4], [1, 5]]"/>
</template>

<style>
@import './assets/base.css';

#app {
  text-align: center;
}
</style>
