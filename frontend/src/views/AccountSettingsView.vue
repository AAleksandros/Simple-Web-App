<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import api from "../api";

// Change Email
const newEmail = ref("");
const emailChangeMessage = ref("");
const emailChangeError = ref("");
const loadingEmail = ref(false);

const emailCooldownActive = ref(false);
const emailCooldownSeconds = ref(0);

const router = useRouter();

// Resume cooldown from localStorage if it exists
onMounted(() => {
  const lastEmailChangeRequest = localStorage.getItem("last_email_change_request");
  const storedCooldown = localStorage.getItem("email_change_cooldown_seconds");
  if (lastEmailChangeRequest && storedCooldown) {
    const elapsed = (Date.now() - Number(lastEmailChangeRequest)) / 1000;
    const remaining = Math.max(Number(storedCooldown) - elapsed, 0);
    if (remaining > 0) {
      emailCooldownSeconds.value = Math.ceil(remaining);
      startEmailCooldown();
    }
  }
});

const startEmailCooldown = () => {
  emailCooldownActive.value = true;
  const interval = setInterval(() => {
    emailCooldownSeconds.value -= 1;
    if (emailCooldownSeconds.value <= 0) {
      clearInterval(interval);
      emailCooldownActive.value = false;
      localStorage.removeItem("email_change_cooldown_seconds");
    }
  }, 1000);
};

const changeEmail = async () => {
  if (emailCooldownActive.value) return;

  emailChangeMessage.value = "";
  emailChangeError.value = "";
  loadingEmail.value = true;

  try {
    const response = await api.post("change-email/", { new_email: newEmail.value });
    emailChangeMessage.value = response.data.message;
    // Start cooldown immediately after a successful request
    const retryAfter = Number(response.headers["retry-after"]) || 60;
    emailCooldownSeconds.value = retryAfter;
    localStorage.setItem("last_email_change_request", Date.now().toString());
    localStorage.setItem("email_change_cooldown_seconds", emailCooldownSeconds.value.toString());
    startEmailCooldown();
  } catch (error: any) {
    if (error.response?.status === 429) {
      const retryAfter = Number(error.response.headers["retry-after"]) || 60;
      emailCooldownSeconds.value = retryAfter;
      localStorage.setItem("last_email_change_request", Date.now().toString());
      localStorage.setItem("email_change_cooldown_seconds", emailCooldownSeconds.value.toString());
      emailChangeError.value = "Please wait before requesting another email change.";
      startEmailCooldown();
    } else {
      emailChangeError.value = error.response?.data?.error || "Failed to change email.";
    }
  } finally {
    loadingEmail.value = false;
  }
};


// Change Password
const oldPassword = ref("");
const newPassword = ref("");
const confirmNewPassword = ref("");
const passwordChangeMessage = ref("");
const passwordChangeError = ref("");
const loadingPassword = ref(false);

const changePassword = async () => {
  passwordChangeMessage.value = "";
  passwordChangeError.value = "";
  loadingPassword.value = true;

  if (!oldPassword.value || !newPassword.value || !confirmNewPassword.value) {
    passwordChangeError.value = "All fields are required.";
    loadingPassword.value = false;
    return;
  }
  if (newPassword.value !== confirmNewPassword.value) {
    passwordChangeError.value = "New passwords do not match.";
    loadingPassword.value = false;
    return;
  }

  try {
    const response = await api.post("change-password/", {
      old_password: oldPassword.value,
      new_password: newPassword.value,
      confirm_password: confirmNewPassword.value,
    });
    passwordChangeMessage.value = response.data.message;
  } catch (error: any) {
    if (error.response?.status === 429) {
      passwordChangeError.value = "Please wait before requesting another password change.";
    } else {
      passwordChangeError.value = error.response?.data?.error || "Failed to change password.";
    }
  } finally {
    loadingPassword.value = false;
  }
};

const goBack = () => {
  router.push("/dashboard");
};
</script>

<template>
  <!-- Full-page container with background -->
  <div
    class="pt-30 pb-30 flex items-center justify-center px-4 bg-cover bg-center overflow-y-auto"
    style="background-image: url('/background.png'); background-attachment: fixed;"
  >
    <!-- Semi-transparent, blurred container -->
    <div class="bg-white/30 backdrop-blur-lg p-8 rounded-lg shadow-lg max-w-md w-full border border-white/20">
      <h1 class="text-center text-2xl font-bold text-white sm:text-3xl">
        Account Settings
      </h1>

      <!-- Change Email Section -->
      <div class="mt-6 space-y-4">
        <h2 class="text-lg font-semibold text-white">Change Email</h2>

        <!-- Error / Success Messages for Email Change -->
        <div
          v-if="emailChangeError"
          class="w-full text-center bg-black/60 backdrop-blur-md px-4 py-2 rounded"
        >
          <p class="text-red-500 text-s">{{ emailChangeError }}</p>
        </div>
        <div
          v-if="emailChangeMessage"
          class="w-full text-center bg-black/60 backdrop-blur-md px-4 py-2 rounded"
        >
          <p class="text-green-400 text-s">{{ emailChangeMessage }}</p>
        </div>

        <!-- New Email Input -->
        <input
          type="email"
          v-model="newEmail"
          placeholder="Enter new email"
          class="w-full rounded-lg border-gray-300 p-3 text-sm bg-white/80 text-black"
        />

        <!-- Change Email Button with cooldown logic -->
        <button
          @click="changeEmail"
          :disabled="loadingEmail || emailCooldownActive"
          class="w-full rounded-lg bg-blue-600 px-5 py-3 text-sm font-medium text-white hover:bg-blue-700 transition disabled:bg-gray-500"
        >
          <template v-if="emailCooldownActive">
            Wait {{ emailCooldownSeconds }}s
          </template>
          <template v-else>
            {{ loadingEmail ? "Changing..." : "Change Email" }}
          </template>
        </button>
      </div>

      <!-- Change Password Section -->
      <div class="mt-8 space-y-4">
        <h2 class="text-lg font-semibold text-white">Change Password</h2>

        <!-- Error / Success Messages for Password Change -->
        <div
          v-if="passwordChangeError"
          class="w-full text-center bg-black/60 backdrop-blur-md px-4 py-2 rounded"
        >
          <p class="text-red-500 text-s">{{ passwordChangeError }}</p>
        </div>
        <div
          v-if="passwordChangeMessage"
          class="w-full text-center bg-black/60 backdrop-blur-md px-4 py-2 rounded"
        >
          <p class="text-green-400 text-s">{{ passwordChangeMessage }}</p>
        </div>

        <!-- Old Password -->
        <input
          type="password"
          v-model="oldPassword"
          placeholder="Enter current password"
          class="w-full rounded-lg border-gray-300 p-3 text-sm bg-white/80 text-black"
        />

        <!-- New Password -->
        <input
          type="password"
          v-model="newPassword"
          placeholder="Enter new password"
          class="w-full rounded-lg border-gray-300 p-3 text-sm bg-white/80 text-black"
        />

        <!-- Confirm New Password -->
        <input
          type="password"
          v-model="confirmNewPassword"
          placeholder="Confirm new password"
          class="w-full rounded-lg border-gray-300 p-3 text-sm bg-white/80 text-black"
        />
        <p class="text-gray-200 text-s mt-1">
            Password must be at least <strong>8 characters</strong> long, contain
            <strong>uppercase</strong> & <strong>lowercase</strong> letters, a
            <strong>number</strong>, and a
            <strong>special character</strong>.
          </p>

        <!-- Change Password Button -->
        <button
          @click="changePassword"
          :disabled="loadingPassword"
          class="w-full rounded-lg bg-blue-600 px-5 py-3 text-sm font-medium text-white hover:bg-blue-700 transition disabled:bg-gray-500"
        >
          {{ loadingPassword ? "Changing..." : "Change Password" }}
        </button>
      </div>

      <!-- Back Button -->
      <button
        @click="goBack"
        class="mt-6 w-full rounded-lg bg-gray-700 px-5 py-3 text-sm font-medium text-white hover:bg-gray-600 transition"
      >
        Back to Dashboard
      </button>
    </div>
  </div>
</template>

<style scoped>
input {
  outline: none;
  transition: border 0.3s ease-in-out;
}
input:focus {
  border-color: #ffffff;
  box-shadow: 0 0 0 2px #525252;
}
button {
  transition: background 0.3s ease-in-out;
}
</style>