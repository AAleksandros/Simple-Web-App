<script setup lang="ts">
import { useRoute, useRouter } from "vue-router";
import NavBar from "./components/NavBar.vue";
import { RouterView } from "vue-router";

const route = useRoute();
const router = useRouter();

// Define paths where we want to hide the navbar
const hideNavbarPaths = ["/login", "/register", "/", "/forgot-password", "/verify-email"];

// Function to navigate home
const goHome = () => {
  router.push("/");
};
</script>

<template>
  <div class="min-h-screen bg-no-repeat bg-cover bg-center"
       style="background-image: url('/background.png'); background-attachment: fixed;">
    
    <!-- Show Navbar unless it's in a hidden view -->
    <NavBar v-if="!hideNavbarPaths.includes(route.path)" />

    <!-- Show Home Button when Navbar is hidden -->
    <button 
      v-if="hideNavbarPaths.includes(route.path)" 
      @click="goHome"
      class="absolute top-4 left-4 px-4 py-2 text-white bg-black/50 backdrop-blur-md rounded-lg shadow-md hover:bg-black/70 transition"
    >
      Home
    </button>

    <!-- Render the page -->
    <RouterView />
  </div>
</template>

<style>
/* Ensure the button does not interfere with other components */
html, body {
  margin: 0;
  padding: 0;
  height: 100%;
}
</style>