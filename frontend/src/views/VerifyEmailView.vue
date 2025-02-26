<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import api from "../api";

const email = ref("");
const verificationCode = ref("");
const successMessage = ref("");
const errorMessage = ref("");
const router = useRouter();

// Loading states
const loadingVerify = ref(false);
const loadingResend = ref(false);

// Cooldown state
const cooldownActive = ref(false);
const cooldownSeconds = ref(60);

onMounted(async () => {
  email.value = localStorage.getItem("pending_verification_email") || "";

  const storedCooldown = localStorage.getItem("resend_cooldown_timestamp");
  const emailLastSent = localStorage.getItem("email_last_sent");
  const currentTime = Date.now();

  if (storedCooldown) {
    const cooldownEndTime = parseInt(storedCooldown, 10);
    if (cooldownEndTime > currentTime) {
      const remainingTime = Math.ceil((cooldownEndTime - currentTime) / 1000);
      startCooldown(remainingTime);
      return;
    }
    localStorage.removeItem("resend_cooldown_timestamp");
  }

  if (emailLastSent && currentTime - parseInt(emailLastSent) < 60000) {
    console.log("Email recently sent. Skipping auto-resend.");
    return;
  }

  await resendCode();
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
    
    // Clear stored email & cooldown timestamp
    localStorage.removeItem("pending_verification_email");
    localStorage.removeItem("resend_cooldown_timestamp");

    setTimeout(() => router.push("/login"), 2000);
  } catch (error: any) {
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
    const cooldownDuration = 60 * 1000;
    const cooldownExpiresAt = Date.now() + cooldownDuration;
    localStorage.setItem("resend_cooldown_timestamp", cooldownExpiresAt.toString());

    startCooldown(60);
  } catch (error: any) {
    if (error.response && error.response.status === 429) {
      errorMessage.value = "Please wait before requesting another verification code.";

      const retryAfter = parseInt(error.response.headers["retry-after"], 10) || 60;
      const cooldownExpiresAt = Date.now() + retryAfter * 1000;
      localStorage.setItem("resend_cooldown_timestamp", cooldownExpiresAt.toString());

      startCooldown(retryAfter);
    } else {
      errorMessage.value = error.response?.data?.error || "Failed to resend code.";
    }
  } finally {
    loadingResend.value = false;
  }
};

const startCooldown = (duration: number) => {
  cooldownActive.value = true;
  cooldownSeconds.value = duration;

  const interval = setInterval(() => {
    cooldownSeconds.value -= 1;
    if (cooldownSeconds.value <= 0) {
      clearInterval(interval);
      cooldownActive.value = false;
      localStorage.removeItem("resend_cooldown_timestamp");
    }
  }, 1000);
};
</script>

<template>
  <div class="pt-30 pb-30 flex items-center justify-center px-4 bg-cover bg-center overflow-y-auto"
       style="background-image: url('/background.png'); background-attachment: fixed;">
    
    <div class="bg-white/30 backdrop-blur-lg p-8 rounded-lg shadow-lg max-w-md w-full border border-white/20">
      <h1 class="text-center text-2xl font-bold text-white sm:text-3xl">Email Verification</h1>
      <p class="mt-2 text-center text-gray-200">
        We have sent a verification code to: 
        <strong class="text-white">{{ email }}</strong>
      </p>

      <form @submit.prevent="verifyEmail" class="mt-6 space-y-4">
        <div v-if="errorMessage" class="w-full text-center mt-2 bg-black/60 backdrop-blur-md px-4 py-2 rounded">
          <p class="text-red-500 text-s">{{ errorMessage }}</p>
        </div>
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