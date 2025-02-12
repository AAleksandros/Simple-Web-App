import { defineStore } from "pinia";

export const useAuthStore = defineStore("auth", {
  state: () => ({
    isAuthenticated: !!localStorage.getItem("access_token"),
  }),
  actions: {
    login(token: string) {
      localStorage.setItem("access_token", token);
      this.isAuthenticated = true;
    },
    logout() {
      localStorage.removeItem("access_token");
      this.isAuthenticated = false;
    },
  },
});