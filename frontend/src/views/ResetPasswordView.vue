<script setup lang="ts">
import { ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import api from "../api";

const route = useRoute();
const router = useRouter();

const token = ref(route.query.token || "");
const newPassword = ref("");
const confirmPassword = ref("");
const loading = ref(false);
const successMessage = ref("");
const errorMessage = ref("");

const resetPassword = async () => {
  if (newPassword.value !== confirmPassword.value) {
    errorMessage.value = "Passwords do not match.";
    return;
  }

  loading.value = true;
  successMessage.value = "";
  errorMessage.value = "";

  try {
    await api.post("reset-password/", {
      token: token.value,
      new_password: newPassword.value,
    });

    successMessage.value = "Password reset successful! Redirecting to login...";
    setTimeout(() => router.push("/login"), 3000);
  } catch (error: any) {
    errorMessage.value = error.response?.data?.error || "Failed to reset password.";
  } finally {
    loading.value = false;
  }
};
</script>

<template>
  <div class="auth-container">
    <h2>Reset Password</h2>
    <p>Enter your new password below.</p>

    <form @submit.prevent="resetPassword">
      <input type="hidden" v-model="token" />
      <input type="password" v-model="newPassword" placeholder="New Password" required />
      <input type="password" v-model="confirmPassword" placeholder="Confirm Password" required />
      <button type="submit" :disabled="loading">
        {{ loading ? "Resetting..." : "Reset Password" }}
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

input {
  padding: 10px;
  font-size: 16px;
  border: 1px solid #ddd;
  border-radius: 5px;
  text-align: center;
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