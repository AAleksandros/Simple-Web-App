<script setup lang="ts">
import { useAuthStore } from "../stores/auth.ts";
import { useRouter } from "vue-router";

const authStore = useAuthStore();
const router = useRouter();

const logout = () => {
  authStore.logout();
  router.push("/login");
  setTimeout(() => window.location.reload(), 500);
};
</script>

<template>
  <nav class="navbar">
    <h1 class="logo">MyApp</h1>
    <div class="nav-links">
      <RouterLink to="/">Home</RouterLink>
      <RouterLink v-if="!authStore.isAuthenticated" to="/register">Register</RouterLink>
      <RouterLink v-if="!authStore.isAuthenticated" to="/login">Login</RouterLink>
      <button v-if="authStore.isAuthenticated" @click="logout" class="logout-btn">
        Logout
      </button>
    </div>
  </nav>
</template>

<style scoped>
.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #1e1e1e;
  padding: 1rem 2rem;
  color: white;
}

.logo {
  font-size: 1.5rem;
  font-weight: bold;
}

.nav-links {
  display: flex;
  gap: 1rem;
}

.nav-links a {
  text-decoration: none;
  color: white;
}

.logout-btn {
  background: #e63946;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  cursor: pointer;
  font-size: 1rem;
  border-radius: 5px;
}

.logout-btn:hover {
  background: #b71c1c;
}
</style>