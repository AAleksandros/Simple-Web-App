<script setup lang="ts">
import { useRouter } from "vue-router";
import { useAuthStore } from "../stores/auth";

const router = useRouter();
const authStore = useAuthStore();

const logout = () => {
  authStore.logout();
  router.push("/");
};
</script>

<template>
  <div class="dashboard-container">
    <h1>Welcome to the Dashboard</h1>
    <p>This is your private area. You are successfully logged in.</p>
    <button class="logout-button" @click="logout">Logout</button>
  </div>
</template>

<style scoped>
.dashboard-container {
  text-align: center;
  padding: 2rem;
}

.logout-button {
  background-color: #e74c3c;
  color: white;
  padding: 10px 20px;
  font-size: 16px;
  cursor: pointer;
  border: none;
  border-radius: 5px;
  margin-top: 20px;
}

.logout-button:hover {
  background-color: #c0392b;
}
</style>