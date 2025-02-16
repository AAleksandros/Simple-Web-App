<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import api from "../api";

const route = useRoute();
const router = useRouter();

const token = ref("");
const newPassword = ref("");
const confirmPassword = ref("");
const loading = ref(false);
const successMessage = ref("");
const errorMessage = ref("");

onMounted(() => {
  token.value = (route.query.token as string) || "";
  console.log("Extracted token:", token.value);
});

// Inline password validation
const isPasswordValid = computed(() => {
  return (
    newPassword.value.length >= 8 &&
    /[A-Z]/.test(newPassword.value) &&
    /[a-z]/.test(newPassword.value) &&
    /\d/.test(newPassword.value) &&
    /[!@#$%^&*(),.?":{}|<>]/.test(newPassword.value)
  );
});

// Ensure passwords match
const passwordsMatch = computed(() => newPassword.value === confirmPassword.value);

const isButtonDisabled = computed(() => {
  return loading.value || !passwordsMatch.value || !isPasswordValid.value || !token.value;
});

const resetPassword = async () => {
  if (!token.value) {
    errorMessage.value = "Invalid or missing reset token.";
    return;
  }

  if (!passwordsMatch.value) {
    errorMessage.value = "Passwords do not match.";
    return;
  }

  loading.value = true;
  successMessage.value = "";
  errorMessage.value = "";

  try {
    console.log("Sending API request with:", {
      token: token.value,
      new_password: newPassword.value,
      confirm_password: confirmPassword.value,
    });

    await api.post("reset-password/", {
      token: token.value,
      new_password: newPassword.value,
      confirm_password: confirmPassword.value,
    });

    successMessage.value = "Password reset successful! Redirecting...";
    setTimeout(() => router.push("/login"), 3000);
  } catch (error: any) {
    console.error("Reset password error:", error.response);
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

      <div class="input-group">
        <label for="newPassword">New Password</label>
        <input id="newPassword" type="password" v-model="newPassword" required />
      </div>

      <p class="password-hint" v-if="newPassword">
        Password must be at least 8 characters, contain uppercase & lowercase letters, a number, and a special character.
      </p>

      <div class="input-group">
        <label for="confirmPassword">Confirm Password</label>
        <input id="confirmPassword" type="password" v-model="confirmPassword" required />
      </div>

      <p class="error" v-if="newPassword && confirmPassword && !passwordsMatch">
        ❌ Passwords do not match.
      </p>

      <button type="submit" :disabled="isButtonDisabled">
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
  cursor: not-allowed;
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

.password-hint {
  font-size: 14px;
  color: #666;
}
</style>