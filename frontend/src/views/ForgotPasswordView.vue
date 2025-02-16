<script setup lang="ts">
import { ref } from "vue";
import api from "../api";

const email = ref("");
const loading = ref(false);
const successMessage = ref("");
const errorMessage = ref("");

const requestPasswordReset = async () => {
  loading.value = true;
  successMessage.value = "";
  errorMessage.value = "";

  try {
    await api.post("forgot-password/", { email: email.value });

    successMessage.value = "If this email exists, a reset link has been sent.";
  } catch (error: any) {
    errorMessage.value = error.response?.data?.error || "Failed to request reset.";
  } finally {
    loading.value = false;
  }
};
</script>

<template>
  <div class="auth-container">
    <h2>Forgot Password</h2>
    <p>Enter your email to receive a password reset link.</p>

    <form @submit.prevent="requestPasswordReset">
      <div class="input-group">
        <label for="email">Email</label>
        <input id="email" type="email" v-model="email" required />
      </div>

      <button type="submit" :disabled="loading">
        {{ loading ? "Sending..." : "Send Reset Link" }}
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
  margin-bottom: 10px;
}

p {
  font-size: 16px;
  margin-bottom: 15px;
}

form {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.input-group {
  display: flex;
  flex-direction: column;
  text-align: left;
}

label {
  font-size: 14px;
  font-weight: bold;
  margin-bottom: 5px;
  color: #333;
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