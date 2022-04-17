<script setup>
import HelloWorld from './components/HelloWorld.vue'
import Game from './components/Game.vue'
</script>

<template>
  <HelloWorld msg="Hello World" />
  <Game :startingBeads="[0, 3, 2, 1]" :edges="[[0, 1], [0, 2], [0, 3], [1, 2], [2, 3]]"/>
</template>

<style>
@import './assets/base.css';

#app {
  text-align: center;
}
</style>
