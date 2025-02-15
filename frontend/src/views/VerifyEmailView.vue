<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import api from "../api";

const email = ref("");
const verificationCode = ref("");
const loading = ref(false);
const successMessage = ref("");
const errorMessage = ref("");
const router = useRouter();

// Retrieve stored email from localStorage
onMounted(() => {
  email.value = localStorage.getItem("pending_verification_email") || "";
});

// Verify email function
const verifyEmail = async () => {
  loading.value = true;
  successMessage.value = "";
  errorMessage.value = "";

  try {
    await api.post("verify-email/", {
      email: email.value,
      code: verificationCode.value,
    });

    successMessage.value = "Email verified successfully! Redirecting...";
    
    // Clear stored email & Redirect to login
    localStorage.removeItem("pending_verification_email");
    setTimeout(() => router.push("/login"), 2000);
  } catch (error: any) {
    errorMessage.value = error.response?.data?.error || "Verification failed.";
  } finally {
    loading.value = false;
  }
};

// Resend verification code function
const resendCode = async () => {
  loading.value = true;
  errorMessage.value = "";
  successMessage.value = "";

  try {
    await api.post("request-verification/", { email: email.value });
    successMessage.value = "New verification code sent!";
  } catch (error: any) {
    errorMessage.value = error.response?.data?.error || "Failed to resend code.";
  } finally {
    loading.value = false;
  }
};
</script>

<template>
  <div class="auth-container">
    <h2>Email Verification</h2>
    <p>We have sent a verification code to: <strong>{{ email }}</strong></p>

    <form @submit.prevent="verifyEmail">
      <input type="text" v-model="verificationCode" placeholder="Enter Verification Code" required />
      <button type="submit" :disabled="loading">
        {{ loading ? "Verifying..." : "Verify Email" }}
      </button>
    </form>

    <button @click="resendCode" :disabled="loading" class="resend-button">
      Resend Code
    </button>

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

.resend-button {
  background-color: #f39c12;
  margin-top: 10px;
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