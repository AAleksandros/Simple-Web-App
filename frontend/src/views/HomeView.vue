<script setup lang="ts">
import { useRouter } from "vue-router";
import { useAuthStore } from "../stores/auth";

const router = useRouter();
const authStore = useAuthStore();

const goToRegister = () => {
  router.push("/register");
};

const goToLogin = () => {
  router.push("/login");
};

const goToDashboard = () => {
  router.push("/dashboard");
};
</script>

<template>
  <div class="h-screen w-screen flex items-center justify-center bg-cover bg-center overflow-hidden"
    style="background-image: url('/background.png');">
    
    <!-- Glass Card Container -->
    <div class="bg-white/25 backdrop-blur-md shadow-xl rounded-lg p-8 max-w-lg w-full text-center border border-white/30">

      <h1 class="text-4xl font-bold text-white drop-shadow-md">
        Welcome to <br /> 
        <span class="text-blue-300">My Web App</span>
      </h1>
      <p class="text-white/90 mt-2 text-lg">A modern auth system demo.</p>

      <!-- Buttons -->
      <div class="mt-6 space-y-3">
        <template v-if="!authStore.isAuthenticated">
          <button @click="goToRegister"
            class="w-full px-5 py-3 text-lg font-semibold bg-teal-500 text-white rounded-lg hover:bg-teal-600 transition">
            Get Started
          </button>
          <button @click="goToLogin"
            class="w-full px-5 py-3 text-lg font-semibold bg-sky-500 text-white rounded-lg hover:bg-sky-600 transition">
            Login
          </button>
        </template>

        <template v-else>
          <button @click="goToDashboard"
            class="w-full px-5 py-3 text-lg font-semibold bg-indigo-500 text-white rounded-lg hover:bg-indigo-600 transition">
            Go to Dashboard
          </button>
        </template>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Prevent scrolling */
html, body {
  height: 100%;
  overflow: hidden;
  margin: 0;
}

/* Glass effect */
.glass {
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.25);
}

/* Soft drop shadow for readability */
h1, p {
  text-shadow: 1px 1px 4px rgba(0, 0, 0, 0.3);
}
</style>