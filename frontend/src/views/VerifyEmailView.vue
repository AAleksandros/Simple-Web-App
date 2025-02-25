<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import api from "../api";

const email = ref("");
const verificationCode = ref("");
const successMessage = ref("");
const errorMessage = ref("");
const router = useRouter();

// Separate loading states for each action
const loadingVerify = ref(false);
const loadingResend = ref(false);

// Cooldown state for resend button
const cooldownActive = ref(false);
const cooldownSeconds = ref(60);

onMounted(() => {
  email.value = localStorage.getItem("pending_verification_email") || "";
});

// Verify email function
const verifyEmail = async () => {
  loadingVerify.value = true;
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
    console.error("Verification error:", error.response);
    errorMessage.value = error.response?.data?.error || "Verification failed.";
  } finally {
    loadingVerify.value = false;
  }
};

// Resend verification code function
const resendCode = async () => {
  if (cooldownActive.value) return;

  loadingResend.value = true;
  errorMessage.value = "";
  successMessage.value = "";

  try {
    await api.post("resend-verification/", { email: email.value });
    successMessage.value = "New verification code sent!";
    startCooldown();
  } catch (error: any) {
    console.error("Resend error:", error.response);
    if (error.response && error.response.status === 429) {
      errorMessage.value = "Please wait before requesting another verification code.";
      startCooldown();
    } else {
      errorMessage.value = error.response?.data?.error || "Failed to resend code.";
    }
  } finally {
    loadingResend.value = false;
  }
};

// Start cooldown timer
const startCooldown = () => {
  cooldownActive.value = true;
  cooldownSeconds.value = 60;

  const interval = setInterval(() => {
    cooldownSeconds.value -= 1;
    if (cooldownSeconds.value <= 0) {
      clearInterval(interval);
      cooldownActive.value = false;
    }
  }, 1000);
};
</script>

<template>
  <div class="h-screen flex items-center justify-center px-4 bg-cover bg-center overflow-hidden"
       style="background-image: url('/background.png'); background-attachment: fixed;">
    
    <div class="bg-white/30 backdrop-blur-lg p-8 rounded-lg shadow-lg max-w-md w-full border border-white/20">
      <h1 class="text-center text-2xl font-bold text-white sm:text-3xl">Email Verification</h1>
      <p class="mt-2 text-center text-gray-200">
        We have sent a verification code to: 
        <strong class="text-white">{{ email }}</strong>
      </p>

      <form @submit.prevent="verifyEmail" class="mt-6 space-y-4">
        <!-- Error Message Container -->
        <div v-if="errorMessage" class="w-full text-center mt-2 bg-black/60 backdrop-blur-md px-4 py-2 rounded">
          <p class="text-red-500 text-s">{{ errorMessage }}</p>
        </div>
        <!-- Success Message Container -->
        <div v-if="successMessage" class="w-full text-center mt-2 bg-black/60 backdrop-blur-md px-4 py-2 rounded">
          <p class="text-green-400 text-s">{{ successMessage }}</p>
        </div>

        <div>
          <label for="verificationCode" class="sr-only">Enter Verification Code</label>
          <input
            id="verificationCode"
            type="text"
            v-model="verificationCode"
            placeholder="Enter Verification Code"
            class="w-full rounded-lg border-gray-300 p-3 text-sm bg-white/80 text-black"
            required
          />
        </div>

        <button
          type="submit"
          :disabled="loadingVerify"
          class="w-full rounded-lg bg-green-600 px-5 py-3 text-s font-medium text-white hover:bg-green-700 transition disabled:bg-gray-500"
        >
          {{ loadingVerify ? "Verifying..." : "Verify Email" }}
        </button>

        <button
          type="button"
          @click="resendCode"
          :disabled="loadingResend || cooldownActive"
          class="w-full rounded-lg bg-yellow-500 px-5 py-3 text-sm font-medium text-white hover:bg-yellow-600 transition disabled:bg-gray-500"
        >
          {{ cooldownActive ? `Wait ${cooldownSeconds}s` : (loadingResend ? "Sending..." : "Resend Code") }}
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
  outline: none;
  border-color: #ffffff;
  box-shadow: 0 0 0 2px #525252;
}

button {
  transition: background 0.3s ease-in-out;
}
</style>