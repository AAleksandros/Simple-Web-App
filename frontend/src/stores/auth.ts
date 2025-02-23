import { defineStore } from "pinia";
import { ref, computed, watch } from "vue";
import { useRouter } from "vue-router";
import api from "../api";

interface User {
  id: number;
  email: string;
  is_active: boolean;
  is_staff: boolean;
}

export const useAuthStore = defineStore("auth", () => {
  const token = ref<string | null>(localStorage.getItem("access_token") || null);
  const router = useRouter();

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

  const fetchUserProfile = async () => {
    try {
      const response = await api.get("profile/");
      const profile = response.data;

      // Check if essential profile fields are empty
      const isProfileIncomplete =
        !profile.phone_number || !profile.country || !profile.city || !profile.address;

      return isProfileIncomplete;
    } catch (error) {
      console.error("Error fetching profile data:", error);
      return false;
    }
  };

  const login = async (newToken: string, userData: User) => {
    token.value = newToken;
    user.value = userData;
    localStorage.setItem("access_token", newToken);
    localStorage.setItem("user", JSON.stringify(userData));

    try {
      if (!userData.is_staff) {
        const isProfileIncomplete = await fetchUserProfile();

        if (isProfileIncomplete) {
          router.push("/profile");
          return;
        }
      }

      // Default redirection based on user type
      router.push(userData.is_staff ? "/admin-dashboard" : "/dashboard");
    } catch (error) {
      console.error("Error checking profile completeness:", error);
      router.push(userData.is_staff ? "/admin-dashboard" : "/dashboard");
    }
  };

  const logout = () => {
    token.value = null;
    user.value = null;
    localStorage.removeItem("access_token");
    localStorage.removeItem("user");
    localStorage.removeItem("profile");
    router.push("/login");
    window.location.reload();
  };

  // Ensure user data updates on changes
  watch(token, () => {
    user.value = parseUserData();
  });

  return { token, user, isAuthenticated, isAdmin, login, logout };
});