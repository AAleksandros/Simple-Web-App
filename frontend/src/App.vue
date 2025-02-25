<script setup lang="ts">
import { useRoute } from "vue-router";
import NavBar from "./components/NavBar.vue";
import { RouterView, RouterLink } from "vue-router";

const route = useRoute();

// Paths where navbar is hidden
const hideNavbarPaths = ["/login", "/register", "/", "/forgot-password", "/reset-password", "/verify-email"];
</script>

<template>
  <div class="min-h-screen bg-no-repeat bg-cover bg-center"
       style="background-image: url('/background.png'); background-attachment: fixed;">
    
    <!-- Show Navbar unless it's in a hidden view -->
    <NavBar v-if="!hideNavbarPaths.includes(route.path)" />

    <!-- Show Home Button when Navbar is hidden -->
    <RouterLink 
      v-if="hideNavbarPaths.includes(route.path)" 
      to="/"
      class="home-btn fixed top-4 left-4 z-50"
    >
      Home
    </RouterLink>
    <RouterView />
  </div>
</template>

<style scoped>
.home-btn {
  background: black;
  color: white;
  text-decoration: none;
  padding: 8px 14px;
  font-size: 0.9rem;
  font-weight: 500;
  border-radius: 6px;
  transition: background 0.3s ease-in-out, transform 0.2s ease-in-out;
}

.home-btn:hover {
  background: rgb(45, 45, 45);
}
</style>