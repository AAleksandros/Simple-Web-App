<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";
import api from "../api";

const email = ref("");
const password = ref("");
const confirmPassword = ref("");
const loading = ref(false);
const successMessage = ref("");
const errorMessage = ref("");
const router = useRouter();

const register = async () => {
  successMessage.value = "";
  errorMessage.value = "";

  if (!email.value || !password.value || !confirmPassword.value) {
    errorMessage.value = "Email, password, and confirmation are required.";
    return;
  }

  if (password.value !== confirmPassword.value) {
    errorMessage.value = "Passwords do not match.";
    return;
  }

  loading.value = true;

  try {
    await api.post("register/", {
      email: email.value,
      password: password.value,
      confirm_password: confirmPassword.value,
    });

    localStorage.setItem("pending_verification_email", email.value);
    successMessage.value = "Registration successful! Check your email for a verification code.\nMake sure to check your spam folder!";

    setTimeout(() => router.push("/verify-email"), 2000);
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
      <div class="input-group">
        <label for="email">Email</label>
        <input id="email" type="email" v-model="email" required />
      </div>

      <div class="input-group">
        <label for="password">Password</label>
        <input id="password" type="password" v-model="password" required />
      </div>

      <!-- Password Hint -->
      <p class="password-hint" v-if="password">
        Password must be at least 8 characters, contain uppercase & lowercase letters, a number, and a special character.
      </p>

      <div class="input-group">
        <label for="confirmPassword">Confirm Password</label>
        <input id="confirmPassword" type="password" v-model="confirmPassword" required />
      </div>

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

/* Password hint styling */
.password-hint {
  font-size: 14px;
  color: #666;
  margin-top: -10px;
  margin-bottom: 10px;
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