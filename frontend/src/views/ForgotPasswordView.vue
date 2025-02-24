<script setup lang="ts">
import { ref, onMounted } from "vue";
import api from "../api";

const email = ref("");
const loading = ref(false);
const successMessage = ref("");
const errorMessage = ref("");
const cooldownActive = ref(false);
const cooldownSeconds = ref(0);

// Retrieve & Resume Cooldown from LocalStorage
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

    // Default cooldown of 5 minutes (300 seconds) if no rate limit provided
    cooldownSeconds.value = 300;
    localStorage.setItem("last_reset_request", Date.now().toString());
    localStorage.setItem("reset_cooldown_seconds", cooldownSeconds.value.toString());

    successMessage.value = "If this email exists, a reset link has been sent. \nMake sure to check your spam folder!";
    startCooldown();
  } catch (error: any) {
    if (error.response?.status === 429) {
      // Read actual cooldown from 'Retry-After' header (if available)
      const retryAfter = Number(error.response.headers["retry-after"]);
      cooldownSeconds.value = retryAfter > 0 ? retryAfter : 300;

      localStorage.setItem("last_reset_request", Date.now().toString());
      localStorage.setItem("reset_cooldown_seconds", cooldownSeconds.value.toString());

      errorMessage.value = "Please wait before requesting another reset link.";
      startCooldown();
    } else {
      errorMessage.value = error.response?.data?.error || "An unexpected error occurred.";
    }
  } finally {
    loading.value = false;
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

        <p v-if="successMessage" class="text-green-400 text-sm whitespace-pre-line">{{ successMessage }}</p>
        <p v-if="errorMessage" class="text-red-800 text-sm">{{ errorMessage }}</p>
      </form>
    </div>
  </div>
</template>