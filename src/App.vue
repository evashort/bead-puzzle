<script setup>
import HelloWorld from './components/HelloWorld.vue'
import Game from './components/Game.vue'
</script>

<template>
  <HelloWorld msg="Hello World" />
  <Game :startingBeads="[0, 3, 2, 1]" />
</template>

<style>
@import './assets/base.css';

#app {
  text-align: center;
}
</style>
