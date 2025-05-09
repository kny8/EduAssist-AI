<template>
  <div class="post-login-layout">
    <div class="main-container">
      <SidebarComponent :is-collapsed="isSidebarCollapsed" @toggle="toggleSidebar" style="z-index: 1000"/>
      <div :class="{'content': true, 'content-collapsed': isSidebarCollapsed,'content-expanded': !isSidebarCollapsed}">
        <router-view/>
      </div>
    </div>
  </div>
</template>

<script>
// import FooterComponent from "@/components/FooterComponent.vue";
import SidebarComponent from "@/components/SidebarComponent.vue";
// import NotificationComponent from "@/components/NotificationComponent.vue";

export default {
  components: {
    SidebarComponent,
  },
  data() {
    return {
      isSidebarCollapsed: false, // Sidebar starts collapsed
    };
  },
  methods: {
    toggleSidebar(collapsed) {
      this.isSidebarCollapsed = collapsed;
    },
  },
};
</script>
<style scoped>
/* Main container */
.main-container {
  display: flex;
  flex-direction: row;
}

/* Content area - adjusts based on sidebar state */
.content {
  flex-grow: 1;
  transition: padding-left 0.3s ease;
}

.content-collapsed {
  padding-left: 80px; /* Adjust for collapsed sidebar */
}

.content-expanded {
  padding-left: 250px; /* Adjust for expanded sidebar */
}
</style>