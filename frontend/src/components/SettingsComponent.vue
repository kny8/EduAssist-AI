<template>
  <v-container>
    <v-card class="settings-card" elevation="4">
      <v-card-title class="text-h5">System Settings</v-card-title>
      <v-card-text>
        <v-form ref="settingsForm">
          <!-- API Configuration -->
          <v-divider class="my-4"></v-divider>
          <v-list-subheader>API Configuration</v-list-subheader>
          <v-text-field v-model="settings.apiBaseUrl" label="API Base URL" outlined></v-text-field>
          <v-text-field v-model="settings.apiKey" label="API Key" type="password" outlined></v-text-field>

          <!-- Model Settings -->
          <v-divider class="my-4"></v-divider>
          <v-list-subheader>Model Settings</v-list-subheader>
          <v-select
              v-model="settings.selectedModel"
              :items="availableModels"
              label="Select AI Model"
              outlined
          ></v-select>
          <v-slider
              v-model="settings.temperature"
              label="Temperature (Randomness)"
              min="0"
              max="1"
              step="0.1"
              thumb-label
          ></v-slider>
          <v-text-field v-model="settings.maxTokens" label="Max Tokens" type="number" outlined></v-text-field>

          <!-- User Preferences -->
          <v-divider class="my-4"></v-divider>
          <v-list-subheader>User Preferences</v-list-subheader>
          <v-switch v-model="settings.darkMode" label="Dark Mode"></v-switch>
          <v-switch v-model="settings.notifications" label="Enable Notifications"></v-switch>

          <!-- System Behavior -->
          <v-divider class="my-4"></v-divider>
          <v-list-subheader>System Behavior</v-list-subheader>
          <v-slider
              v-model="settings.responseSpeed"
              label="Response Speed"
              min="1"
              max="5"
              step="1"
              thumb-label
          ></v-slider>
          <v-switch v-model="settings.streamingMode" label="Enable Streaming Mode"></v-switch>

          <!-- Save & Reset Buttons -->
          <v-row justify="center" class="mt-4">
            <v-btn color="primary" @click="saveSettings">Save Settings</v-btn>
            <v-btn color="grey" class="ml-2" @click="resetSettings">Reset</v-btn>
          </v-row>
        </v-form>
      </v-card-text>
    </v-card>
  </v-container>
</template>

<script setup>
import { ref } from 'vue';

// Default settings
const settings = ref({
  apiBaseUrl: 'https://api.example.com/v1',
  apiKey: '',
  selectedModel: 'gpt-4',
  temperature: 0.7,
  maxTokens: 1000,
  darkMode: false,
  notifications: true,
  responseSpeed: 3,
  streamingMode: true,
});

// Available AI Models
const availableModels = ref(['gpt-3.5', 'gpt-4', 'gpt-4-turbo']);

// Save settings
const saveSettings = () => {
  alert('Settings saved successfully!');
};

// Reset settings
const resetSettings = () => {
  alert('Settings reset to default values.');
};
</script>

<style scoped>
.settings-card {
  max-width: 600px;
  margin: 0 auto;
  padding: 20px;
  border-radius: 12px;
}
</style>