<script setup lang="ts">
import { useAuthStore } from "../stores/auth";
import { computed } from "vue";
import { useRouter } from "vue-router";

const authStore = useAuthStore();
const router = useRouter();

const isAuthenticated = computed(() => authStore.isAuthenticated);
const isAdmin = computed(() => authStore.user?.is_staff === true);

const logout = () => {
  authStore.logout();
  router.push("/");
  setTimeout(() => window.location.reload(), 500);
};
</script>

<template>
  <div class="fixed top-4 right-4 flex gap-3 z-50">
    <!-- Home Button -->
    <RouterLink to="/" class="nav-btn fixed top-4 left-4 z-50">Home</RouterLink>

    <!-- Show these when NOT logged in -->
    <RouterLink v-if="!isAuthenticated" to="/register" class="nav-btn">Register</RouterLink>
    <RouterLink v-if="!isAuthenticated" to="/login" class="nav-btn">Login</RouterLink>

    <!-- Show these when logged in -->
    <RouterLink v-if="isAuthenticated" to="/dashboard" class="nav-btn">Dashboard</RouterLink>
    <RouterLink v-if="isAuthenticated && !isAdmin" to="/profile" class="nav-btn">Profile</RouterLink>
    <RouterLink v-if="isAuthenticated && isAdmin" to="/admin-dashboard" class="nav-btn">Admin Panel</RouterLink>

    <!-- Logout Button -->
    <button v-if="isAuthenticated" @click="logout" class="logout-btn">Logout</button>
  </div>
</template>

<style scoped>
/* Floating Button Style */
.nav-btn {
  background: black;
  color: white;
  text-decoration: none;
  padding: 8px 14px;
  font-size: 0.9rem;
  font-weight: 500;
  border-radius: 6px;
  transition: background 0.3s ease-in-out, transform 0.2s ease-in-out;
}

.nav-btn:hover {
  background: rgb(45, 45, 45);
}

/* Logout Button */
.logout-btn {
  background: #e63946;
  color: white;
  border: none;
  padding: 8px 14px;
  font-size: 0.9rem;
  font-weight: 500;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.3s ease-in-out, transform 0.2s ease-in-out;
}

.logout-btn:hover {
  background: #b71c1c;
}
</style>