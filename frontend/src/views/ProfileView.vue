<script setup lang="ts">
import { ref, onMounted, computed } from "vue";
import api from "../api";
import { useAuthStore } from "../stores/auth";
import { countries } from "countries-list";
import { parsePhoneNumberFromString } from "libphonenumber-js";

const authStore = useAuthStore();

const profile = ref({
  email: authStore.user?.email || "",
  first_name: "",
  last_name: "",
  phone_number: "",
  country: "",
  city: "",
  address: "",
});

const isEditing = ref(false);
const errorMessage = ref("");
const successMessage = ref("");

const countryList = computed(() =>
  Object.entries(countries)
    .map(([code, data]) => ({
      name: data.name,
      code,
      phoneCode: data.phone ? `+${data.phone}` : "",
    }))
    .sort((a, b) => a.name.localeCompare(b.name))
);

const selectedCountry = ref(countryList.value.find(c => c.name === profile.value.country) || countryList.value[0]);
const phoneNumberWithoutCode = ref("");

const updatePhoneNumber = () => {
  if (phoneNumberWithoutCode.value) {
    profile.value.phone_number = `${selectedCountry.value.phoneCode} ${phoneNumberWithoutCode.value.trim()}`;
  }
};

const fetchProfile = async () => {
  try {
    const cachedProfile = localStorage.getItem("profile");

    if (cachedProfile) {
      console.log("Using cached profile data.");
      profile.value = JSON.parse(cachedProfile);

      selectedCountry.value = countryList.value.find(c => c.name === profile.value.country) || countryList.value[0];

      phoneNumberWithoutCode.value = profile.value.phone_number.replace(profile.value.phone_number.match(/^\+\d{1,4}\s?/)?.[0] || "", "").trim();
      return;
    }

    console.log("Fetching profile from API.");
    const response = await api.get("profile/");
    profile.value = response.data;

    localStorage.setItem("profile", JSON.stringify(profile.value));

    selectedCountry.value = countryList.value.find(c => c.name === profile.value.country) || countryList.value[0];

    phoneNumberWithoutCode.value = profile.value.phone_number.replace(profile.value.phone_number.match(/^\+\d{1,4}\s?/)?.[0] || "", "").trim();
  } catch (error) {
    errorMessage.value = "Failed to load profile information.";
  }
};

const saveProfile = async () => {
  if (!profile.value.first_name || !profile.value.last_name || !profile.value.phone_number || !profile.value.country || !profile.value.city || !profile.value.address) {
    errorMessage.value = "All fields must be filled in.";
    return;
  }

  if (!validateName(profile.value.first_name) || !validateName(profile.value.last_name) || !validatePhoneNumberFormat() || !validateCity()) return;

  sanitizeAddress();

  try {
    await api.put("profile/", profile.value);
    successMessage.value = "Profile updated successfully!";
    isEditing.value = false;

    localStorage.setItem("profile", JSON.stringify(profile.value));
  } catch (error) {
    errorMessage.value = "Failed to update profile.";
  }
};

const validatePhoneNumberFormat = () => {
  const phoneRegex = /^[0-9-]+$/;
  if (!phoneRegex.test(phoneNumberWithoutCode.value)) {
    errorMessage.value = "Phone number can only contain numbers and dashes.";
    return false;
  }
  return true;
};

const validateName = (name: string) => {
  const nameRegex = /^[A-Za-zÀ-ÖØ-öø-ÿ\s-]+$/;
  if (!nameRegex.test(name)) {
    errorMessage.value = "First and Last name can only contain letters.";
    return false;
  }
  return true;
};

const validateCity = () => {
  const cityRegex = /^[A-Za-zÀ-ÖØ-öø-ÿ\s-]+$/;
  if (!cityRegex.test(profile.value.city)) {
    errorMessage.value = "City can only contain letters.";
    return false;
  }
  return true;
};

const sanitizeAddress = () => {
  profile.value.address = profile.value.address.replace(/[^a-zA-Z0-9\s,.-]/g, "");
};

onMounted(fetchProfile);
</script>

<template>
  <div class="profile-container">
    <h2>User Profile</h2>

    <p v-if="successMessage" class="success">{{ successMessage }}</p>
    <p v-if="errorMessage" class="error">{{ errorMessage }}</p>

    <div class="profile-form">
      <label>First Name:</label>
      <input type="text" v-model="profile.first_name" :disabled="!isEditing" />

      <label>Last Name:</label>
      <input type="text" v-model="profile.last_name" :disabled="!isEditing" />

      <label>Email:</label>
      <input type="email" v-model="profile.email" disabled />

      <label>Phone Number:</label>
      <div class="phone-input">
        <select v-model="selectedCountry" @change="updatePhoneNumber" :disabled="!isEditing">
          <option v-for="country in countryList" :key="country.code" :value="country">
            {{ country.name }} ({{ country.phoneCode }})
          </option>
        </select>
        <input
          type="text"
          v-model="phoneNumberWithoutCode"
          @input="updatePhoneNumber"
          :disabled="!isEditing"
          placeholder="Enter your number"
        />
      </div>

      <label>Country:</label>
      <select v-model="profile.country" :disabled="!isEditing">
        <option v-for="country in countryList" :key="country.name" :value="country.name">
          {{ country.name }}
        </option>
      </select>

      <label>City:</label>
      <input type="text" v-model="profile.city" :disabled="!isEditing" />

      <label>Address:</label>
      <textarea v-model="profile.address" :disabled="!isEditing"></textarea>

      <div class="button-group">
        <button v-if="!isEditing" @click="isEditing = true" class="edit-btn">Edit</button>
        <button v-if="isEditing" @click="saveProfile" class="save-btn">Save</button>
        <button v-if="isEditing" @click="fetchProfile" class="cancel-btn">Cancel</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.profile-container {
  max-width: 500px;
  margin: auto;
  padding: 2rem;
  background: #1e1e1e;
  color: white;
  border-radius: 8px;
  box-shadow: 0px 0px 10px rgba(255, 255, 255, 0.2);
}

label {
  margin-top: 10px;
  font-size: 1rem;
  font-weight: bold;
}

select, input, textarea {
  width: 100%;
  padding: 10px;
  margin-top: 5px;
  border-radius: 5px;
  background: #2e2e2e;
  color: white;
}

.phone-input {
  display: flex;
  gap: 5px;
}

.phone-input select {
  width: 40%;
}

.phone-input input {
  width: 60%;
}

.button-group {
  display: flex;
  justify-content: space-between;
  margin-top: 15px;
}

.edit-btn {
  background: #007bff;
  color: white;
}

.save-btn {
  background: #28a745;
  color: white;
}

.cancel-btn {
  background: #e63946;
  color: white;
}

button:hover {
  opacity: 0.8;
}

.success {
  color: green;
  text-align: center;
}

.error {
  color: red;
  text-align: center;
}
</style>