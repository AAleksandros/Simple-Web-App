<template>
  <nav class="navbar">
    <div class="logo">MyApp</div>
    <div class="nav-links">
      <router-link to="/">Home</router-link>
      <template v-if="!authStore.isAuthenticated">
        <router-link to="/register">Register</router-link>
        <router-link to="/login">Login</router-link>
      </template>
      <button v-else class="logout-btn" @click="logout">Logout</button>
    </div>
  </nav>
</template>

<script setup lang="ts">
import { useAuthStore } from "../stores/auth";
import { useRouter } from "vue-router";

const authStore = useAuthStore();
const router = useRouter();

const logout = () => {
  authStore.logout();
  router.push("/");
};
</script>

<style scoped>
.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 20px;
  background: #222;
  color: white;
}

.logo {
  font-size: 24px;
  font-weight: bold;
}

.nav-links {
  display: flex;
  align-items: center;
  gap: 15px;
}

.nav-links a {
  color: white;
  text-decoration: none;
  font-size: 16px;
  transition: color 0.3s ease;
}

.nav-links a:hover {
  color: #42b883;
}

.logout-btn {
  background: #e74c3c;
  color: white;
  padding: 8px 15px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 16px;
}

.logout-btn:hover {
  background: #c0392b;
}
</style>