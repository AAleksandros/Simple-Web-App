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
const isFirstTimeUser = ref(false);

// Create a country list for both dropdowns
const countryList = computed(() =>
  Object.entries(countries)
    .map(([code, data]) => ({
      name: data.name,
      code,
      phoneCode: `+${data.phone || ""}`,
    }))
    .sort((a, b) => a.name.localeCompare(b.name))
);

// Backup original profile for canceling changes
const originalProfile = ref({ ...profile.value });

// For phone number's country code dropdown
const phoneNumberSelectedCountry = ref(countryList.value[0]);
const phoneNumberWithoutCode = ref("");

// For profile's country field (separate dropdown)
const profileSelectedCountry = ref(countryList.value[0]);

const updatePhoneNumber = () => {
  if (phoneNumberWithoutCode.value) {
    profile.value.phone_number = `${phoneNumberSelectedCountry.value.phoneCode} ${phoneNumberWithoutCode.value.trim()}`;
  } else {
    profile.value.phone_number = "";
  }
};

// Restrict phone input to digits, dashes, spaces
const handlePhoneNumberInput = () => {
  phoneNumberWithoutCode.value = phoneNumberWithoutCode.value.replace(/[^0-9-\s]/g, "");
  errorMessage.value = "";
};

// Sanitize name: allow only letters, spaces, dashes
const sanitizeName = (value: string) => {
  return value.replace(/[^A-Za-zÀ-ÖØ-öø-ÿ\s-]/g, "");
};

// Sanitize city: allow only letters, spaces, dashes
const sanitizeCity = (value: string) => {
  return value.replace(/[^A-Za-zÀ-ÖØ-öø-ÿ\s-]/g, "");
};

// Sanitize address: allow only letters, numbers, spaces, commas, periods, dashes
const sanitizeAddress = () => {
  profile.value.address = profile.value.address.replace(/[^a-zA-Z0-9\s,.-]/g, "");
};

// Validate name fields
const validateName = (name: string) => {
  const nameRegex = /^[A-Za-zÀ-ÖØ-öø-ÿ\s-]+$/;
  if (!nameRegex.test(name)) {
    errorMessage.value = "First and Last name can only contain letters.";
    return false;
  }
  return true;
};

// Validate city field
const validateCity = () => {
  const cityRegex = /^[A-Za-zÀ-ÖØ-öø-ÿ\s-]+$/;
  if (!cityRegex.test(profile.value.city)) {
    errorMessage.value = "City can only contain letters.";
    return false;
  }
  return true;
};

// Validate phone number using libphonenumber-js
const isPhoneNumberValid = () => {
  if (!phoneNumberWithoutCode.value) return false;
  const fullNumber = `${phoneNumberSelectedCountry.value.phoneCode} ${phoneNumberWithoutCode.value.trim()}`;
  const parsedNumber = parsePhoneNumberFromString(fullNumber);
  if (!parsedNumber) {
    errorMessage.value = "Invalid phone number format.";
    return false;
  }
  if (!parsedNumber.isValid()) {
    errorMessage.value = "Phone number is not valid for the selected country.";
    return false;
  }
  errorMessage.value = "";
  return true;
};

const fetchProfile = async () => {
  try {
    const cachedProfile = localStorage.getItem("profile");

    if (cachedProfile) {
      console.log("Using cached profile data.");
      profile.value = JSON.parse(cachedProfile);
    } else {
      console.log("Fetching profile from API.");
      const response = await api.get("profile/");
      profile.value = response.data;
      localStorage.setItem("profile", JSON.stringify(profile.value));
    }

    // Ensure each field is a string
    Object.keys(profile.value).forEach((key) => {
      if (profile.value[key] == null) {
        profile.value[key] = "";
      }
    });

    originalProfile.value = { ...profile.value };

    // Split phone_number into country code and local number
    const phoneParts = profile.value.phone_number.match(/^(\+\d{1,4})\s?(.*)$/);
    if (phoneParts) {
      const phoneCode = phoneParts[1];
      phoneNumberSelectedCountry.value = countryList.value.find(c => c.phoneCode === phoneCode) || countryList.value[0];
      phoneNumberWithoutCode.value = phoneParts[2] || "";
    } else {
      phoneNumberSelectedCountry.value = countryList.value[0];
      phoneNumberWithoutCode.value = "";
    }

    // Set profile country based on stored value (if any)
    const foundCountry = countryList.value.find(c => c.name === profile.value.country);
    profileSelectedCountry.value = foundCountry || countryList.value[0];

    // Determine if this is a first-time user (fields are empty except email)
    isFirstTimeUser.value = !profile.value.first_name.trim() &&
                            !profile.value.last_name.trim() &&
                            !profile.value.phone_number.trim() &&
                            !profile.value.country.trim() &&
                            !profile.value.city.trim() &&
                            !profile.value.address.trim();
  } catch (error) {
    if (!isFirstTimeUser.value) {
      errorMessage.value = "Failed to load profile information.";
    }
  }
};

const saveProfile = async () => {
  // Trim all fields
  Object.keys(profile.value).forEach((key) => {
    if (typeof profile.value[key] === "string") {
      profile.value[key] = profile.value[key].trim();
    }
  });

  // Set profile country from the profile country dropdown
  profile.value.country = profileSelectedCountry.value.name;

  if (!profile.value.first_name ||
      !profile.value.last_name ||
      !profile.value.phone_number ||
      !profile.value.country ||
      !profile.value.city ||
      !profile.value.address) {
    errorMessage.value = "All fields must be filled in.";
    return;
  }

  if (!validateName(profile.value.first_name) ||
      !validateName(profile.value.last_name)) {
    return;
  }

  if (!validateCity()) return;

  sanitizeAddress();

  if (!isPhoneNumberValid()) return;

  try {
    profile.value.phone_number = `${phoneNumberSelectedCountry.value.phoneCode} ${phoneNumberWithoutCode.value.trim()}`;

    await api.put("profile/", profile.value);
    successMessage.value = "Profile updated successfully!";
    isEditing.value = false;
    // Remove the first-time user prompt after saving
    isFirstTimeUser.value = false;
    localStorage.setItem("profile", JSON.stringify(profile.value));

    setTimeout(() => {
      successMessage.value = "";
    }, 5000);
  } catch (error) {
    errorMessage.value = "Failed to update profile.";
  }
};

const cancelEdit = () => {
  profile.value = { ...originalProfile.value };
  isEditing.value = false;
};

onMounted(fetchProfile);
</script>

<template>
  <div class="h-screen flex items-center justify-center px-4 bg-cover bg-center overflow-hidden"
       style="background-image: url('/background.png'); background-attachment: fixed;">
    
    <div class="bg-white/30 backdrop-blur-lg p-8 rounded-lg shadow-lg max-w-md w-full border border-white/20">
      <h1 class="text-center text-2xl font-bold text-white sm:text-3xl">User Profile</h1>

      <!-- Prompt for first-time users -->
      <p v-if="isFirstTimeUser" class="text-center text-yellow-400 text-sm mt-2">
        Please complete your profile information before continuing.
      </p>

      <!-- Success and error messages -->
      <p v-if="successMessage" class="text-center text-green-400 text-sm mt-2">{{ successMessage }}</p>
      <p v-if="errorMessage" class="text-center text-red-400 text-sm mt-2">{{ errorMessage }}</p>

      <form @submit.prevent="saveProfile" class="mt-6 space-y-4">
        <!-- First Name -->
        <div>
          <label for="firstName" class="sr-only">First Name</label>
          <input
            id="firstName"
            type="text"
            v-model="profile.first_name"
            @input="profile.first_name = sanitizeName(profile.first_name); errorMessage = ''"
            :disabled="!isEditing"
            placeholder="First Name"
            class="w-full rounded-lg border-gray-300 p-3 text-sm bg-white/80 text-black"
            required
          />
        </div>

        <!-- Last Name -->
        <div>
          <label for="lastName" class="sr-only">Last Name</label>
          <input
            id="lastName"
            type="text"
            v-model="profile.last_name"
            @input="profile.last_name = sanitizeName(profile.last_name); errorMessage = ''"
            :disabled="!isEditing"
            placeholder="Last Name"
            class="w-full rounded-lg border-gray-300 p-3 text-sm bg-white/80 text-black"
            required
          />
        </div>

        <!-- Email (disabled) -->
        <div>
          <label for="email" class="sr-only">Email</label>
          <input
            id="email"
            type="email"
            v-model="profile.email"
            disabled
            placeholder="Email"
            class="w-full rounded-lg border-gray-300 p-3 text-sm bg-white/50 text-gray-500"
          />
        </div>

        <!-- Phone Number with separate Country Code -->
        <div class="flex space-x-2">
          <!-- Phone Code Dropdown -->
          <select
            v-model="phoneNumberSelectedCountry"
            @change="updatePhoneNumber"
            :disabled="!isEditing"
            class="w-1/3 rounded-lg border-gray-300 p-3 text-sm bg-white/80 text-black"
          >
            <option
              v-for="country in countryList"
              :key="country.code"
              :value="country"
            >
              {{ country.name }} ({{ country.phoneCode }})
            </option>
          </select>
          <!-- Local Phone Input -->
          <input
            type="text"
            v-model="phoneNumberWithoutCode"
            @input="updatePhoneNumber(); handlePhoneNumberInput(); errorMessage = ''"
            :disabled="!isEditing"
            placeholder="Phone Number"
            class="w-2/3 rounded-lg border-gray-300 p-3 text-sm bg-white/80 text-black"
            required
          />
        </div>

        <!-- Profile Country Dropdown -->
        <div>
          <label for="profileCountry" class="sr-only">Country</label>
          <select
            id="profileCountry"
            v-model="profileSelectedCountry"
            :disabled="!isEditing"
            class="w-full rounded-lg border-gray-300 p-3 text-sm bg-white/80 text-black"
            required
          >
            <option
              v-for="country in countryList"
              :key="country.code"
              :value="country"
            >
              {{ country.name }}
            </option>
          </select>
        </div>

        <!-- City -->
        <div>
          <label for="city" class="sr-only">City</label>
          <input
            id="city"
            type="text"
            v-model="profile.city"
            @input="profile.city = sanitizeCity(profile.city); errorMessage = ''"
            :disabled="!isEditing"
            placeholder="City"
            class="w-full rounded-lg border-gray-300 p-3 text-sm bg-white/80 text-black"
            required
          />
        </div>

        <!-- Address -->
        <div>
          <label for="address" class="sr-only">Address</label>
          <textarea
            id="address"
            v-model="profile.address"
            @input="sanitizeAddress(); errorMessage = ''"
            :disabled="!isEditing"
            placeholder="Address"
            class="w-full rounded-lg border-gray-300 p-3 text-sm bg-white/80 text-black"
            required
          ></textarea>
        </div>

        <!-- Buttons: Edit, Save, Cancel -->
        <div class="flex space-x-2">
          <button
            v-if="!isEditing"
            @click="isEditing = true"
            type="button"
            class="w-full rounded-lg bg-yellow-500 px-5 py-3 text-sm font-medium text-white hover:bg-yellow-600 transition"
          >
            Edit
          </button>
          <button
            v-if="isEditing"
            type="submit"
            class="w-full rounded-lg bg-green-500 px-5 py-3 text-sm font-medium text-white hover:bg-green-600 transition"
          >
            Save
          </button>
          <button
            v-if="isEditing"
            @click="cancelEdit"
            type="button"
            class="w-full rounded-lg bg-gray-500 px-5 py-3 text-sm font-medium text-white hover:bg-gray-600 transition"
          >
            Cancel
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<style scoped>
/* Input & Select Field Styling */
.input-field {
  width: 100%;
  padding: 10px;
  margin-top: 5px;
  border-radius: 5px;
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: none;
}

input:focus {
  outline: none;
  border-color: #ffffff;
  box-shadow: 0 0 0 2px #525252;
}

.input-field:disabled {
  opacity: 0.5;
}

.select-field {
  width: 100%;
  padding: 10px;
  border-radius: 5px;
  background: rgba(255, 255, 255, 0.2);
  color: white;
}

/* Buttons */
.edit-btn {
  background: #007bff;
  padding: 10px;
  border-radius: 5px;
  font-weight: bold;
}

.save-btn {
  background: #28a745;
  padding: 10px;
  border-radius: 5px;
  font-weight: bold;
}

.cancel-btn {
  background: #e63946;
  padding: 10px;
  border-radius: 5px;
  font-weight: bold;
}

/* Button Hover Effects */
button:hover {
  opacity: 0.8;
}

/* Message Styles */
.text-yellow-400 {
  font-size: 0.9rem;
  text-align: center;
}
</style>