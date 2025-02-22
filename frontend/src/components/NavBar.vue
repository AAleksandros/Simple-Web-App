<script setup lang="ts">
import { useAuthStore } from "../stores/auth";
import { computed } from "vue";
import { useRouter } from "vue-router";

const authStore = useAuthStore();
const router = useRouter();

const isAuthenticated = computed(() => authStore.isAuthenticated);
const isAdmin = computed(() => authStore.user?.is_staff === true); // Checks admin status

const logout = () => {
  authStore.logout();
  router.push("/");
  setTimeout(() => window.location.reload(), 500); // Ensures a full logout reset
};
</script>

<template>
  <nav class="navbar">
    <RouterLink to="/" class="logo">MyApp</RouterLink>
    <div class="nav-links">
      <RouterLink v-if="!isAuthenticated" to="/register">Register</RouterLink>
      <RouterLink v-if="!isAuthenticated" to="/login">Login</RouterLink>
      <RouterLink v-if="isAuthenticated" to="/dashboard">Dashboard</RouterLink>
      <RouterLink v-if="isAuthenticated && isAdmin" to="/admin-dashboard">Admin Panel</RouterLink>
      <button v-if="isAuthenticated" @click="logout" class="logout-btn">Logout</button>
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
  text-decoration: none;
  color: white;
  transition: color 0.3s ease-in-out;
}

.logo:hover {
  color: #42b883;
}

.nav-links {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.nav-links a {
  text-decoration: none;
  color: white;
  font-size: 1rem;
  transition: color 0.3s ease-in-out;
}

.nav-links a:hover {
  color: #42b883;
}

.logout-btn {
  background: #e63946;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  cursor: pointer;
  font-size: 1rem;
  border-radius: 5px;
  transition: background 0.3s ease-in-out;
}

.logout-btn:hover {
  background: #b71c1c;
}
</style>