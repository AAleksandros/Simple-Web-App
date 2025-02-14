<script setup lang="ts">
import { ref, onMounted } from "vue";
import api from "../api";
import { useAuthStore } from "../stores/auth";

const authStore = useAuthStore();
const users = ref<{ id: number; email: string; is_active: boolean; is_staff: boolean }[]>([]);
const errorMessage = ref("");
const successMessage = ref("");

// For Modal
const showModal = ref(false);
const modalAction = ref<"delete" | "update" | null>(null);
const selectedUserId = ref<number | null>(null);
const selectedUserStatus = ref({ is_active: false, is_staff: false });

const fetchUsers = async () => {
  try {
    const response = await api.get("admin/users/", {
      headers: { Authorization: `Bearer ${authStore.token}` },
    });
    users.value = response.data;
  } catch (error) {
    errorMessage.value = "Failed to fetch users.";
  }
};

const openModal = (action: "delete" | "update", userId: number, userStatus?: { is_active: boolean; is_staff: boolean }) => {
  showModal.value = true;
  modalAction.value = action;
  selectedUserId.value = userId;
  if (userStatus) {
    selectedUserStatus.value = { ...userStatus };
  }
};

const confirmAction = async () => {
  if (modalAction.value === "delete" && selectedUserId.value !== null) {
    try {
      await api.delete(`admin/users/${selectedUserId.value}/`, {
        headers: { Authorization: `Bearer ${authStore.token}` },
      });
      users.value = users.value.filter((user) => user.id !== selectedUserId.value);
      successMessage.value = "User deleted successfully!";
    } catch (error) {
      errorMessage.value = "Failed to delete user.";
    }
  } else if (modalAction.value === "update" && selectedUserId.value !== null) {
    try {
      await api.put(
        `admin/users/${selectedUserId.value}/`,
        { is_active: selectedUserStatus.value.is_active, is_staff: selectedUserStatus.value.is_staff },
        { headers: { Authorization: `Bearer ${authStore.token}` } }
      );
      successMessage.value = "User updated successfully!";
      fetchUsers();
    } catch (error) {
      errorMessage.value = "Failed to update user.";
    }
  }
  showModal.value = false;
};

onMounted(fetchUsers);
</script>

<template>
  <div class="admin-container">
    <h2>Admin Dashboard</h2>

    <p v-if="successMessage" class="success">{{ successMessage }}</p>
    <p v-if="errorMessage" class="error">{{ errorMessage }}</p>

    <table>
      <thead>
        <tr>
          <th>ID</th>
          <th>Email</th>
          <th>Active</th>
          <th>Role</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="user in users" :key="user.id">
          <td>{{ user.id }}</td>
          <td>{{ user.email }}</td>
          <td>
            <select v-model="user.is_active" @change="openModal('update', user.id, { is_active: user.is_active, is_staff: user.is_staff })">
              <option :value="true">Yes</option>
              <option :value="false">No</option>
            </select>
          </td>
          <td>
            <select v-model="user.is_staff" @change="openModal('update', user.id, { is_active: user.is_active, is_staff: user.is_staff })">
              <option :value="true">Admin</option>
              <option :value="false">User</option>
            </select>
          </td>
          <td>
            <button @click="openModal('delete', user.id)">Delete</button>
          </td>
        </tr>
      </tbody>
    </table>

    <!-- Custom Modal for Confirmation -->
    <div v-if="showModal" class="modal-overlay">
      <div class="modal">
        <h3>Confirm Action</h3>
        <p v-if="modalAction === 'delete'">Are you sure you want to delete this user?</p>
        <p v-if="modalAction === 'update'">Are you sure you want to update this user's status?</p>
        <div class="modal-buttons">
          <button @click="confirmAction" class="confirm-btn">Confirm</button>
          <button @click="showModal = false" class="cancel-btn">Cancel</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.admin-container {
  max-width: 800px;
  margin: auto;
  text-align: center;
  padding: 2rem;
}
table {
  width: 100%;
  border-collapse: collapse;
}
th, td {
  border: 1px solid #ddd;
  padding: 8px;
  text-align: center;
}
th {
  background-color: #42b883;
  color: white;
}
button {
  background-color: red;
  color: white;
  border: none;
  padding: 5px 10px;
  cursor: pointer;
}
select {
  padding: 5px;
  border-radius: 5px;
}
.success {
  color: green;
  margin-top: 10px;
}
.error {
  color: red;
  margin-top: 10px;
}

/* Custom Modal Styling */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
}
.modal {
  background: white;
  padding: 20px;
  border-radius: 8px;
  text-align: center;
}
.modal-buttons {
  display: flex;
  justify-content: space-around;
  margin-top: 10px;
}
.confirm-btn {
  background-color: #42b883;
  color: white;
  border: none;
  padding: 10px 15px;
  cursor: pointer;
}
.cancel-btn {
  background-color: #e63946;
  color: white;
  border: none;
  padding: 10px 15px;
  cursor: pointer;
}
</style>