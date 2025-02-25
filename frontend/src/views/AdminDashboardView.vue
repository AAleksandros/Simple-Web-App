<script setup lang="ts">
import { ref, onMounted, reactive, computed } from "vue";
import api from "../api";
import { useAuthStore } from "../stores/auth";

const authStore = useAuthStore();
const users = ref<{ id: number; email: string; is_active: boolean; is_staff: boolean }[]>([]);
const errorMessage = ref("");
const successMessage = ref("");
const currentPage = ref(1);
const itemsPerPage = 10;
const searchQuery = ref("");
const sortColumn = ref<"id" | "email">("id");
const sortDirection = ref<"asc" | "desc">("asc");

// Modal state
const showModal = ref(false);
const modalAction = ref<"delete" | "update" | null>(null);
const selectedUserId = ref<number | null>(null);

// For status update, we use a reactive Map to store the temporary status per user
const tempUserStatus = reactive(new Map<number, { is_active: boolean; is_staff: boolean }>());
const modalOriginalStatus = ref<{ is_active: boolean; is_staff: boolean } | null>(null);

const showSuccess = (msg: string) => {
  successMessage.value = msg;
  setTimeout(() => {
    successMessage.value = "";
  }, 5000);
};

const showError = (msg: string) => {
  errorMessage.value = msg;
  setTimeout(() => {
    errorMessage.value = "";
  }, 5000);
};

const fetchUsers = async () => {
  try {
    const response = await api.get("admin/users/", {
      headers: { Authorization: `Bearer ${authStore.token}` },
    });
    users.value = response.data;
    // Initialize temporary status for each user
    users.value.forEach(user => {
      tempUserStatus.set(user.id, { is_active: user.is_active, is_staff: user.is_staff });
    });
  } catch (error: any) {
    showError("Failed to fetch users.");
  }
};

onMounted(fetchUsers);

//  Search & Sort 
const filteredUsers = computed(() => {
  const query = searchQuery.value.trim().toLowerCase();
  if (!query) return users.value;
  return users.value.filter(user => {
    return (
      user.email.toLowerCase().includes(query) ||
      user.id.toString() === query
    );
  });
});

const sortedUsers = computed(() => {
  const sorted = [...filteredUsers.value];
  sorted.sort((a, b) => {
    // Always keep admin users first
    if (a.is_staff && !b.is_staff) return -1;
    if (!a.is_staff && b.is_staff) return 1;
    if (sortColumn.value === "id") {
      return sortDirection.value === "asc" ? a.id - b.id : b.id - a.id;
    } else {
      return sortDirection.value === "asc"
        ? a.email.localeCompare(b.email)
        : b.email.localeCompare(a.email);
    }
  });
  return sorted;
});

const totalPages = computed(() => {
  return Math.ceil(sortedUsers.value.length / itemsPerPage);
});

const paginatedUsers = computed(() => {
  const startIndex = (currentPage.value - 1) * itemsPerPage;
  return sortedUsers.value.slice(startIndex, startIndex + itemsPerPage);
});

// Sorting Handler
function sortBy(column: "id" | "email") {
  if (sortColumn.value === column) {
    sortDirection.value = sortDirection.value === "asc" ? "desc" : "asc";
  } else {
    sortColumn.value = column;
    sortDirection.value = "asc";
  }
  currentPage.value = 1;
}

// Modal / Actions
const openModal = (action: "delete" | "update", userId: number) => {
  errorMessage.value = "";
  successMessage.value = "";
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

const handleActiveChange = (userId: number, event: Event) => {
  const newValue = (event.target as HTMLSelectElement).value === "true";
  const current = tempUserStatus.get(userId);
  if (current) {
    tempUserStatus.set(userId, { ...current, is_active: newValue });
  }
  openModal("update", userId);
};

const handleStaffChange = (userId: number, event: Event) => {
  const newValue = (event.target as HTMLSelectElement).value === "true";
  const current = tempUserStatus.get(userId);
  if (current) {
    tempUserStatus.set(userId, { ...current, is_staff: newValue });
  }
  openModal("update", userId);
};

const modalHeading = computed(() => {
  if (modalAction.value === "update" && modalOriginalStatus.value && modalOriginalStatus.value.is_staff) {
    return "<span style='color: red;'>Warning:</span> You are about to modify an admin account!";
  }
  return "Are you sure you want to do that?";
});

const modalMessage = computed(() => {
  if (modalAction.value === "update" && modalOriginalStatus.value && modalOriginalStatus.value.is_staff) {
    return "Modifying an admin account may have significant consequences. Are you absolutely sure you want to proceed?";
  }
  return "This action may have consequences, are you absolutely sure?";
});

const confirmAction = async () => {
  if (modalAction.value === "delete" && selectedUserId.value !== null) {
    try {
      await api.delete(`admin/users/${selectedUserId.value}/`, {
        headers: { Authorization: `Bearer ${authStore.token}` },
      });
      users.value = users.value.filter(user => user.id !== selectedUserId.value);
      tempUserStatus.delete(selectedUserId.value);
      showSuccess("User deleted successfully!");
    } catch (error) {
      showError("Failed to delete user.");
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
      const idx = users.value.findIndex(u => u.id === selectedUserId.value);
      if (idx !== -1) {
        users.value[idx] = { ...users.value[idx], ...newStatus };
      }
      showSuccess("User updated successfully!");
    } catch (error) {
      showError("Failed to update user.");
    }
  }
  showModal.value = false;
};

const cancelAction = () => {
  if (modalAction.value === "update" && selectedUserId.value !== null && modalOriginalStatus.value) {
    tempUserStatus.set(selectedUserId.value, { ...modalOriginalStatus.value });
  }
  showModal.value = false;
};
</script>

<template>
  <div 
    class="h-screen flex items-center justify-center px-4 bg-cover bg-center"
    style="background-image: url('/background.png'); background-attachment: fixed;"
  >
    <div class="bg-white/30 backdrop-blur-md p-8 rounded-lg shadow-lg w-full max-w-4xl">
      <h1 class="text-center text-3xl font-bold text-white mb-4">
        Admin Dashboard
      </h1>

      <!-- Success / Error messages -->
      <div v-if="successMessage" class="w-full text-center mb-4 bg-black/60 backdrop-blur-md px-4 py-2 rounded">
        <p class="text-green-500 text-s">
          {{ successMessage }}
        </p>
      </div>
      <div v-if="errorMessage" class="w-full text-center mb-4 bg-black/60 backdrop-blur-md px-4 py-2 rounded">
        <p class="text-red-500 text-s">
          {{ errorMessage }}
        </p>
      </div>

      <!-- Search Input -->
      <div class="mb-4">
        <input
          type="text"
          v-model="searchQuery"
          placeholder="Search by ID or email..."
          class="w-full p-3 rounded border border-gray-500 text-white placeholder:text-white/80 bg-gray-800/70 text-lg"
        />
      </div>

      <div class="overflow-x-auto rounded-t-lg mt-4">
        <table class="min-w-full table-fixed divide-y divide-gray-300 text-sm text-white">
          <thead class="bg-white/20 text-gray-900">
            <tr class="h-12">
              <th 
                class="px-4 py-2 text-left font-medium cursor-pointer" 
                style="width:80px;" 
                @click="sortBy('id')"
              >
                ID <span v-if="sortColumn === 'id'">{{ sortDirection === 'asc' ? '↑' : '↓' }}</span>
              </th>
              <th 
                class="px-4 py-2 text-left font-medium cursor-pointer" 
                style="width:300px;" 
                @click="sortBy('email')"
              >
                Email <span v-if="sortColumn === 'email'">{{ sortDirection === 'asc' ? '↑' : '↓' }}</span>
              </th>
              <th class="px-4 py-2 text-center font-medium" style="width:100px;">Active</th>
              <th class="px-4 py-2 text-center font-medium" style="width:100px;">Role</th>
              <th class="px-4 py-2 text-center font-medium" style="width:100px;">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-400" style="min-height: 400px;">
            <tr v-for="user in paginatedUsers" :key="user.id" class="h-12">
              <td class="px-4 py-2" style="width:80px;">{{ user.id }}</td>
              <td class="px-4 py-2" style="width:300px;">{{ user.email }}</td>
              <td class="px-4 py-2 text-center" style="width:100px;">
                <select 
                  :value="tempUserStatus.get(user.id)?.is_active"
                  @change="handleActiveChange(user.id, $event)"
                  class="border border-gray-300 rounded px-2 py-1 bg-white text-black w-full"
                >
                  <option :value="true">Yes</option>
                  <option :value="false">No</option>
                </select>
              </td>
              <td class="px-4 py-2 text-center" style="width:100px;">
                <select 
                  :value="tempUserStatus.get(user.id)?.is_staff"
                  @change="handleStaffChange(user.id, $event)"
                  class="border border-gray-300 rounded px-2 py-1 bg-white text-black w-full"
                >
                  <option :value="true">Admin</option>
                  <option :value="false">User</option>
                </select>
              </td>
              <td class="px-4 py-2 text-center" style="width:100px;">
                <button @click="openModal('delete', user.id)" class="delete-btn">
                  Delete
                </button>
              </td>
            </tr>
            <tr v-for="n in (10 - paginatedUsers.length)" :key="'empty-' + n" class="h-12">
              <td class="px-4 py-4 text-center text-gray-500" colspan="5">—</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination Controls with Highlighted Active Page -->
      <div class="mt-4 flex justify-end space-x-2 items-center">
        <button
          class="px-3 py-1 bg-gray-300 rounded text-white"
          :disabled="currentPage === 1"
          @click="currentPage--"
        >
          «
        </button>
        <button
          v-for="page in totalPages"
          :key="page"
          class="px-3 py-1 rounded transition-colors duration-300"
          :class="currentPage === page ? 'bg-blue-500 text-blue-400 font-bold shadow-md' : 'bg-gray-300 text-white'"
          @click="currentPage = page"
        >
          {{ page }}
        </button>
        <button
          class="px-3 py-1 bg-gray-300 rounded text-white"
          :disabled="currentPage === totalPages"
          @click="currentPage++"
        >
          »
        </button>
      </div>
    </div>

    <!-- Modal Confirmation Popup -->
    <div v-if="showModal" class="fixed inset-0 flex items-center justify-center bg-black/50">
      <div class="rounded-lg bg-white/20 backdrop-blur-lg p-8 shadow-2xl max-w-sm border border-white/30">
        <h2 class="text-lg font-bold text-white" v-html="modalHeading"></h2>
        <p class="mt-2 text-sm text-gray-200">{{ modalMessage }}</p>
        <div class="mt-4 flex gap-2">
          <button @click="confirmAction" class="rounded-sm bg-green-500 px-4 py-2 text-sm font-medium text-white hover:bg-green-600">
            Yes, I'm sure
          </button>
          <button @click="cancelAction" class="rounded-sm bg-gray-700 px-4 py-2 text-sm font-medium text-white hover:bg-gray-600">
            No, go back
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
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

button svg {
  color: white;
}
</style>