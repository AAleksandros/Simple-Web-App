<script setup lang="ts">
import { ref, onMounted, reactive } from "vue";
import api from "../api";
import { useAuthStore } from "../stores/auth";

const authStore = useAuthStore();
const users = ref<{ id: number; email: string; is_active: boolean; is_staff: boolean }[]>([]);
const errorMessage = ref("");
const successMessage = ref("");

const showModal = ref(false);
const modalAction = ref<"delete" | "update" | null>(null);
const selectedUserId = ref<number | null>(null);

// For update modal, we store the new (temporary) status
// and also store the original values for canceling.
const tempUserStatus = reactive(new Map<number, { is_active: boolean; is_staff: boolean }>());
const modalOriginalStatus = ref<{ is_active: boolean; is_staff: boolean } | null>(null);

const fetchUsers = async () => {
  try {
    const response = await api.get("admin/users/", {
      headers: { Authorization: `Bearer ${authStore.token}` },
    });
    users.value = response.data;
    users.value.forEach(user => {
      tempUserStatus.set(user.id, { is_active: user.is_active, is_staff: user.is_staff });
    });
  } catch (error: any) {
    errorMessage.value = "Failed to fetch users.";
  }
};

onMounted(fetchUsers);

/**
 * Opens the modal.
 * For "update", we record the original status from the users array.
 */
const openModal = (action: "delete" | "update", userId: number) => {
  showModal.value = true;
  modalAction.value = action;
  selectedUserId.value = userId;
  if (action === "update") {
    const orig = users.value.find(u => u.id === userId);
    if (orig) {
      modalOriginalStatus.value = { is_active: orig.is_active, is_staff: orig.is_staff };
    }
  }
};

/**
 * Handler for when the Active dropdown is changed.
 * It updates the temporary state and opens the modal for confirmation.
 */
const handleActiveChange = (userId: number, event: Event) => {
  const newValue = (event.target as HTMLSelectElement).value === "true";
  const current = tempUserStatus.get(userId);
  if (current) {
    tempUserStatus.set(userId, { ...current, is_active: newValue });
  }
  openModal("update", userId);
};

/**
 * Handler for when the Role dropdown is changed.
 */
const handleStaffChange = (userId: number, event: Event) => {
  const newValue = (event.target as HTMLSelectElement).value === "true";
  const current = tempUserStatus.get(userId);
  if (current) {
    // Update only the staff value in the temporary status
    tempUserStatus.set(userId, { ...current, is_staff: newValue });
  }
  openModal("update", userId);
};

const confirmAction = async () => {
  if (modalAction.value === "delete" && selectedUserId.value !== null) {
    try {
      await api.delete(`admin/users/${selectedUserId.value}/`, {
        headers: { Authorization: `Bearer ${authStore.token}` },
      });
      users.value = users.value.filter(user => user.id !== selectedUserId.value);
      tempUserStatus.delete(selectedUserId.value);
      successMessage.value = "User deleted successfully!";
    } catch (error) {
      errorMessage.value = "Failed to delete user.";
    }
  } else if (modalAction.value === "update" && selectedUserId.value !== null) {
    const newStatus = tempUserStatus.get(selectedUserId.value);
    if (!newStatus) return;
    try {
      await api.put(
        `admin/users/${selectedUserId.value}/`,
        { is_active: newStatus.is_active, is_staff: newStatus.is_staff },
        { headers: { Authorization: `Bearer ${authStore.token}` } }
      );
      // Update the user in the main array
      const idx = users.value.findIndex(u => u.id === selectedUserId.value);
      if (idx !== -1) {
        users.value[idx] = { ...users.value[idx], ...newStatus };
      }
      successMessage.value = "User updated successfully!";
    } catch (error) {
      errorMessage.value = "Failed to update user.";
    }
  }
  showModal.value = false;
};

const cancelAction = () => {
  if (modalAction.value === "update" && selectedUserId.value !== null && modalOriginalStatus.value) {
    // Reset the temporary status for this user to the original values
    tempUserStatus.set(selectedUserId.value, { ...modalOriginalStatus.value });
  }
  showModal.value = false;
};
</script>

<template>
  <div class="flex flex-col items-center justify-center min-h-screen p-8">
    <h1 class="text-3xl font-bold text-white mb-4">Admin Dashboard</h1>

    <div v-if="successMessage" class="p-3 mb-4 text-green-500 rounded">{{ successMessage }}</div>
    <div v-if="errorMessage" class="p-3 mb-4 text-red-500 rounded">{{ errorMessage }}</div>

    <div class="w-full max-w-4xl bg-white/30 backdrop-blur-lg shadow-lg rounded-lg p-6">
      <div class="overflow-x-auto rounded-t-lg">
        <table class="min-w-full divide-y divide-gray-300 text-sm text-white">
          <thead class="bg-white/20 text-gray-900">
            <tr>
              <th class="px-4 py-2 text-left font-medium">ID</th>
              <th class="px-4 py-2 text-left font-medium">Email</th>
              <th class="px-4 py-2 text-center font-medium">Active</th>
              <th class="px-4 py-2 text-center font-medium">Role</th>
              <th class="px-4 py-2 text-center font-medium">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-400">
            <tr v-for="user in users" :key="user.id">
              <td class="px-4 py-2">{{ user.id }}</td>
              <td class="px-4 py-2">{{ user.email }}</td>
              <td class="px-4 py-2 text-center">
                <select 
                  :value="tempUserStatus.get(user.id)?.is_active"
                  @change="handleActiveChange(user.id, $event)"
                  class="border border-gray-300 rounded px-2 py-1 bg-white text-black"
                >
                  <option :value="true">Yes</option>
                  <option :value="false">No</option>
                </select>
              </td>
              <td class="px-4 py-2 text-center">
                <select 
                  :value="tempUserStatus.get(user.id)?.is_staff"
                  @change="handleStaffChange(user.id, $event)"
                  class="border border-gray-300 rounded px-2 py-1 bg-white text-black"
                >
                  <option :value="true">Admin</option>
                  <option :value="false">User</option>
                </select>
              </td>
              <td class="px-4 py-2 text-center">
                <button @click="openModal('delete', user.id)" class="delete-btn">
                  Delete
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <!-- Pagination Placeholder -->
      <div class="mt-4 flex justify-end space-x-2">
        <button class="px-3 py-1 bg-gray-300 rounded text-white">«</button>
        <button class="px-3 py-1 bg-blue-500 text-white rounded">1</button>
        <button class="px-3 py-1 bg-gray-300 rounded text-white">»</button>
      </div>
    </div>

    <!-- Modal -->
    <div v-if="showModal" class="fixed inset-0 flex items-center justify-center bg-black/50">
      <div class="rounded-lg bg-white/20 backdrop-blur-lg p-8 shadow-2xl max-w-sm border border-white/30">
        <h2 class="text-lg font-bold text-white">Are you sure you want to do that?</h2>
        <p class="mt-2 text-sm text-gray-200">
          This action may have consequences, are you absolutely sure?
        </p>
        <div class="mt-4 flex gap-2">
          <button @click="confirmAction"
                  class="rounded-sm bg-green-500 px-4 py-2 text-sm font-medium text-white hover:bg-green-600">
            Yes, I'm sure
          </button>
          <button @click="cancelAction"
                  class="rounded-sm bg-gray-700 px-4 py-2 text-sm font-medium text-white hover:bg-gray-600">
            No, go back
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Delete button */
.delete-btn {
  background-color: #e63946;
  color: white;
  border: none;
  padding: 10px 15px;
  font-size: 14px;
  border-radius: 5px;
  cursor: pointer;
  transition: background 0.3s ease-in-out;
}

.delete-btn:hover {
  background-color: #b71c1c;
}

select {
  cursor: pointer;
}

button {
  transition: background 0.3s ease-in-out;
}

/* Fix black-on-black button arrow issue */
button svg {
  color: white;
}
</style>