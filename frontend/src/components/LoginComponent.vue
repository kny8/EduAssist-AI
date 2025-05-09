<template>
  <v-card class="elevation-3 login-card pa-6 fill-height">
    <div class="text-start">
      <h2>Hello!</h2>
      <h3 class="blue--text">{{ greeting }}</h3>
      <p>Login to Your Account</p>
    </div>

    <v-form @submit.prevent="loginUser">
      <v-text-field
          v-model="email"
          label="Email Address"
          type="email"
          required
          outlined
          class="mb-4"
      ></v-text-field>

      <v-text-field
          v-model="password"
          label="Password"
          type="password"
          required
          outlined
          class="mb-4"
      ></v-text-field>

      <v-row>
        <v-col cols="6">
          <v-checkbox label="Remember Me"/>
        </v-col>
        <v-col cols="6" class="text-right">
          <a href="#" class="blue--text">Forgot Password?</a>
        </v-col>
      </v-row>

      <v-btn class="mt-4" color="primary" block type="submit" height="50" :loading="loading">
        Submit
      </v-btn>
    </v-form>

    <div class="text-center mt-4">
      <a href="#" @click="gotoRegistration" class="blue--text">Create Account</a>
    </div>
  </v-card>
</template>

<script>
import {supabase} from "@/services/supabase-service";
import AuthService from "@/services/auth-service.js"; // ✅ Import Supabase client

export default {
  data() {
    return {
      email: "",
      password: "",
      greeting: "Welcome back!",
      loading: false,
    };
  },
  created() {
    this.setGreeting();
  },
  methods: {
    async loginUser() {
      this.loading = true;
      // try {
      // const {data, error} = await supabase.auth.signInWithPassword({
      //   email: this.email,
      //   password: this.password,
      // });
      //
      // if (error) throw error; // If login fails, throw an error
      //
      // console.log("Login successful:", data);
      //
      // document.cookie = `supabase_access_token=${data.session.access_token}; Secure; HttpOnly; SameSite=Strict; path=/`;
      //
      // // Store session details
      // localStorage.setItem("user", JSON.stringify(data.user));
      //
      // console.log("Login successful:", data);
      try {
        console.log('loginUser')
        await AuthService.login({
          email: this.email,
          password: this.password,
        });
        const user = await AuthService.getUser()


        if (user) {
          if (user.role === 'teacher') {
            this.$router.push('/tdashboard'); // Redirect to teacher's dashboard
          } else if (user.role === 'student') {
            this.$router.push('/dashboard2'); // Redirect to student's dashboard
          }
        }

        // Redirect to dashboard
        // this.$router.push("/dashboard");
      } catch (error) {
        console.error("Login failed:", error.message);
        alert(error.message); // Show an alert with error message
      } finally {
        this.loading = false;
      }
    },
    gotoRegistration() {
      this.$router.push("/register"); // Redirect to Register page
    },
    setGreeting() {
      const currentHour = new Date().getHours();
      if (currentHour >= 5 && currentHour < 12) {
        this.greeting = "Good Morning";
      } else if (currentHour >= 12 && currentHour < 18) {
        this.greeting = "Good Afternoon";
      } else {
        this.greeting = "Good Evening";
      }
    },
  },
};
</script>


<style scoped>

.welcome-content h1 {
  font-size: 36px;
  margin-bottom: 10px;
}

.welcome-content p {
  font-size: 18px;
  margin-bottom: 20px;
}

/* Right side (login form card) */
.login-card {
  max-width: 450px;
  border-radius: 8px;
}

/* Text alignments */
.text-start h2 {
  margin: 0;
  font-size: 28px;
}

.text-start h3 {
  margin: 0;
  font-size: 22px;
}

.blue--text {
  color: #007bff !important;
}

/* Center content for create account and forgot password */
.text-right {
  text-align: right;
}

/* Additional styles for desktop spacing */
@media (min-width: 960px) {
  .login-card {
    padding: 40px;
  }
}

</style>