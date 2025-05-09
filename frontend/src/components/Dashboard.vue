<template>
  <div class="dashboard container-fluid">
    <header class="row py-3 bg-light">
      <div class="col">
        <h1 class="h3">Student Dashboard: Home View</h1>
        <div class="user-info small text-muted">
          <p class="mb-0">Jan 25</p>
          <p class="mb-0">Software Engg.</p>
          <p class="mb-0">Hello, 21f1001247!</p>
        </div>
      </div>
    </header>

    <div class="row mt-4">
      <!-- Left Sidebar -->
<!--      <nav class="col-12 col-md-3 col-lg-2 mb-4">-->
<!--        <div class="d-flex flex-column">-->
<!--          <router-link to="/" class="btn btn-light mb-2 text-start">Homepage</router-link>-->
<!--          <router-link to="/study" class="btn btn-light mb-2 text-start">Study with GenAI</router-link>-->
<!--          <router-link to="/code" class="btn btn-light mb-2 text-start">Code with GenAI</router-link>-->
<!--          <router-link to="/bookmarks" class="btn btn-light mb-2 text-start">Bookmarks</router-link>-->
<!--        </div>-->
<!--      </nav>-->

      <!-- Main Content -->
      <main class="col-12 col-md-6 col-lg-7 mb-4">
        <div class="card mb-4">
          <div class="card-body">
            <h2 class="h5">Pick up where you left off...</h2>
            <div class="bg-light p-3 rounded">
              <p>Explain me how to create effective wireframes</p>
              <button class="btn btn-primary">Study with GenAI!</button>
            </div>
          </div>
        </div>

        <div class="card mb-4">
          <div class="card-body">
            <div class="d-flex justify-content-between align-items-center mb-3">
              <h2 class="h5 mb-0">Your Study Plan</h2>
              <select class="form-select w-auto">
                <option>Goal: Quiz ▼</option>
              </select>
            </div>
            <div class="timeline mb-3">
              <!-- Timeline visualization here -->
            </div>
            <button class="btn btn-secondary">Re-assess my Plan</button>
          </div>
        </div>

        <div class="card">
          <div class="card-body">
            <h2 class="h5 mb-3">Quick Links</h2>
            <div class="row g-2">
              <div class="col-6">
                <button class="btn btn-light w-100">Course Grading Document</button>
              </div>
              <div class="col-6">
                <button class="btn btn-light w-100">Slides Used in Lectures</button>
              </div>
            </div>
          </div>
        </div>
      </main>

      <!-- Right Sidebar -->
      <aside class="col-12 col-md-3 col-lg-3">
        <div class="card mb-4">
          <div class="card-body">
            <h2 class="h5 mb-3">Upcoming Deadlines</h2>
            <ul class="list-unstyled">
              <li class="d-flex justify-content-between py-2 border-bottom">
                <span class="text-danger">Lx 1.1</span>
                <span class="text-danger">02/02</span>
              </li>
              <li class="d-flex justify-content-between py-2 border-bottom">
                <span class="text-danger">Graded Assignment</span>
                <span class="text-danger">02/02</span>
              </li>
              <li class="d-flex justify-content-between py-2 border-bottom">
                <span>Lx 2.1</span>
                <span>09/02</span>
              </li>
              <li class="d-flex justify-content-between py-2 border-bottom">
                <span>Graded Assignment</span>
                <span>09/02</span>
              </li>
            </ul>
          </div>
        </div>

        <div class="card">
          <div class="card-body">
            <h2 class="h5 mb-3">Past Results</h2>
            <div class="bg-light p-3 rounded">
              <!-- Chart here -->
            </div>
          </div>
        </div>
      </aside>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
const router = useRouter()
</script>

<style scoped>
.dashboard {
  min-height: 100vh;
  width: 100%;
  margin: 0;
  padding: 20px;
  background-color: #f5f5f5;
}

/* Header Styles */
header {
  background: #fff;
  padding: 15px 20px;
  margin-bottom: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

/* Layout Grid */
.dashboard-layout {
  display: grid;
  grid-template-columns: 200px 1fr 300px;
  gap: 20px;
  height: calc(100vh - 120px); /* Subtract header height + padding */
}

/* Sidebar */
.sidebar {
  background: #fff;
  padding: 15px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
  height: 100%;
}

/* Main Content */
.main-content {
  background: #fff;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
  height: 100%;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* Right Sidebar */
.right-sidebar {
  background: #fff;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
  height: 100%;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* Task Card */
.task-card {
  background: #f8f9fa;
  padding: 15px;
  border-radius: 6px;
  margin-bottom: 20px;
}

/* Study Plan */
.study-plan {
  flex-grow: 1;
  display: flex;
  flex-direction: column;
}

.timeline {
  flex-grow: 1;
  display: flex;
  align-items: center;
  justify-content: space-around;
  padding: 20px 0;
}

/* Quick Links */
.links-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

/* Responsive Design */
@media (max-width: 1200px) {
  .dashboard-layout {
    grid-template-columns: 180px 1fr 250px;
  }
}

@media (max-width: 992px) {
  .dashboard-layout {
    grid-template-columns: 160px 1fr;
    height: auto;
  }
  .right-sidebar {
    grid-column: 1 / -1;
  }
}

@media (max-width: 768px) {
  .dashboard-layout {
    grid-template-columns: 1fr;
  }
  .sidebar, .main-content, .right-sidebar {
    grid-column: 1 / -1;
  }
}

/* Add these to your existing styles */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  margin: 0;
  padding: 0;
  min-height: 100vh;
}

#app {
  min-height: 100vh;
}
</style>