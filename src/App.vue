<script setup>
import Switcher from './components/Switcher.vue';
</script>

<template>
  <div style="display: flex; justify-content: space-between; align-items: center;">
    <button style="height: 5rem">Settings</button>
    1 ▶️ Moving
    <button style="height: 5rem">Menu</button>
  </div>
  <div style="height: calc(100vh - 5rem);">
    <Switcher headerHeight="5rem"/>
  </div>
</template>

<style>
@import './assets/base.css';
</style>
