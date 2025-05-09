<template>
  <v-container class="d-flex justify-center">
    <v-card class="profile-card" elevation="4">
      <v-card-title class="text-h5 text-center">Edit Profile</v-card-title>
      <v-card-text>
        <!-- Profile Picture Upload -->
        <v-row align="center" justify="center">
          <v-avatar size="120">
            <v-img :src="previewAvatar || user.avatar" alt="User Avatar"></v-img>
          </v-avatar>
        </v-row>
        <v-row justify="center">
          <v-file-input
              label="Upload Profile Picture"
              accept="image/*"
              prepend-icon="mdi-camera"
              @change="handleAvatarUpload"
          ></v-file-input>
        </v-row>

        <!-- Profile Information -->
        <v-form ref="profileForm">
          <v-text-field v-model="user.name" label="Name" outlined></v-text-field>
          <v-text-field v-model="user.email" label="Email" type="email" outlined></v-text-field>
          <v-textarea v-model="user.bio" label="Bio" outlined></v-textarea>
        </v-form>

        <!-- Mock Settings -->
        <v-divider class="my-4"></v-divider>
        <v-list-subheader>Settings</v-list-subheader>
        <v-switch v-model="settings.darkMode" label="Dark Mode"></v-switch>
        <v-switch v-model="settings.notifications" label="Enable Notifications"></v-switch>

        <!-- Action Buttons -->
        <v-row justify="center" class="mt-4">
          <v-btn color="primary" @click="saveProfile">Save</v-btn>
          <v-btn color="grey" class="ml-2" @click="resetProfile">Cancel</v-btn>
        </v-row>
      </v-card-text>
    </v-card>
  </v-container>
</template>

<script setup>
import { ref } from 'vue';

const user = ref({
  name: 'John Doe',
  email: 'john.doe@example.com',
  bio: 'Software Engineer passionate about AI and CAD systems.',
  avatar: 'https://randomuser.me/api/portraits/men/45.jpg', // Mock profile image
});

const settings = ref({
  darkMode: false,
  notifications: true,
});

const previewAvatar = ref(null);

const handleAvatarUpload = (event) => {
  const file = event.target.files[0];
  if (file) {
    const reader = new FileReader();
    reader.onload = () => {
      previewAvatar.value = reader.result;
    };
    reader.readAsDataURL(file);
  }
};

const saveProfile = () => {
  alert('Profile saved!');
};

const resetProfile = () => {
  alert('Changes discarded!');
  previewAvatar.value = null;
};
</script>

<style scoped>
.profile-card {
  max-width: 450px;
  padding: 20px;
  border-radius: 12px;
}
</style>