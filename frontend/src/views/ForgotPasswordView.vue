<script setup lang="ts">
import { ref } from "vue";
import api from "../api";

const email = ref("");
const loading = ref(false);
const successMessage = ref("");
const errorMessage = ref("");

const RATE_LIMIT_MS = 0 * 60 * 1000; // 5 minutes
const FAKE_WAIT_MS = 2000; // 2 seconds delay

const requestPasswordReset = async () => {
  successMessage.value = "";
  errorMessage.value = "";

  const lastRequestTime = localStorage.getItem("last_reset_request");
  const now = Date.now();

  // Prevent spam by checking time difference
  if (lastRequestTime && now - Number(lastRequestTime) < RATE_LIMIT_MS) {
    errorMessage.value = "Please wait before requesting another reset link.";
    return;
  }

  loading.value = true;

  try {
    const response = await api.post("forgot-password/", { email: email.value });

    localStorage.setItem("last_reset_request", now.toString());

    successMessage.value = "If this email exists, a reset link has been sent. \nMake sure to check your spam folder!";
  } catch (error: any) {
    if (error.response?.status === 404) {
      setTimeout(() => {
        successMessage.value = "If this email exists, a reset link has been sent. \nMake sure to check your spam folder!";
      }, FAKE_WAIT_MS);
    } else {
      errorMessage.value = error.response?.data?.error || "An unexpected error occurred.";
    }
  } finally {
    setTimeout(() => {
      loading.value = false;
    }, FAKE_WAIT_MS);
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
  white-space: pre-line;
}

.error {
  color: red;
  margin-top: 10px;
}
</style>