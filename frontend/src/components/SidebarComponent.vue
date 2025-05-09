<template>

  <v-card
      class="mx-auto"
      max-width="300"
  >
    <v-navigation-drawer
        v-model="drawer"
        location="start"
        permanent
        :width="isCollapsed ? 80 : 250"
        :height="100"
        theme="dark"
    >
      <v-list>
        <v-list-item
            prepend-avatar="https://cdn.vuetifyjs.com/images/john.png"
            @click="toggleSidebar"
        >
          <v-list-item-title>
            {{ currentUser?.name || 'Guest' }}
          </v-list-item-title>
          <v-list-item-subtitle>
            {{ currentUser?.email || '' }}
          </v-list-item-subtitle>
          <template v-slot:append>
            <v-btn size="small" variant="text">
              <v-icon>{{ isCollapsed ? mdiChevronRight() : mdiChevronLeft() }}</v-icon>
            </v-btn>
          </template>
        </v-list-item>
      </v-list>

      <v-divider></v-divider>

      <v-list density="compact" nav :lines="false">
        <v-list-item
            v-for="(item, i) in filteredMenuItems"
            :key="i"
            :value="item"
            color="secondary"
            @click="navigateTo(item)"
            :class="{'logout-item': item.title === 'Logout'}"
        >
          <template v-slot:prepend>
            <v-icon :icon="item.icon"></v-icon>
          </template>

          <v-list-item-title v-text="item.title" class="text-start"></v-list-item-title>
        </v-list-item>
      </v-list>
      <!-- Toggle button to collapse/expand the sidebar -->
      <!--    <v-btn icon @click="toggleSidebar" class="mt-5">-->
      <!--      <v-icon>{{ isCollapsed ? 'mdi-chevron-right' : 'mdi-chevron-left' }}</v-icon>-->
      <!--    </v-btn>-->
    </v-navigation-drawer>
  </v-card>
</template>

<script>

import {supabase} from "@/services/supabase-service.js";
import {
  mdiAbacus,
  mdiAccount,
  mdiBookmark,
  mdiChevronLeft,
  mdiChevronRight,
  mdiCodeTags,
  mdiLogout,
  mdiNotebookOutline,
  mdiSchool, mdiSettingsHelper,
  mdiViewDashboardEditOutline,
} from "@mdi/js";

export default {
  name: "SidebarComponent",
  data() {
    return {
      drawer: true, // Sidebar visibility
      isCollapsed: false, // Sidebar collapsed state
      currentUser: null,
      currentRole: null,
      studentMenuItems: [
        // {title: 'Dashboard', icon: mdiViewDashboardEditOutline, path: '/dashboard'},
        {title: 'Dashboard', icon: mdiViewDashboardEditOutline, path: '/dashboard2'},
        {title: "Study With GenAI", icon: mdiNotebookOutline, path: "/study"}, // Notebook icon
        {title: "Code With GenAI", icon: mdiCodeTags, path: "/code"}, // Code icon
        {title: "Bookmarks", icon: mdiBookmark, path: "/bookmarks"}, // Bookmark icon
        {title: "Course Page", icon: mdiSchool, path: "/course"}, // School/education icon
        {title: "Profile", icon: mdiAccount, path: "/profile"}, // User profile icon
        {title: "Settings", icon: mdiAbacus, path: "/settings"}, // User profile icon
        {title: "Logout", icon: mdiLogout, path: "/logout"}, // Logout icon
      ],
      teacherMenuItems: [
        {title: 'Teacher Dashboard', icon: mdiViewDashboardEditOutline, path: '/tdashboard'},
        {title: "Course Page", icon: mdiSchool, path: "/course"}, // School/education icon
        {title: "Profile", icon: mdiAccount, path: "/profile"}, // User profile icon
        {title: "Settings", icon: mdiAbacus, path: "/settings"}, // User profile icon
        {title: "Logout", icon: mdiLogout, path: "/logout"}, // Logout icon
      ],
      adminMenuItems: [
        {title: 'Administrator Dashboard', icon: mdiViewDashboardEditOutline, path: '/adashboard'},
        {title: "Course Page", icon: mdiSchool, path: "/course"}, // School/education icon
        {title: "Profile", icon: mdiAccount, path: "/profile"}, // User profile icon
        {title: "Settings", icon: mdiAbacus, path: "/settings"}, // User profile icon
        {title: "Logout", icon: mdiLogout, path: "/logout"}, // Logout icon
      ]
    };
  },
  methods: {
    mdiChevronLeft() {
      return mdiChevronLeft
    },
    mdiChevronRight() {
      return mdiChevronRight
    },

    toggleSidebar() {
      this.isCollapsed = !this.isCollapsed; // Collapse/Expand Sidebar
      this.emitToggle(); // Emit the toggle event
    },
    emitToggle() {
      this.$emit('toggle', this.isCollapsed);
    },
    async navigateTo(item) {
      if (item.title === 'Logout') {
        await this.logoutUser() // Navigate to the selected path

      } else {

        await this.$router.push(item.path); // Navigate to the selected path
      }
    },
    async logoutUser() {
      try {
        // await supabase.auth.signOut();
        localStorage.clear()
        this.$router.push('/login'); // Redirect to login page after logout
      } catch (error) {
        console.error('Logout failed:', error); // Handle errors gracefully
      }
    },
    getUser() {
      const user = localStorage.getItem("user");
      this.currentUser = user ? JSON.parse(user) : null;
      if (this.currentUser) {
        this.currentRole = this.currentUser['role'] ?? 'student'
      }
    },
  },
  computed: {
    filteredMenuItems() {
      if (this.currentRole === 'student') {
        return this.studentMenuItems;
      } else if (this.currentRole === 'teacher') {
        return this.teacherMenuItems;
      } else if (this.currentRole === 'admin') {
        return this.adminMenuItems
      }
      return this.studentMenuItems
    },
  },
  mounted() {
    this.getUser();
  }

};
</script>

<style scoped>

</style>