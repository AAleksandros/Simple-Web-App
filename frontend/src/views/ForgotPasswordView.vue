<script setup lang="ts">
import { ref, onMounted } from "vue";
import api from "../api";

const email = ref("");
const loading = ref(false);
const successMessage = ref("");
const errorMessage = ref("");
const cooldownActive = ref(false);
const cooldownSeconds = ref(0);

const RATE_LIMIT_MS = 60 * 1000; // 60 seconds per email
const FAKE_WAIT_MS = 2000; // 2 seconds delay

// Retrieve & resume cooldown from localStorage
onMounted(() => {
  const lastRequestTime = localStorage.getItem("last_reset_request");
  const storedCooldown = localStorage.getItem("reset_cooldown_seconds");

  if (lastRequestTime && storedCooldown) {
    const elapsed = (Date.now() - Number(lastRequestTime)) / 1000;
    const remainingCooldown = Math.max(Number(storedCooldown) - elapsed, 0);

    if (remainingCooldown > 0) {
      cooldownSeconds.value = Math.ceil(remainingCooldown);
      startCooldown();
    }
  }
});

// Start cooldown timer
const startCooldown = () => {
  cooldownActive.value = true;
  const interval = setInterval(() => {
    cooldownSeconds.value -= 1;
    if (cooldownSeconds.value <= 0) {
      clearInterval(interval);
      cooldownActive.value = false;
      localStorage.removeItem("reset_cooldown_seconds");
    }
  }, 1000);
};

const requestPasswordReset = async () => {
  if (cooldownActive.value) return;

  loading.value = true;
  successMessage.value = "";
  errorMessage.value = "";

  try {
    await api.post("forgot-password/", { email: email.value });

    // Set cooldown to 60 seconds (default)
    cooldownSeconds.value = 60;
    localStorage.setItem("last_reset_request", Date.now().toString());
    localStorage.setItem("reset_cooldown_seconds", cooldownSeconds.value.toString());

    successMessage.value = "If this email exists, a reset link has been sent.\nMake sure to check your spam folder!";
    startCooldown();
    loading.value = false;
  } catch (error: any) {
    if (error.response?.status === 429) {
      const retryAfter = Number(error.response.headers["retry-after"]);
      cooldownSeconds.value = retryAfter > 0 ? retryAfter : 60;

      localStorage.setItem("last_reset_request", Date.now().toString());
      localStorage.setItem("reset_cooldown_seconds", cooldownSeconds.value.toString());

      errorMessage.value = "Please wait before requesting another reset link.";
      startCooldown();
      loading.value = false;
    } else if (error.response?.status === 404) {
      // Delay before showing success message for 404 to hide email existence
      setTimeout(() => {
        successMessage.value = "If this email exists, a reset link has been sent.\nMake sure to check your spam folder!";
        cooldownSeconds.value = 60;
        localStorage.setItem("last_reset_request", Date.now().toString());
        localStorage.setItem("reset_cooldown_seconds", cooldownSeconds.value.toString());
        startCooldown();
        loading.value = false;
      }, FAKE_WAIT_MS);
      // Do not set loading.value to false immediately
    } else {
      errorMessage.value = error.response?.data?.error || "An unexpected error occurred.";
      loading.value = false;
    }
  }
};
</script>

<template>
  <div class="flex items-center justify-center min-h-screen bg-cover bg-center" 
       style="background-image: url('/background.png');">
    
    <div class="bg-white/30 backdrop-blur-md shadow-lg rounded-lg p-8 max-w-md w-full text-center border border-white/20">
      <h2 class="text-3xl font-bold text-white drop-shadow-lg">Forgot Password?</h2>
      <p class="text-gray-200 mt-2">Enter your email to receive a password reset link.</p>

      <form @submit.prevent="requestPasswordReset" class="mt-6 space-y-4">
        <div>
          <label for="email" class="sr-only">Email</label>
          <input
            id="email"
            type="email"
            v-model="email"
            required
            placeholder="Enter your email"
            class="w-full rounded-lg border-gray-300 p-3 text-sm bg-white/70"
          />
        </div>

        <button 
          type="submit"
          :disabled="loading || cooldownActive"
          class="w-full rounded-lg bg-blue-500 px-5 py-3 text-sm font-medium text-white transition hover:bg-blue-600 disabled:bg-gray-500"
        >
          {{ cooldownActive ? `Wait ${cooldownSeconds}s` : (loading ? "Sending..." : "Send Reset Link") }}
        </button>

        <!-- Success Message Container -->
        <div v-if="successMessage" class="w-full text-center mt-2 bg-black/60 backdrop-blur-md px-4 py-2 rounded">
          <p class="text-green-400 text-s whitespace-pre-line">{{ successMessage }}</p>
        </div>
        <!-- Error Message Container -->
        <div v-if="errorMessage" class="w-full text-center mt-2 bg-black/60 backdrop-blur-md px-4 py-2 rounded">
          <p class="text-red-800 text-s">{{ errorMessage }}</p>
        </div>
      </form>
    </div>
  </div>
</template>

<style scoped>
input {
  outline: none;
  transition: border 0.3s ease-in-out;
}

input:focus {
  outline: none;
  border-color: #ffffff;
  box-shadow: 0 0 0 2px #525252;
}
</style>