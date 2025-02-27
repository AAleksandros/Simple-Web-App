<script setup lang="ts">
import { ref, computed } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "../stores/auth";

const authStore = useAuthStore();
const router = useRouter();

const isAuthenticated = computed(() => authStore.isAuthenticated);
const isAdmin = computed(() => authStore.user?.is_staff === true);

const logout = () => {
  authStore.logout();
  router.push("/");
  setTimeout(() => window.location.reload(), 500);
};

const navVisible = ref(true);

const toggleNav = () => {
  navVisible.value = !navVisible.value;
};
</script>

<template>
  <div class="navbar-container">
    <transition name="slide-nav">
      <div v-if="navVisible" class="nav-inner">
        <!-- Left side: Logout + Dashboard -->
        <div class="left-links">
          <button
            v-if="isAuthenticated"
            @click="logout"
            class="logout-btn"
          >
            Logout
          </button>

          <RouterLink
            v-if="isAuthenticated"
            to="/dashboard"
            class="nav-btn"
          >
            Dashboard
          </RouterLink>
        </div>

        <!-- Right side: other links -->
        <div class="right-links">
          <RouterLink
            v-if="isAuthenticated && !isAdmin"
            to="/profile"
            class="nav-btn"
          >
            Profile
          </RouterLink>

          <RouterLink
            v-if="isAuthenticated"
            to="/account-settings"
            class="nav-btn"
          >
            Account Settings
          </RouterLink>

          <RouterLink
            v-if="isAuthenticated && isAdmin"
            to="/admin-dashboard"
            class="nav-btn"
          >
            Admin Panel
          </RouterLink>
        </div>
      </div>
    </transition>

    <!-- Toggle Button stays visible at all times -->
    <button class="toggle-circle" @click="toggleNav">
      <span v-if="navVisible">✖</span>
      <span v-else>☰</span>
    </button>
  </div>
</template>

<style scoped>
.navbar-container {
  /* Stretch across the top */
  position: fixed;
  top: 4px;
  left: 4px;
  right: 4px;
  z-index: 50;

  /* Align toggle to the right by default */
  display: flex;
  justify-content: flex-end; 
  align-items: center;
}

/* Container that holds all nav links when visible */
.nav-inner {  
  width: 100%; 
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-right: 0.5rem;
}

/* Left side links*/
.left-links {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

/* Right side links */
.right-links {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

/* Toggle button */
.toggle-circle {
  width: 55px;
  height: 55px;
  border-radius: 30%;
  background: #000;
  color: white;
  border: none;
  font-size: 1.5rem;
  display: flex;
  justify-content: center;
  align-items: center;
  cursor: pointer;
  transition: background 0.3s ease;
}
.toggle-circle:hover {
  background: #555;
}

/* Nav button styling */
.nav-btn {
  background: black;
  color: white;
  text-decoration: none;
  padding: 8px 14px;
  font-size: 0.9rem;
  font-weight: 500;
  border-radius: 6px;
  transition: background 0.3s ease-in-out;
}
.nav-btn:hover {
  background: rgb(31, 47, 70);
}

/* Logout button styling */
.logout-btn {
  background: #e63946;
  color: white;
  border: none;
  padding: 8px 14px;
  font-size: 0.9rem;
  font-weight: 500;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.3s ease-in-out;
}
.logout-btn:hover {
  background: #b71c1c;
}

/* Slide Transition */
.slide-nav-enter-active,
.slide-nav-leave-active {
  transition: transform 0.3s ease, opacity 0.3s ease;
}
.slide-nav-enter-from,
.slide-nav-leave-to {
  transform: translateY(-20px);
  opacity: 0;
}
.slide-nav-enter-to,
.slide-nav-leave-from {
  transform: translateY(0);
  opacity: 1;
}
</style>