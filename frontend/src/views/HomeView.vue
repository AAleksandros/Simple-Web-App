<script setup lang="ts">
import { useRouter } from "vue-router";
import { useAuthStore } from "../stores/auth";

const router = useRouter();
const authStore = useAuthStore();

const goToRegister = () => {
  router.push("/register");
};

const goToLogin = () => {
  router.push("/login");
};

const goToDashboard = () => {
  router.push("/dashboard");
};
</script>

<template>
  <div class="home-container">
    <h1>Welcome to my Web App</h1>
    <p>This is a simple authentication system using Django and Vue.js.</p>

    <div class="buttons">
      <!-- Show Register/Login if NOT authenticated -->
      <template v-if="!authStore.isAuthenticated">
        <button @click="goToRegister">Register</button>
        <button @click="goToLogin">Login</button>
      </template>

      <!-- Show Dashboard button if already logged in -->
      <template v-else>
        <button class="dashboard-button" @click="goToDashboard">Go to Dashboard</button>
      </template>
    </div>
  </div>
</template>

<style scoped>
.home-container {
  text-align: center;
  padding: 2rem;
}

.buttons {
  margin-top: 20px;
}

button {
  margin: 10px;
  padding: 10px 20px;
  font-size: 16px;
  cursor: pointer;
  border: none;
  background-color: #42b883;
  color: white;
  border-radius: 5px;
}

button:hover {
  background-color: #2c9a6a;
}

/* Dashboard Button Styling */
.dashboard-button {
  background-color: #3498db;
}

.dashboard-button:hover {
  background-color: #2980b9;
}
</style>