import {createRouter, createWebHistory} from 'vue-router'
import Dashboard from '@/components/Dashboard.vue'
import PublicLayout from "@/layout/PublicLayout.vue";
import LoginComponent from "@/components/LoginComponent.vue";
import AuthLayout from "@/layout/AuthLayout.vue";
import {supabase} from "@/services/supabase-service.js";

// Import the new components
import CodeWithGenAI from '@/components/CodeWithGenAI.vue';
import BookmarkPage from '@/components/BookmarkPage.vue';
import StudentDashboard from '@/components/StudyWithGenAI.vue';
import SeekComponent from "@/components/SeekComponent.vue";
import ProfileComponent from "@/components/ProfileComponent.vue";
import SettingsComponent from "@/components/SettingsComponent.vue";
import TeacherDashboard from "@/components/TeacherDashboard.vue";
import AdministratorComponent from "@/components/AdministratorComponent.vue";
import Dashboard2 from "@/components/Dashboard2.vue";

const routes = [

    {
        path: "/dashboard",
        component: AuthLayout,
        children: [
            {path: "", component: Dashboard},
            {path: "/code", component: CodeWithGenAI},
            {path: "/bookmarks", component: BookmarkPage},
            {path: "/course", component: SeekComponent},
            {
                path: "/study",
                name: 'studywithgenAI',
                component: StudentDashboard,  // No layout wrapper, directly render the component
            },
            {path: "/profile", component: ProfileComponent},
            {path: "/settings", component: SettingsComponent},
            {path: "/tdashboard", component: TeacherDashboard},
            {path: "/adashboard", component: AdministratorComponent},
            {path: "/dashboard2", component: Dashboard2},

        ],
        meta: {requiresAuth: true},
    },

    {
        path: "/",
        component: PublicLayout,
        // redirect: "/login",
        children: [
            {path: "login", component: LoginComponent},
        ],

        beforeEnter: async (to, from, next) => {
            const {data} = await supabase.auth.getSession();
            const isAuthenticated = data?.session?.user;
            if (isAuthenticated && to.path === "/login") {
                next("/dashboard");
            } else {
                next();
            }
        },
    },
]

const router = createRouter({
    history: createWebHistory(),
    routes
})
const isAuthenticated = async () => {
    const token = localStorage.getItem("token");

    if (!token) return false; // ❌ No token, user is not authenticated

    return true
};
// **Route Guard to Protect Auth Routes**
router.beforeEach(async (to, from, next) => {
    const authenticated = isAuthenticated()

    if (to.path === "/" && authenticated) {
        next("/dashboard");
    } else if (to?.meta?.requiresAuth && !authenticated) {
        next("/login");
    } else {
        next();
    }
});

export default router
