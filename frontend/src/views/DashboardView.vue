<script setup lang="ts">
import { useRouter } from "vue-router";
import { useAuthStore } from "../stores/auth";
import { computed } from "vue";

const router = useRouter();
const authStore = useAuthStore();
const isAdmin = computed(() => authStore.user?.is_staff === true);

const logout = () => {
  authStore.logout();
  router.push("/");
};

const goToAdminPanel = () => router.push("/admin-dashboard");
const goToProfile = () => router.push("/profile");
const goToAccountSettings = () => router.push("/account-settings");
</script>

<template>
  <div class="pt-30 pb-30 flex items-center justify-center h-screen px-4 bg-cover bg-center overflow-y-auto"
       style="background-image: url('/background.png'); background-attachment: fixed;">
    
    <div class="bg-white/30 backdrop-blur-lg p-8 rounded-lg shadow-lg max-w-lg w-full border border-white/20 text-center">
      <h1 class="text-4xl font-bold text-white drop-shadow-md">
        Welcome to the <br />
        <span class="text-blue-300">Dashboard</span>
      </h1>

      <p class="mt-2 text-lg text-gray-200">
        You are successfully logged in.
      </p>

      <!-- Role-specific message -->
      <p v-if="isAdmin" class="mt-4 text-lg text-blue-300">
        Go to the <strong>Admin Panel</strong> to manage users and settings.
      </p>
      <p v-else class="mt-4 text-lg text-green-300">
        Go to your <strong>Profile</strong> to view and edit your information.
      </p>

      <div class="mt-6 flex justify-center gap-4">
        <button v-if="isAdmin" @click="goToAdminPanel"
          class="px-6 py-3 rounded-lg text-white bg-blue-500 hover:bg-blue-600 transition text-lg font-semibold">
          Go to Admin Panel
        </button>
        <button v-else @click="goToProfile"
          class="px-6 py-3 rounded-lg text-white bg-green-500 hover:bg-green-600 transition text-lg font-semibold">
          Go to Profile
        </button>

        <!-- Account Settings Button -->
        <button @click="goToAccountSettings"
          class="px-6 py-3 rounded-lg text-white bg-purple-500 hover:bg-purple-600 transition text-lg font-semibold">
          Account Settings
        </button>

        <button @click="logout"
          class="px-6 py-3 rounded-lg text-white bg-red-500 hover:bg-red-600 transition text-lg font-semibold">
          Logout
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
button {
  transition: background 0.3s ease-in-out;
}
h1 {
  text-shadow: 2px 2px 8px rgba(0, 0, 0, 0.3);
}
</style>