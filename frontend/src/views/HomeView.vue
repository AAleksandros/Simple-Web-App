<script setup lang="ts">
import { useRouter } from "vue-router";

const router = useRouter();

const goToRegister = () => {
  router.push("/register");
};

const goToLogin = () => {
  router.push("/login");
};
</script>

<template>
  <div class="home-container">
    <h1>Welcome to MyApp</h1>
    <p>This is a simple authentication system using Django and Vue.js.</p>
    <div class="buttons">
      <button @click="goToRegister">Register</button>
      <button @click="goToLogin">Login</button>
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
</style>