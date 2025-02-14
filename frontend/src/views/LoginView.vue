<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";
import api from "../api";
import { useAuthStore } from "../stores/auth";
import axios from "axios";

const email = ref("");
const password = ref("");
const errorMessage = ref("");
const authStore = useAuthStore();
const router = useRouter();

const login = async () => {
  try {
    const response = await api.post("login/", { email: email.value, password: password.value });
    authStore.login(response.data.access);
    localStorage.setItem("access_token", response.data.access);

    router.push("/dashboard"); 
  } catch (err) {
    if (axios.isAxiosError(err)) {
      errorMessage.value = err.response?.data?.error || "Login failed.";
    } else {
      errorMessage.value = "An unexpected error occurred.";
    }
  }
};
</script>

<template>
  <div class="auth-container">
    <h2>Login</h2>
    <form @submit.prevent="login">
      <input type="email" v-model="email" placeholder="Email" required />
      <input type="password" v-model="password" placeholder="Password" required />
      <button type="submit">Login</button>
    </form>
    <p v-if="errorMessage" class="error">{{ errorMessage }}</p>
  </div>
</template>

<style scoped>
.auth-container {
  max-width: 400px;
  margin: 0 auto;
  padding: 2rem;
  background: #fff;
  border-radius: 10px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  text-align: center;
}

h2 {
  font-size: 24px;
  margin-bottom: 20px;
}

form {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

input {
  padding: 10px;
  font-size: 16px;
  border: 1px solid #ddd;
  border-radius: 5px;
}

button {
  background-color: #42b883;
  color: white;
  padding: 10px;
  font-size: 16px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}

button:hover {
  background-color: #2c9a6a;
}

.error {
  color: red;
  margin-top: 10px;
}
</style>