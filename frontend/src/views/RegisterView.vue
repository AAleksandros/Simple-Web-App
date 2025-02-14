<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";
import api from "../api";

const email = ref("");
const password = ref("");
const loading = ref(false);
const successMessage = ref("");
const errorMessage = ref("");
const router = useRouter();

const register = async () => {
  loading.value = true;
  successMessage.value = "";
  errorMessage.value = "";

  try {
    await api.post("register/", {
      email: email.value,
      password: password.value,
    });

    successMessage.value = "Registration successful! Redirecting...";
    setTimeout(() => router.push("/login"), 2000);
  } catch (error: any) {
    errorMessage.value = error.response?.data?.error || "Registration failed.";
  } finally {
    loading.value = false;
  }
};
</script>

<template>
  <div class="auth-container">
    <h2>Register</h2>
    <form @submit.prevent="register">
      <input type="email" v-model="email" placeholder="Email" required />
      <input type="password" v-model="password" placeholder="Password" required />
      <button type="submit" :disabled="loading">
        {{ loading ? "Registering..." : "Register" }}
      </button>
    </form>
    <p v-if="successMessage" class="success">{{ successMessage }}</p>
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

button:disabled {
  background: gray;
}

button:hover {
  background-color: #2c9a6a;
}

.success {
  color: green;
  margin-top: 10px;
}

.error {
  color: red;
  margin-top: 10px;
}
</style>