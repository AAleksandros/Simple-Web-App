import { createRouter, createWebHistory, NavigationGuardNext, RouteLocationNormalized } from "vue-router";
import HomeView from "../views/HomeView.vue";
import LoginView from "../views/LoginView.vue";
import RegisterView from "../views/RegisterView.vue";
import DashboardView from "../views/DashboardView.vue";
import { useAuthStore } from "../stores/auth";

const authGuard = (_to: RouteLocationNormalized, _from: RouteLocationNormalized, next: NavigationGuardNext) => {
  const authStore = useAuthStore();
  authStore.isAuthenticated ? next() : next("/login");
};

const guestGuard = (_to: RouteLocationNormalized, _from: RouteLocationNormalized, next: NavigationGuardNext) => {
  const authStore = useAuthStore();
  authStore.isAuthenticated ? next("/dashboard") : next();
};

const routes = [
  { path: "/", component: HomeView, meta: { title: "Home - Web App" } },
  { path: "/login", component: LoginView, meta: { title: "Login - Web App" }, beforeEnter: guestGuard },
  { path: "/register", component: RegisterView, meta: { title: "Register - Web App" }, beforeEnter: guestGuard },
  { path: "/dashboard", component: DashboardView, meta: { title: "Dashboard - Web App" }, beforeEnter: authGuard }
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach((to) => {
  document.title = typeof to.meta.title === "string" ? to.meta.title : "Web App";
});

export default router;