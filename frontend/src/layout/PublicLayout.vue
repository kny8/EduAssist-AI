<template>

  <v-container fluid class="fill-height d-flex align-center justify-center pre-login-container">
    <v-row class="move-above-section">
      <!-- Left Section (Background + Welcome Message) -->
      <v-col cols="12" md="6" class="welcome-section">
        <div class="welcome-content">
          <h1 >RAG Project</h1>
          <p>Team 44</p>
        </div>
      </v-col>

      <!-- Right Section (Login Form) -->
      <v-col cols="12" md="6" >
        <router-view/>
      </v-col>
    </v-row>
  </v-container>

</template>

<script>


export default {};
</script>
<style scoped>

/* Login container: split layout */
.pre-login-container {
  display: flex;
  justify-content: center;
  background-size: cover;
  background-image: url('https://plus.unsplash.com/premium_photo-1683121710572-7723bd2e235d?q=80&w=1932&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D'); /* Replace with actual image URL */
}

.pre-login-container::before {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5); /* Black overlay with 50% opacity */
  z-index: 1; /* Ensure the overlay is on top of the background */
}

/* Left side (background image) */
.welcome-section {
  //color: white;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* Welcome message styles */
.welcome-content {
  text-align: center;
  background: black;
  color: white;
  padding: 50px;
  opacity: 80%;
}

.move-above-section {
  position: relative;
  z-index: 2; /* This ensures the form (router-view) is on top of the background overlay */
  opacity: 100%;
}
</style>
