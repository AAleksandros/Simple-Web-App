<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import api from "../api";

const route = useRoute();
const router = useRouter();

const token = ref("");
const newPassword = ref("");
const confirmPassword = ref("");
const loading = ref(false);
const checkingToken = ref(true);
const tokenValid = ref(false);
const successMessage = ref("");
const errorMessage = ref("");

// Inline password validation
const isPasswordValid = ref(false);
const passwordsMatch = ref(false);

// Validate token before showing the form
onMounted(async () => {
  token.value = (route.query.token as string) || "";
  
  if (!token.value) {
    errorMessage.value = "Invalid or missing reset token.";
    checkingToken.value = false;
    return;
  }

  try {
    // Validate token with backend API before showing form
    await api.post("validate-reset-token/", { token: token.value });
    tokenValid.value = true;
  } catch (error: any) {
    console.error("Token validation error:", error.response);
    errorMessage.value = "This reset link is invalid or has expired.";
  } finally {
    checkingToken.value = false;
  }
});

// Check password validity
const checkPasswordStrength = () => {
  isPasswordValid.value =
    newPassword.value.length >= 8 &&
    /[A-Z]/.test(newPassword.value) &&
    /[a-z]/.test(newPassword.value) &&
    /\d/.test(newPassword.value) &&
    /[!@#$%^&*(),.?":{}|<>]/.test(newPassword.value);
};

// Ensure passwords match
const checkPasswordsMatch = () => {
  passwordsMatch.value = newPassword.value === confirmPassword.value;
};

// Reset password function
const resetPassword = async () => {
  if (!tokenValid.value) {
    errorMessage.value = "Invalid or expired reset token.";
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
  <div class="h-screen flex items-center justify-center px-4 bg-cover bg-center overflow-hidden"
       style="background-image: url('/background.png'); background-attachment: fixed;">
    
    <div class="bg-white/30 backdrop-blur-lg p-8 rounded-lg shadow-lg max-w-md w-full border border-white/20">
      <h1 class="text-center text-2xl font-bold text-white sm:text-3xl">Reset Password</h1>

      <!-- Conditionally show or hide instructions based on token validity -->
      <p v-if="tokenValid" class="text-center text-gray-200 mt-2">Enter your new password below.</p>

      <!-- Show Loading while checking the token -->
      <p v-if="checkingToken" class="text-center text-gray-300 text-sm mt-4">Checking reset token...</p>

      <!-- Show error if token is invalid -->
      <div v-if="!checkingToken && !tokenValid" class="text-center">
        <p class="text-red-400 text-sm mt-4">This reset link is invalid or has expired.</p>
        <button 
          @click="router.push('/forgot-password')" 
          class="mt-4 px-5 py-2 rounded-lg bg-yellow-500 text-white hover:bg-yellow-600 transition">
          Request New Reset Link
        </button>
      </div>

      <!-- Show form only if token is valid -->
      <form v-if="tokenValid" @submit.prevent="resetPassword" class="mt-6 space-y-4">
        <p v-if="errorMessage" class="text-center text-red-400 text-sm">{{ errorMessage }}</p>
        <p v-if="successMessage" class="text-center text-green-400 text-sm">{{ successMessage }}</p>

        <div>
          <label for="newPassword" class="sr-only">New Password</label>
          <input
            id="newPassword"
            type="password"
            v-model="newPassword"
            @input="checkPasswordStrength"
            placeholder="New Password"
            class="w-full rounded-lg border-gray-300 p-3 text-sm bg-white/80 text-black"
            required
          />
          <!-- Password Hint (Restored) -->
          <p class="text-gray-300 text-xs mt-1">
            Password must be at least <strong>8 characters</strong> long, 
            contain <strong>uppercase</strong> & <strong>lowercase</strong> letters, 
            a <strong>number</strong>, and a <strong>special character</strong>.
          </p>
        </div>

        <div>
          <label for="confirmPassword" class="sr-only">Confirm Password</label>
          <input
            id="confirmPassword"
            type="password"
            v-model="confirmPassword"
            @input="checkPasswordsMatch"
            placeholder="Confirm Password"
            class="w-full rounded-lg border-gray-300 p-3 text-sm bg-white/80 text-black"
            required
          />
        </div>

        <p class="text-red-400 text-xs" v-if="newPassword && confirmPassword && !passwordsMatch">
          Passwords do not match.
        </p>

        <button
          type="submit"
          :disabled="loading || !passwordsMatch || !isPasswordValid"
          class="w-full rounded-lg bg-green-500 px-5 py-3 text-sm font-medium text-white hover:bg-green-600 transition disabled:bg-gray-500"
        >
          {{ loading ? "Resetting..." : "Reset Password" }}
        </button>
      </form>
    </div>
  </div>
</template>

<style scoped>
/* Improved consistency with theme */
input {
  outline: none;
  transition: border 0.3s ease-in-out;
}

input:focus {
  border-color: #42b883;
}

button {
  transition: background 0.3s ease-in-out;
}
</style>