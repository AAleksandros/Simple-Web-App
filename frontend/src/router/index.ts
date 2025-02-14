import { createRouter, createWebHistory, NavigationGuardNext, RouteLocationNormalized } from "vue-router";
import HomeView from "../views/HomeView.vue";
import LoginView from "../views/LoginView.vue";
import RegisterView from "../views/RegisterView.vue";
import DashboardView from "../views/DashboardView.vue";
import { useAuthStore } from "../stores/auth";

const routes = [
  { path: "/", component: HomeView },
  { 
    path: "/login", 
    component: LoginView, 
    beforeEnter: (to: RouteLocationNormalized, _from: RouteLocationNormalized, next: NavigationGuardNext) => {
      const authStore = useAuthStore();
      if (authStore.isAuthenticated) {
        next("/dashboard");
      } else {
        next();
      }
    }
  },
  { 
    path: "/register", 
    component: RegisterView, 
    beforeEnter: (to: RouteLocationNormalized, _from: RouteLocationNormalized, next: NavigationGuardNext) => {
      const authStore = useAuthStore();
      if (authStore.isAuthenticated) {
        next("/dashboard");
      } else {
        next();
      }
    }
  },
  { 
    path: "/dashboard", 
    component: DashboardView, 
    beforeEnter: (to: RouteLocationNormalized, _from: RouteLocationNormalized, next: NavigationGuardNext) => {
      const authStore = useAuthStore();
      if (!authStore.isAuthenticated) {
        next("/login");
      } else {
        next();
      }
    }
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;