<script setup>
import { RouterView } from 'vue-router'
</script>

<template>
  <!--  <div id="app">-->
  <v-app> <!-- Automatically add id=app to the div -->

    <!-- This is where routed views will be injected -->
    <router-view></router-view>


  </v-app>
  <!--  </div>-->
</template>
