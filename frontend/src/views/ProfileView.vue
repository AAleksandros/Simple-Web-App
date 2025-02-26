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

// For profile's country field
const profileSelectedCountry = ref(countryList.value[0]);

const updatePhoneNumber = () => {
  if (phoneNumberWithoutCode.value) {
    profile.value.phone_number = `${phoneNumberSelectedCountry.value.phoneCode} ${phoneNumberWithoutCode.value.trim()}`;
  } else {
    profile.value.phone_number = "";
  }
  isEditing.value = true;
};

const handlePhoneNumberInput = () => {
  phoneNumberWithoutCode.value = phoneNumberWithoutCode.value.replace(/[^0-9-\s]/g, "");
  errorMessage.value = "";
  isEditing.value = true;
};

const sanitizeName = (value: string) => {
  isEditing.value = true;
  return value.replace(/[^A-Za-zÀ-ÖØ-öø-ÿ\s-]/g, "");
};

const sanitizeCity = (value: string) => {
  isEditing.value = true;
  return value.replace(/[^A-Za-zÀ-ÖØ-öø-ÿ\s-]/g, "");
};

const sanitizeAddress = () => {
  isEditing.value = true;
  profile.value.address = profile.value.address.replace(/[^a-zA-Z0-9\s,.-]/g, "");
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
      const k = key as keyof typeof profile.value;
      if (profile.value[k] == null) {
        profile.value[k] = "";
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

    const foundCountry = countryList.value.find(c => c.name === profile.value.country);
    profileSelectedCountry.value = foundCountry || countryList.value[0];

    // Determine if this is a first-time user
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
  // Trim all string fields
  Object.keys(profile.value).forEach((key) => {
    const k = key as keyof typeof profile.value;
    if (typeof profile.value[k] === "string") {
      profile.value[k] = profile.value[k].trim();
    }
  });

  // Set profile country from the dropdown
  profile.value.country = profileSelectedCountry.value.name;

  if (
    !profile.value.first_name ||
    !profile.value.last_name ||
    !profile.value.phone_number ||
    !profile.value.country ||
    !profile.value.city ||
    !profile.value.address
  ) {
    errorMessage.value = "All fields must be filled in.";
    return;
  }

  if (
    !validateName(profile.value.first_name) ||
    !validateName(profile.value.last_name)
  ) {
    return;
  }

  if (!validateCity()) return;

  sanitizeAddress();

  if (!isPhoneNumberValid()) return;

  try {
    // Update phone number using selected country code
    profile.value.phone_number = `${phoneNumberSelectedCountry.value.phoneCode} ${phoneNumberWithoutCode.value.trim()}`;

    await api.put("profile/", profile.value);
    successMessage.value = "Profile updated successfully!";
    isEditing.value = false;
    isFirstTimeUser.value = false;
    
    // Update localStorage with new profile data
    localStorage.setItem("profile", JSON.stringify(profile.value));
    // **New:** update originalProfile to the newly saved data
    originalProfile.value = { ...profile.value };

    setTimeout(() => {
      successMessage.value = "";
    }, 5000);
  } catch (error) {
    errorMessage.value = "Failed to update profile.";
  }
};

const cancelEdit = () => {
  // Reset the main profile data
  profile.value = { ...originalProfile.value };
  isEditing.value = false;

  const phoneParts = profile.value.phone_number.match(/^(\+\d{1,4})\s?(.*)$/);
  if (phoneParts) {
    phoneNumberSelectedCountry.value =
      countryList.value.find(c => c.phoneCode === phoneParts[1]) || countryList.value[0];
    phoneNumberWithoutCode.value = phoneParts[2] || "";
  } else {
    phoneNumberSelectedCountry.value = countryList.value[0];
    phoneNumberWithoutCode.value = "";
  }

  // Reset the profile country dropdown
  const foundCountry = countryList.value.find(c => c.name === profile.value.country);
  profileSelectedCountry.value = foundCountry || countryList.value[0];
};

onMounted(fetchProfile);
</script>

<template>
  <div class="pt-30 pb-30 flex items-center justify-center px-4 bg-cover bg-center overflow-y-auto"
       style="background-image: url('/background.png'); background-attachment: fixed;">
    
    <div class="bg-white/30 backdrop-blur-lg p-8 rounded-lg shadow-lg max-w-md w-full border border-white/20">
      <h1 class="text-center text-2xl font-bold text-white sm:text-3xl">User Profile</h1>

      <!-- Prompt for first-time users -->
      <div v-if="isFirstTimeUser" class="w-full text-center mt-2 bg-black/60 backdrop-blur-md px-4 py-2 rounded">
        <p class="text-yellow-400 text-s">
          Please complete your profile information before continuing.
        </p>
      </div>

      <!-- Success Message -->
      <div v-if="successMessage" class="w-full text-center mt-2 bg-black/60 backdrop-blur-md px-4 py-2 rounded">
        <p class="text-green-400 text-s">
          {{ successMessage }}
        </p>
      </div>

      <!-- Error Message -->
      <div v-if="errorMessage" class="w-full text-center mt-2 bg-black/60 backdrop-blur-md px-4 py-2 rounded">
        <p class="text-red-500 text-s">
          {{ errorMessage }}
        </p>
      </div>

      <form @submit.prevent="saveProfile" class="mt-6 space-y-4">
        <!-- First Name -->
        <div>
          <label for="firstName" class="sr-only">First Name</label>
          <input
            id="firstName"
            type="text"
            v-model="profile.first_name"
            @input="profile.first_name = sanitizeName(profile.first_name); errorMessage = ''; isEditing = true"
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
            @input="profile.last_name = sanitizeName(profile.last_name); errorMessage = ''; isEditing = true"
            placeholder="Last Name"
            class="w-full rounded-lg border-gray-300 p-3 text-sm bg-white/80 text-black"
            required
          />
        </div>

        <!-- Email -->
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
            @change="updatePhoneNumber(); isEditing = true"
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
            @input="updatePhoneNumber(); handlePhoneNumberInput(); errorMessage = ''; isEditing = true"
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
            @change="isEditing = true"
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
            @input="profile.city = sanitizeCity(profile.city); errorMessage = ''; isEditing = true"
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
            @input="sanitizeAddress(); errorMessage = ''; isEditing = true"
            placeholder="Address"
            class="w-full rounded-lg border-gray-300 p-3 text-sm bg-white/80 text-black"
            required
          ></textarea>
        </div>

        <!-- Buttons: Save, Cancel (appear only when editing) -->
        <div v-if="isEditing" class="flex space-x-2">
          <button
            type="submit"
            class="w-full rounded-lg bg-green-500 px-5 py-3 text-sm font-medium text-white hover:bg-green-600 transition"
          >
            Save
          </button>
          <button
            type="button"
            @click="cancelEdit"
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

button:hover {
  opacity: 0.8;
}

.text-yellow-400 {
  font-size: 0.9rem;
  text-align: center;
}
</style>