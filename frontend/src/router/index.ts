import { createRouter, createWebHistory, NavigationGuardNext, RouteLocationNormalized } from "vue-router";
import HomeView from "../views/HomeView.vue";
import LoginView from "../views/LoginView.vue";
import RegisterView from "../views/RegisterView.vue";
import DashboardView from "../views/DashboardView.vue";
import AdminDashboardView from "../views/AdminDashboardView.vue";
import VerifyEmailView from "../views/VerifyEmailView.vue";
import ForgotPasswordView from "../views/ForgotPasswordView.vue";
import ResetPasswordView from "../views/ResetPasswordView.vue";
import ProfileView from "../views/ProfileView.vue";
import AccountSettingsView from "../views/AccountSettingsView.vue";
import { useAuthStore } from "../stores/auth";

// User Dashboard Guard
const authGuard = (_to: RouteLocationNormalized, _from: RouteLocationNormalized, next: NavigationGuardNext) => {
  const authStore = useAuthStore();
  authStore.isAuthenticated ? next() : next("/login");
};

// Admin Dashboard Guard
const adminGuard = (_to: RouteLocationNormalized, _from: RouteLocationNormalized, next: NavigationGuardNext) => {
  const authStore = useAuthStore();
  authStore.isAuthenticated && authStore.isAdmin ? next() : next("/dashboard");
};

// Prevent logged-in users from accessing guest pages (login, register, etc.)
const guestGuard = (_to: RouteLocationNormalized, _from: RouteLocationNormalized, next: NavigationGuardNext) => {
  const authStore = useAuthStore();
  authStore.isAuthenticated ? next("/dashboard") : next();
};

const routes = [
  { path: "/", component: HomeView, meta: { title: "Home - Web App" } },
  { path: "/login", component: LoginView, meta: { title: "Login - Web App" }, beforeEnter: guestGuard },
  { path: "/register", component: RegisterView, meta: { title: "Register - Web App" }, beforeEnter: guestGuard },
  { path: "/profile", component: ProfileView, meta: { title: "My Profile - Web App" }, beforeEnter: authGuard },
  { path: "/account-settings", component: AccountSettingsView, meta: { title: "Account Settings - Web App" }, beforeEnter: authGuard },
  { path: "/dashboard", component: DashboardView, meta: { title: "Dashboard - Web App" }, beforeEnter: authGuard },
  { path: "/admin-dashboard", component: AdminDashboardView, meta: { title: "Admin Panel - Web App" }, beforeEnter: adminGuard },

  // Email Verification & Password Reset
  { path: "/verify-email", component: VerifyEmailView, meta: { title: "Verify Email - Web App" }, beforeEnter: guestGuard },
  { path: "/forgot-password", component: ForgotPasswordView, meta: { title: "Forgot Password - Web App" }, beforeEnter: guestGuard },
  { path: "/reset-password", component: ResetPasswordView, meta: { title: "Reset Password - Web App" }, beforeEnter: guestGuard },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach((to) => {
  document.title = typeof to.meta.title === "string" ? to.meta.title : "Web App";
});

export default router;