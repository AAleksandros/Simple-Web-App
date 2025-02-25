<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";
import api from "../api";
import { useAuthStore } from "../stores/auth";
import axios from "axios";

const email = ref("");
const password = ref("");
const errorMessage = ref("");

const authStore = useAuthStore();
const router = useRouter();

const login = async () => {
  errorMessage.value = "";

  try {
    const response = await api.post("login/", {
      email: email.value,
      password: password.value,
    });

    if (response.data.access && response.data.user) {
      authStore.login(response.data.access, response.data.user);
      router.push(response.data.user.is_staff ? "/admin-dashboard" : "/dashboard");
    } else {
      throw new Error("Invalid server response.");
    }
  } catch (err) {
    if (axios.isAxiosError(err)) {
      errorMessage.value = err.response?.data?.error || "Invalid email or password.";
    } else {
      errorMessage.value = "An unexpected error occurred.";
    }
  }
};

const goToForgotPassword = () => {
  router.push("/forgot-password");
};
</script>

<template>
  <div class="h-screen flex items-center justify-center px-4 bg-cover bg-center"
       style="background-image: url('/background.png'); background-attachment: fixed;">
    
    <div class="bg-white/30 backdrop-blur-md p-8 rounded-lg shadow-lg max-w-md w-full">
      <h1 class="text-center text-2xl font-bold text-white sm:text-3xl">Login Form</h1>
      <p class="mt-2 text-center text-white">Sign in to your account below.</p>

      <form @submit.prevent="login" class="mt-6 space-y-4">
        <p v-if="errorMessage" class="text-center text-red-500 text-sm">{{ errorMessage }}</p>

        <div>
          <label for="email" class="sr-only">Email</label>
          <input
            type="email"
            id="email"
            v-model="email"
            placeholder="Enter email"
            class="w-full rounded-lg border-gray-300 p-3 text-sm text-white"
          />
        </div>

        <div>
          <label for="password" class="sr-only">Password</label>
          <input
            type="password"
            id="password"
            v-model="password"
            placeholder="Enter password"
            class="w-full rounded-lg border-gray-300 p-3 text-sm text-white"
          />
        </div>

        <button
          type="submit"
          class="w-full rounded-lg bg-green-600 px-5 py-3 text-sm font-medium text-white"
        >
          Sign in
        </button>

        <p class="text-center text-s text-black">
          No account?
          <router-link to="/register" class="underline text-blue-400 hover:text-blue-600">
            Sign up
          </router-link>
        </p>

        <button
          type="button"
          class="block mx-auto mt-2 text-sm text-white"
          @click="goToForgotPassword"
        >
          Forgot password?
        </button>
      </form>
    </div>
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
  margin-bottom: 20px;
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


button:disabled {
  background: gray;
  cursor: not-allowed;
}

.error {
  color: red;
  margin-top: 10px;
}
</style>