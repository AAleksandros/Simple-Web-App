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

    console.log("API Login Response:", response.data);

    if (response.data.access && response.data.user) {
      if (!response.data.user.is_active) {
        console.log("Redirecting unverified user to /verify-email...");
        localStorage.setItem("pending_verification_email", email.value);
        localStorage.setItem("email_last_sent", Date.now().toString());
        return router.push("/verify-email");
      }

      authStore.login(response.data.access, response.data.user);
      console.log("Redirecting to dashboard...");
      router.push(response.data.user.is_staff ? "/admin-dashboard" : "/dashboard");
    } else {
      throw new Error("Invalid server response.");
    }
  } catch (err) {
    if (axios.isAxiosError(err) && err.response) {
      const apiError = err.response.data;

      // Handle unverified email case without logging an error
      if (apiError?.error?.includes("Email not verified")) {
        console.log("Redirecting to /verify-email after failed login due to unverified email...");
        localStorage.setItem("pending_verification_email", email.value);
        localStorage.setItem("email_last_sent", Date.now().toString());
        return router.push("/verify-email");
      }

      console.error("Unexpected Login Error:", err);
      errorMessage.value = apiError?.error || "Invalid email or password.";
    } else {
      console.error("Unexpected Login Exception:", err);
      errorMessage.value = "An unexpected error occurred.";
    }
  }
};

const goToForgotPassword = () => {
  router.push("/forgot-password");
};
</script>

<template>
  <div class="pt-30 pb-30 flex items-center justify-center px-4 bg-cover bg-center overflow-y-auto" 
       style="background-image: url('/background.png'); background-attachment: fixed;">
    
    <div class="bg-white/30 backdrop-blur-md p-8 rounded-lg shadow-lg max-w-md w-full">
      <h1 class="text-center text-2xl font-bold text-white sm:text-3xl">Login Form</h1>
      <p class="mt-2 text-center text-white">Sign in to your account below.</p>

      <form @submit.prevent="login" class="mt-6 space-y-4">
        <!-- Error Message Container -->
        <div v-if="errorMessage" class="w-full text-center mt-2 bg-black/60 backdrop-blur-md px-4 py-2 rounded">
          <p class="text-red-500 text-s">{{ errorMessage }}</p>
        </div>

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