import { defineStore } from "pinia";
import { ref, computed, watch } from "vue";

interface User {
  id: number;
  email: string;
  is_active: boolean;
  is_staff: boolean;
}

export const useAuthStore = defineStore("auth", () => {
  const token = ref<string | null>(localStorage.getItem("access_token") || null);

  const parseUserData = (): User | null => {
    try {
      const storedUser = localStorage.getItem("user");
      return storedUser ? JSON.parse(storedUser) : null;
    } catch (error) {
      console.error("Error parsing user data:", error);
      return null;
    }
  };

  const user = ref<User | null>(parseUserData());

  const isAuthenticated = computed(() => !!token.value);
  const isAdmin = computed(() => user.value?.is_staff === true);

  const login = (newToken: string, userData: User) => {
    token.value = newToken;
    user.value = userData;
    localStorage.setItem("access_token", newToken);
    localStorage.setItem("user", JSON.stringify(userData));
  };

  const logout = () => {
    token.value = null;
    user.value = null;
    localStorage.removeItem("access_token");
    localStorage.removeItem("user");
  };

  // Ensure user data updates on changes
  watch(token, () => {
    user.value = parseUserData();
  });

  return { token, user, isAuthenticated, isAdmin, login, logout };
});