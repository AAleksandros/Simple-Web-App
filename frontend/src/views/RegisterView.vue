<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";
import api from "../api";

const email = ref("");
const password = ref("");
const confirmPassword = ref("");
const loading = ref(false);
const successMessage = ref("");
const errorMessage = ref("");
const router = useRouter();

const register = async () => {
  successMessage.value = "";
  errorMessage.value = "";

  if (!email.value || !password.value || !confirmPassword.value) {
    errorMessage.value = "Email, password, and confirmation are required.";
    return;
  }

  if (password.value !== confirmPassword.value) {
    errorMessage.value = "Passwords do not match.";
    return;
  }

  loading.value = true;

  try {
    const response = await api.post("register/", {
      email: email.value,
      password: password.value,
      confirm_password: confirmPassword.value,
    });

    // Registration successful
    localStorage.setItem("pending_verification_email", email.value);
    localStorage.setItem("email_last_sent", Date.now().toString());

    successMessage.value =
      "Registration successful! Redirecting to email verification page soon...";
    setTimeout(() => {
      router.push("/verify-email").catch((err) =>
        console.error("Navigation error:", err)
      );
    }, 5000);
  } catch (error: any) {
    const apiError = error.response?.data?.error;

    // Handle "User already exists but is not verified" case
    if (apiError?.includes("User already exists but is not verified")) {
      console.log("Email exists but not verified. Displaying message then redirecting...");

      localStorage.setItem("pending_verification_email", email.value);
      localStorage.setItem("email_last_sent", Date.now().toString());

      successMessage.value =
        "This email is already registered but not verified. Redirecting to verification page soon...";
      setTimeout(() => {
        router.push("/verify-email").catch((err) =>
          console.error("Navigation error:", err)
        );
      }, 5000);
      return;
    }

    errorMessage.value = apiError || "Registration failed.";
  } finally {
    loading.value = false;
  }
};
</script>

<template>
  <div
    class="pt-30 pb-30 flex items-center justify-center px-4 bg-cover bg-center overflow-y-auto"
    style="background-image: url('/background.png'); background-attachment: fixed;"
  >
    <div class="bg-white/30 backdrop-blur-md p-8 rounded-lg shadow-lg max-w-md w-full">
      <h1 class="text-center text-2xl font-bold text-white sm:text-3xl">
        Create an Account
      </h1>
      <p class="mt-2 text-center text-gray-200">Sign up to get started.</p>

      <!-- Error Message -->
      <div
        v-if="errorMessage"
        class="w-full text-center mt-2 bg-black/60 backdrop-blur-md px-4 py-2 rounded"
      >
        <p class="text-red-500 text-s">{{ errorMessage }}</p>
      </div>

      <!-- Success Message -->
      <div
        v-if="successMessage"
        class="w-full text-center mt-2 bg-black/60 backdrop-blur-md px-4 py-2 rounded"
      >
        <p class="text-green-400 text-s">{{ successMessage }}</p>
      </div>

      <form @submit.prevent="register" class="mt-6 space-y-4">
        <div>
          <label for="email" class="sr-only">Email</label>
          <input
            type="email"
            id="email"
            v-model="email"
            placeholder="Enter your email"
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
            class="w-full rounded-lg border-gray-100 p-3 text-sm text-white"
          />
          <p class="text-gray-200 text-s mt-1">
            Password must be at least <strong>8 characters</strong> long, contain
            <strong>uppercase</strong> & <strong>lowercase</strong> letters, a
            <strong>number</strong>, and a
            <strong>special character</strong>.
          </p>
        </div>

        <div>
          <label for="confirm-password" class="sr-only">Confirm Password</label>
          <input
            type="password"
            id="confirm-password"
            v-model="confirmPassword"
            placeholder="Confirm password"
            class="w-full rounded-lg border-gray-300 p-3 text-sm text-white"
          />
          <p class="text-gray-200 text-s mt-1">
            Please enter the same password as above.
          </p>
        </div>

        <button
          type="submit"
          :disabled="loading"
          class="w-full rounded-lg bg-green-600 px-5 py-3 text-sm font-medium text-white"
        >
          {{ loading ? "Registering..." : "Create an account" }}
        </button>

        <p class="text-center text-s text-black">
          Already have an account?
          <router-link
            to="/login"
            class="underline text-blue-400 hover:text-blue-600"
          >
            Log in
          </router-link>
        </p>
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
}

.error {
  color: red;
  margin-top: 10px;
}
</style>