<template>
  <v-container fluid>
    <!-- Loading overlay -->
    <div v-if="isRedirecting" class="loading-overlay">
      <v-progress-circular
        indeterminate
        color="primary"
        size="64"
      ></v-progress-circular>
      <p class="mt-3">Loading your study session...</p>
    </div>
    
    <v-row>
      <!-- Sidebar Navigation -->
      <!--      <v-col cols="12" md="2" class="sidebar">-->
      <!--        <h3 class="text-h5 font-weight-medium">Jan'25</h3>-->
      <!--        <h4 class="text-h6 font-weight-bold">Software Engg.</h4>-->

      <!--        <v-btn block color="grey-lighten-3" class="sidebar-btn">Homepage</v-btn>-->
      <!--        <v-btn block color="grey-lighten-3" class="sidebar-btn">Study with GenAI</v-btn>-->
      <!--        <v-btn block color="grey-lighten-3" class="sidebar-btn">Code with GenAI</v-btn>-->
      <!--        <v-btn block color="grey-lighten-3" class="sidebar-btn">Bookmarks</v-btn>-->

      <!--        <v-btn block color="grey-darken-1" class="sidebar-btn mt-4" dark>To Course Page</v-btn>-->
      <!--      </v-col>-->

      <!-- Main Dashboard Content -->
      <v-col cols="12" md="7">
        <h2 class="text-h5 font-weight-medium">Hello, {{ user.name }}!</h2>

        <!-- Study Progress Section -->
        <v-card class="progress-card mt-4" outlined>
          <v-card-title>Pick up where you left off…</v-card-title>
          <v-card-text>
            <v-text-field v-model="studyPrompt" readonly outlined dense class="study-prompt"></v-text-field>
            <div class="d-flex align-center">
              <v-btn color="primary" class="mr-2" @click="goToStudy">Study with GenAI!</v-btn>

              <!-- Mini Gemini Chat -->
              <v-btn
                  icon
                  color="primary"
                  class="ml-auto"
                  @click="toggleGeminiChat"
              >
                <v-icon>{{ showGeminiChat ? mdiClose() : mdiMessageProcessing() }}</v-icon>
              </v-btn>
            </div>

            <!-- Gemini Chat Interface -->
            <v-expand-transition>
              <div v-if="showGeminiChat" class="gemini-chat-container mt-3">
                <div class="gemini-chat-messages" ref="geminiChatContainer">
                  <div
                      v-for="(msg, index) in geminiMessages"
                      :key="index"
                      :class="['gemini-message', msg.isUser ? 'gemini-user-message' : 'gemini-ai-message']"
                  >
                    <div class="gemini-message-content">
                      <p>{{ msg.text }}</p>
                      <span v-if="msg.isFallback" class="gemini-fallback-indicator">
                        <v-icon x-small color="amber darken-2" class="mr-1">{{ mdiInformation() }}</v-icon>
                        Quick answer mode
                      </span>
                    </div>
                  </div>

                  <!-- Loading indicator -->
                  <div v-if="isGeminiLoading" class="gemini-message gemini-ai-message">
                    <div class="gemini-message-content">
                      <div class="gemini-typing-indicator">
                        <span></span>
                        <span></span>
                        <span></span>
                      </div>
                    </div>
                  </div>
                </div>

                <div class="gemini-input-area">
                  <v-text-field
                      v-model="geminiInput"
                      placeholder="Ask Gemini a quick question..."
                      dense
                      outlined
                      hide-details
                      @keyup.enter="sendGeminiMessage"
                      :disabled="isGeminiLoading"
                  ></v-text-field>
                  <v-btn
                      icon
                      color="primary"
                      class="ml-2"
                      @click="sendGeminiMessage"
                      :disabled="isGeminiLoading"
                  >
                    <v-icon>{{mdiSend()}}</v-icon>
                  </v-btn>
                </div>
              </div>
            </v-expand-transition>
          </v-card-text>
        </v-card>

        <!-- Study Plan - Horizontal Timeline -->
        <v-card class="study-plan mt-4" outlined>
          <v-card-title class="d-flex justify-space-between align-center py-2">
            Your Study Plan
            <v-select
                v-model="selectedQuiz"
                :items="quizzes"
                item-title="name"
                item-value="id"
                return-object
                label="Select Quiz"
                dense
                outlined
                hide-details
                style="max-width: 180px;"
            ></v-select>
          </v-card-title>
          <v-card-text class="pb-0">
            <!-- Main progress bar showing weeks leading to quiz -->
            <div class="progress-container mb-2">
              <v-progress-linear
                  height="8"
                  rounded
                  background-color="grey lighten-3"
                  color="primary"
                  :value="calculateProgressPercentage()"
              ></v-progress-linear>

              <div class="progress-markers">
                <div
                    v-for="(item, index) in timeline"
                    :key="index"
                    class="marker-container"
                    :class="{'quiz-marker': item.type === 'quiz'}"
                    :style="{left: `${calculateMarkerPosition(index)}%`}"
                >
                  <v-tooltip bottom>
                    <template v-slot:activator="{ on, attrs }">
                      <div
                          class="marker"
                          :class="{
                          'quiz-marker': item.type === 'quiz',
                          'completed-marker': item.type === 'week' && item.completed
                        }"
                          v-bind="attrs"
                          v-on="on"
                          @click="item.type === 'week' ? toggleLecturesForWeek(item.id.toString()) : null"
                      >
                        <v-icon x-small v-if="item.type === 'quiz'">{{ mdiFlagCheckered() }}</v-icon>
                        <span v-else>{{ index + 1 }}</span>
                      </div>
                    </template>
                    <span>
                      <strong>{{ item.title }}</strong><br>
                      <span v-if="item.type === 'week' && item.lectures">{{ item.lectures.length }} lectures</span>
                      <span v-if="item.type === 'quiz'">Final assessment</span>
                    </span>
                  </v-tooltip>
                </div>
              </div>
            </div>

            <!-- Week labels below progress bar -->
            <div class="week-labels d-flex justify-space-between mb-3">
              <div
                  v-for="(item, index) in timeline"
                  :key="`label-${index}`"
                  class="week-label text-caption"
                  :class="{'quiz-label': item.type === 'quiz'}"
                  @click="item.type === 'week' ? toggleLecturesForWeek(item.id.toString()) : null"
                  style="cursor: pointer;"
              >
                {{ item.title }}
              </div>
            </div>

            <!-- Current expanded week section -->
            <div v-if="expandedWeeks.length > 0" class="expanded-week mt-3 mb-2">
              <div v-for="weekId in expandedWeeks" :key="`expanded-${weekId}`">
                <div class="week-header d-flex justify-space-between align-center mb-3">
                  <div class="d-flex align-center">
                    <v-avatar size="28" color="primary" class="mr-2">
                      <span class="white--text text-caption">{{ weekId }}</span>
                    </v-avatar>
                    <div class="week-title text-h6">
                      {{ getWeekTitle(weekId) }} <span class="text-subtitle-2 font-weight-regular">Learning Materials</span>
                    </div>
                  </div>
                  <v-chip small color="blue-grey lighten-5" @click="toggleLecturesForWeek(weekId)" class="close-btn">
                    <v-icon x-small left>{{ mdiClose() }}</v-icon>
                    Hide
                  </v-chip>
                </div>

                <div class="week-description mb-4 text-caption text-medium-emphasis">
                  <v-icon x-small class="mr-1">mdi-information-outline</v-icon>
                  Click on any lecture to study it with GenAI assistance. All materials are prepared to help you master the concepts efficiently.
                </div>

                <div class="lectures-grid">
                  <v-row dense>
                    <v-col
                        v-for="(lecture, lectureIndex) in getWeekLectures(weekId)"
                        :key="lectureIndex"
                        cols="12"
                        sm="6"
                        md="4"
                    >
                      <v-card 
                          elevation="0" 
                          outlined 
                          hover 
                          class="lecture-card" 
                          @click="goToStudyWithLecture(lecture)"
                      >
                        <v-list-item three-line dense>
                          <v-list-item-content>
                            <div class="lecture-header d-flex align-center mb-1">
                              <v-icon 
                                size="18" 
                                :color="lecture.type === 'Video' ? 'blue' : 'green'"
                                class="mr-2"
                              >
                                {{ lecture.type === 'Video' ? mdiPlayCircle() : mdiFileDocument() }}
                              </v-icon>
                              <v-list-item-title class="text-subtitle-2 font-weight-medium">
                                {{ lecture.name }}
                              </v-list-item-title>
                            </div>
                            <v-list-item-subtitle class="text-caption text-truncate">
                              <v-chip
                                  x-small
                                  :color="lecture.type === 'Video' ? 'blue' : 'green'"
                                  text-color="white"
                                  class="mt-1"
                              >
                                {{ lecture.type }}
                              </v-chip>
                              <span v-if="lecture.duration" class="lecture-duration ml-2">
                                {{ lecture.duration }}
                              </span>
                            </v-list-item-subtitle>
                          </v-list-item-content>
                          <v-list-item-action>
                            <v-btn 
                                icon 
                                x-small 
                                :color="lecture.type === 'Video' ? 'blue' : 'green'"
                                class="lecture-action-btn"
                            >
                              <v-icon size="16">{{ mdiFile() }}</v-icon>
                            </v-btn>
                          </v-list-item-action>
                        </v-list-item>
                        <v-divider class="mx-3"></v-divider>
                        <v-card-actions class="pa-2">
                          <v-btn x-small text color="primary" class="px-1">
                            <v-icon x-small left>mdi-book-open-variant</v-icon>
                            Study Now
                          </v-btn>
                          <v-spacer></v-spacer>
                          <v-tooltip bottom>
                            <template v-slot:activator="{ on, attrs }">
                              <v-icon 
                                  x-small 
                                  color="grey"
                                  v-bind="attrs"
                                  v-on="on"
                              >
                                mdi-information-outline
                              </v-icon>
                            </template>
                            <span>Click to study with GenAI</span>
                          </v-tooltip>
                        </v-card-actions>
                      </v-card>
                    </v-col>
                  </v-row>
                </div>
              </div>
            </div>

            <v-card-actions class="mt-4 pt-2 d-flex justify-center">
              <v-btn 
                  color="primary" 
                  outlined 
                  class="px-4 py-2 reassess-btn" 
                  @click="$emit('reassess')"
              >
                <v-icon left size="18">mdi-refresh</v-icon>
                RE-ASSESS MY PLAN
              </v-btn>
            </v-card-actions>
          </v-card-text>
        </v-card>

        <!-- Quick Links -->
        <v-card class="quick-links mt-4" outlined>
          <v-card-title>Quick Links</v-card-title>
          <v-card-text class="d-flex flex-wrap">
            <v-btn block color="primary" class="quick-link-btn">Course Grading Document</v-btn>
            <v-btn block color="primary" class="quick-link-btn">Slides Used in Lectures</v-btn>
            <v-btn block color="primary" class="quick-link-btn">Previous Year Papers</v-btn>
            <v-btn block color="primary" class="quick-link-btn">Practice Assignment Solution</v-btn>
          </v-card-text>
        </v-card>
      </v-col>

      <!-- Right Sidebar: Deadlines & Past Results -->
      <v-col cols="12" md="3">
        <v-card class="deadlines-card" outlined>
          <v-card-title>Upcoming Deadlines</v-card-title>
          <v-card-text>
            <ul class="deadlines-list">
              <li v-for="(deadline, index) in upcomingDeadlines" :key="index">
                <span class="deadline-title">{{ deadline.title }}</span>
                <span class="deadline-date">{{ deadline.date }}</span>
                <v-chip
                    v-if="deadline.type === 'quiz'"
                    color="primary"
                    size="small"
                    class="ml-2"
                >
                  Quiz
                </v-chip>
              </li>
            </ul>
          </v-card-text>
        </v-card>

        <!-- Past Results Chart -->
        <v-card class="past-results mt-4" outlined>
          <v-card-title>Past Results</v-card-title>
          <v-card-text>
            <canvas ref="pastResultsChart"></canvas>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import Chart from 'chart.js/auto';
import {DashboardService} from '@services/dashboard.js';
import axios from '@services/http-common';
import {
  mdiClose, mdiFile, mdiFileDocument,
  mdiFlagCheckered,
  mdiInformation,
  mdiInformationOutline,
  mdiMessageProcessing, mdiPlayCircle,
  mdiSend
} from "@mdi/js";

export default {
  name: 'Dashboard2',
  data() {
    return {
      studyPrompt: "Explain me how to create effective wireframes",
      selectedQuiz: null,
      quizzes: [],
      timeline: [],
      weeksData: {},
      expandedWeeks: [], // Track which weeks are expanded
      showGeminiChat: false,
      geminiInput: "",
      geminiMessages: [],
      isGeminiLoading: false,
      isRedirecting: false,
      user: {
        id: null,
        name: '',
        student_id: ''
      },
      upcomingDeadlines: [],
      studyPlan: [
        {title: "Step 1", date: "Feb 10", completed: true},
        {title: "Step 2", date: "Feb 12", completed: true},
        {title: "Step 3", date: "Feb 15", completed: false},
        {title: "Step 4", date: "Feb 18", completed: false},
      ],
      pastResultsChart: null,
      currentUser: null
    };
  },
  watch: {
    selectedQuiz(newQuiz, oldQuiz) {
      console.log('Quiz selection changed:', newQuiz);
      if (newQuiz && (!oldQuiz || newQuiz.id !== oldQuiz.id)) {
        // Reset expanded weeks and rebuild timeline
        this.expandedWeeks = [];
        this.buildTimeline();
      }
    }
  },
  methods: {
    mdiFileDocument() {
      return mdiFileDocument
    },
    mdiFile() {
      return mdiFile
    },
    mdiPlayCircle() {
      return mdiPlayCircle
    },
    mdiFlagCheckered() {
      return mdiFlagCheckered
    },
    mdiSend() {
      return mdiSend;
    },
    mdiInformation() {
      return mdiInformation
    },
    mdiClose() {
      return mdiClose;
    },
    mdiMessageProcessing() {
      return mdiMessageProcessing;
    },
    async fetchDashboardData() {
      try {
        const response = await DashboardService.getStudentDashboard();

        this.user = response.user;
        this.upcomingDeadlines = response.upcoming_deadlines;
        this.studyPlan = response.study_plan.steps;

        // Clear existing data first
        this.quizzes = [];
        this.weeksData = {};
        this.timeline = [];
        this.selectedQuiz = null;

        // Process quiz data - make a copy to avoid reference issues
        if (response.study_plan.quizzes && response.study_plan.quizzes.length > 0) {
          this.quizzes = response.study_plan.quizzes.map(quiz => ({...quiz}));
          console.log("Quizzes loaded:", JSON.stringify(this.quizzes));
        }

        // Process weeks data - make a copy to avoid reference issues
        if (response.study_plan.weeks_data) {
          this.weeksData = JSON.parse(JSON.stringify(response.study_plan.weeks_data));
          console.log("Weeks data loaded:", Object.keys(this.weeksData));
        }

        this.pastResults = response.past_results;
        this.quickLinks = response.quick_links;
        this.pickUpWhereLeftOff = response.pick_up_where_left_off;

        // Set default selected quiz if not already set and rebuild timeline
        if (this.quizzes.length > 0) {
          // First clear any previous selection
          this.selectedQuiz = null;
          // Then set the new selection and rebuild
          this.$nextTick(() => {
            this.selectedQuiz = this.quizzes[0];
            console.log("Selected default quiz:", this.selectedQuiz);
            this.buildTimeline();
          });
        }
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
      }
    },
    getUser() {
      const user = localStorage.getItem("user");
      this.currentUser = user ? JSON.parse(user) : null;
      if (this.currentUser) {
        this.currentRole = this.currentUser['role'] ?? 'student';
      }
    },
    goToStudy() {
      this.$router.push('/study');
    },
    goToStudyWithLecture(lecture) {
      // Show loading overlay
      this.isRedirecting = true;
      
      // Navigate to study page with lecture information
      this.$router.push({
        path: '/study',
        query: {
          lecture_id: lecture.id,
          lecture_name: lecture.name,
          prompt: `Help me understand ${lecture.name}`
        }
      }).catch(err => {
        console.error('Navigation failed:', err);
        this.isRedirecting = false; // Hide overlay if navigation fails
      });
    },
    initCharts() {
      if (this.$refs.pastResultsChart) {
        new Chart(this.$refs.pastResultsChart.getContext('2d'), {
          type: 'bar',
          data: {
            labels: ["Week 1", "Week 2", "Week 3"],
            datasets: [
              {
                label: "Total Grade Contribution",
                data: [3, 3, 3],
                backgroundColor: "#66BB6A",
              },
            ],
          },
        });
      }
    },
    getTimelineItemColor(item) {
      if (item.type === 'quiz') {
        return 'red';
      } else if (item.completed) {
        return 'green';
      } else {
        return 'blue';
      }
    },
    getTimelineItemIcon(item) {
      if (item.type === 'quiz') {
        return 'mdi-clipboard-text';
      } else {
        return 'mdi-book-open-variant';
      }
    },
    buildTimeline() {
      this.timeline = [];

      if (!this.selectedQuiz || !this.weeksData) {
        console.log("Missing quiz or weeks data");
        return;
      }

      // Get the target week ID from the quiz
      const targetWeekId = parseInt(this.selectedQuiz.after);
      console.log("Selected quiz:", this.selectedQuiz);
      console.log("Target week ID:", targetWeekId);
      console.log("All available weeks:", Object.keys(this.weeksData));

      if (isNaN(targetWeekId)) {
        console.error("Invalid target week ID:", this.selectedQuiz.after);
        return;
      }

      // Get all week IDs as integers, sorted
      const allWeekIds = Object.keys(this.weeksData)
          .map(id => parseInt(id))
          .sort((a, b) => a - b);
      console.log("All week IDs (sorted):", allWeekIds);

      // Filter weeks to only include those up to target week
      const weeksToInclude = allWeekIds.filter(id => id <= targetWeekId);
      console.log("Weeks to include:", weeksToInclude);

      // Build the new timeline
      for (const weekId of weeksToInclude) {
        // Get the week data from weeksData using string key
        const week = this.weeksData[weekId.toString()];
        if (week) {
          this.timeline.push({...week});
          console.log(`Added week ${weekId} to timeline`);
        } else {
          console.warn(`Week ${weekId} not found in weeksData`);
        }
      }

      // Add the quiz as the final item
      this.timeline.push({
        id: this.selectedQuiz.id,
        title: this.selectedQuiz.name,
        type: 'quiz',
        date: this.selectedQuiz.date,
        completed: false
      });
      console.log("Added quiz to timeline");

      console.log("Final timeline:", this.timeline);
    },
    toggleLecturesForWeek(weekId) {
      // Convert to string for consistency
      const id = weekId.toString();
      const index = this.expandedWeeks.indexOf(id);

      if (index === -1) {
        // Clear any previously expanded weeks first
        this.expandedWeeks = [];
        // Add only the newly selected week
        this.expandedWeeks.push(id);
        console.log(`Expanded week ${id}`);
      } else {
        // Remove from expanded weeks
        this.expandedWeeks.splice(index, 1);
        console.log(`Collapsed week ${id}`);
      }
    },
    calculateProgressPercentage() {
      if (!this.timeline.length) return 0;

      // Count how many weeks are completed
      const weekItems = this.timeline.filter(item => item.type === 'week');
      const completedWeeks = weekItems.filter(item => item.completed).length;

      return (completedWeeks / weekItems.length) * 100;
    },

    calculateMarkerPosition(index) {
      if (!this.timeline.length) return 0;

      const totalItems = this.timeline.length;
      // Ensure first and last markers aren't right at the edges
      const padding = 2;
      const usableSpace = 100 - (padding * 2);

      return padding + (index / (totalItems - 1)) * usableSpace;
    },

    getWeekTitle(weekId) {
      const id = weekId.toString();
      if (!this.weeksData || !this.weeksData[id]) {
        console.warn(`Week ${weekId} not found in weeksData`);
        return '';
      }
      return this.weeksData[id].title;
    },

    getWeekLectures(weekId) {
      const id = weekId.toString();
      if (!this.weeksData || !this.weeksData[id] || !this.weeksData[id].lectures) {
        console.warn(`Lectures for week ${weekId} not found`);
        return [];
      }
      return this.weeksData[id].lectures;
    },
    toggleGeminiChat() {
      this.showGeminiChat = !this.showGeminiChat;
      if (this.showGeminiChat && this.geminiMessages.length === 0) {
        // Add initial welcome message from Gemini
        this.geminiMessages.push({
          isUser: false,
          text: "Hi there! I'm Gemini. How can I help you today?"
        });
      }
      this.$nextTick(() => {
        this.scrollGeminiToBottom();
      });
    },

    async sendGeminiMessage() {
      if (!this.geminiInput.trim() || this.isGeminiLoading) return;

      const userMessage = this.geminiInput.trim();
      this.geminiInput = "";

      // Add user message
      this.geminiMessages.push({
        isUser: true,
        text: userMessage
      });

      // Set loading state
      this.isGeminiLoading = true;

      // Scroll to bottom to show new message
      this.scrollGeminiToBottom();

      try {
        // Call the actual API
        await this.callGeminiAPI(userMessage);
      } catch (error) {
        console.error('Error calling Gemini API:', error);

        // Add error message
        this.geminiMessages.push({
          isUser: false,
          text: "Sorry, I encountered an error. Please try again later."
        });

        // End loading state
        this.isGeminiLoading = false;

        // Scroll to bottom to show error message
        this.scrollGeminiToBottom();
      }
    },

    async callGeminiAPI(userMessage) {
      try {
        // Make API call to our backend endpoint for Gemini API
        const response = await axios.post('/chat/gemini', {
          message: userMessage,
          context: 'dashboard_quick_chat'
        });

        // Add AI response from Gemini
        this.geminiMessages.push({
          isUser: false,
          text: response.data.response || "I'm not sure how to respond to that.",
          isFallback: response.data.is_fallback || false
        });

        // If this was a fallback response, we could potentially add UI to indicate that
        if (response.data.is_fallback) {
          console.log('Using fallback response mechanism');
        }
      } catch (error) {
        console.error('API call failed:', error);
        throw error;
      } finally {
        // End loading state
        this.isGeminiLoading = false;

        // Scroll to bottom to show new message
        this.scrollGeminiToBottom();
      }
    },

    scrollGeminiToBottom() {
      this.$nextTick(() => {
        const container = this.$refs.geminiChatContainer;
        if (container) {
          container.scrollTop = container.scrollHeight;
        }
      });
    }
  },
  mounted() {
    this.getUser();
    this.fetchDashboardData();
    this.initCharts();
  }
};
</script>

<style scoped>
/* Loading overlay */
.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(255, 255, 255, 0.9);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  z-index: 9999;
}

/* Sidebar */
.sidebar {
  padding: 20px;
  background: #F5F5F5;
  border-right: 2px solid #E0E0E0;
}

.sidebar-btn {
  margin-bottom: 8px;
}

/* Study Progress */
.progress-card {
  padding: 15px;
  border-radius: 10px;
}

.study-prompt {
  background: #f8f9fa;
}

/* Study Plan */
.study-plan {
  padding: 12px;
  border-radius: 10px;
}

/* Updated lecture card styling */
.expanded-week {
  background-color: #f8fbff;
  border-radius: 12px;
  padding: 16px;
  box-shadow: inset 0 0 8px rgba(0, 0, 0, 0.05);
  border: 1px solid #e3f2fd;
}

.week-header {
  padding-bottom: 8px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
}

.week-title {
  color: #1976D2;
  font-weight: 500;
  display: flex;
  align-items: baseline;
  gap: 8px;
}

.week-description {
  background-color: rgba(25, 118, 210, 0.06);
  padding: 8px 12px;
  border-radius: 6px;
  color: #37474F;
}

.close-btn {
  transition: all 0.2s ease;
}

.close-btn:hover {
  background-color: #E3F2FD;
}

.lectures-grid {
  margin-top: 12px;
}

.lecture-card {
  transition: all 0.25s ease;
  border-radius: 8px;
  border: 1px solid #e0e0e0;
  overflow: hidden;
}

.lecture-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);
  border-color: #bbdefb;
}

.lecture-header {
  overflow: hidden;
}

.lecture-action-btn {
  opacity: 0.7;
  transition: all 0.2s ease;
}

.lecture-card:hover .lecture-action-btn {
  opacity: 1;
  transform: scale(1.1);
}

.lecture-duration {
  color: #757575;
  font-size: 0.75rem;
}

/* Progress bar and markers */
.progress-container {
  position: relative;
  padding-top: 20px;
  padding-bottom: 10px;
  margin: 0 10px;
}

.progress-markers {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}

.marker-container {
  position: absolute;
  transform: translateX(-50%);
}

.marker {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background-color: #1976D2;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  cursor: pointer;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
  z-index: 2;
  transition: all 0.2s ease;
}

.marker:hover {
  transform: scale(1.15);
  box-shadow: 0 3px 8px rgba(0, 0, 0, 0.3);
}

.quiz-marker {
  background-color: #F44336;
  width: 26px;
  height: 26px;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% {
    box-shadow: 0 0 0 0 rgba(244, 67, 54, 0.4);
  }
  70% {
    box-shadow: 0 0 0 7px rgba(244, 67, 54, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(244, 67, 54, 0);
  }
}

.completed-marker {
  background-color: #4CAF50;
}

.week-labels {
  margin: 0 5px;
  padding-top: 8px;
  display: flex;
  justify-content: space-between;
}

.week-label {
  max-width: 70px;
  text-align: center;
  font-size: 10px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  color: #555;
  padding: 4px 6px;
  border-radius: 12px;
  transition: all 0.2s ease;
  cursor: pointer;
}

.week-label:hover {
  background-color: #E3F2FD;
  color: #1976D2;
}

.quiz-label {
  color: #F44336;
  font-weight: bold;
}

.quiz-label:hover {
  background-color: #FFEBEE;
}

.reassess-btn {
  letter-spacing: 1.2px;
  font-weight: 500;
  text-transform: uppercase;
  border-radius: 20px;
  box-shadow: 0 2px 5px rgba(0,0,0,0.05);
  transition: all 0.2s ease;
}

.reassess-btn:hover {
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
  transform: translateY(-2px);
}

/* Quick Links */
.quick-links {
  padding: 15px;
  border-radius: 10px;
}

.quick-link-btn {
  margin-bottom: 10px;
}

/* Deadlines */
.deadlines-card {
  padding: 15px;
  border-radius: 10px;
}

.deadlines-list {
  list-style-type: none;
  padding: 0;
}

.deadlines-list li {
  display: flex;
  justify-content: space-between;
  padding: 5px 0;
  font-size: 16px;
}

.deadline-title {
  color: #e57373;
}

.deadline-date {
  font-weight: bold;
  color: #000;
}

/* Past Results */
.past-results {
  padding: 15px;
  border-radius: 10px;
}

.user-info {
  display: flex;
  align-items: center;
  padding: 20px;
  background: linear-gradient(135deg, #1a237e 0%, #0d47a1 100%);
  color: white;
  border-radius: 8px;
  margin-bottom: 20px;
}

.avatar {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 15px;
}

.user-details {
  flex: 1;
}

.greeting {
  font-size: 1.1em;
  font-weight: 500;
  margin-bottom: 4px;
}

.roll-number {
  font-size: 0.9em;
  opacity: 0.8;
}

/* Gemini Chat Styles */
.gemini-chat-container {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  overflow: hidden;
  background-color: #f8f9fa;
}

.gemini-chat-messages {
  height: 200px;
  overflow-y: auto;
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.gemini-message {
  max-width: 80%;
  padding: 8px 12px;
  border-radius: 12px;
  word-wrap: break-word;
}

.gemini-user-message {
  align-self: flex-end;
  background-color: #dcf8c6;
  color: #000;
  border-radius: 12px 12px 0 12px;
}

.gemini-ai-message {
  align-self: flex-start;
  background-color: white;
  color: #000;
  border-radius: 12px 12px 12px 0;
  border: 1px solid #e0e0e0;
}

.gemini-message-content p {
  margin: 0;
  font-size: 0.9rem;
}

.gemini-input-area {
  display: flex;
  align-items: center;
  padding: 8px 12px;
  background-color: white;
  border-top: 1px solid #e0e0e0;
}

.gemini-typing-indicator {
  display: flex;
  align-items: center;
  gap: 4px;
}

.gemini-typing-indicator span {
  display: inline-block;
  width: 8px;
  height: 8px;
  background-color: #1867c0;
  border-radius: 50%;
  animation: gemini-bounce 1.3s ease infinite;
  opacity: 0.6;
}

.gemini-typing-indicator span:nth-child(2) {
  animation-delay: 0.15s;
}

.gemini-typing-indicator span:nth-child(3) {
  animation-delay: 0.3s;
}

@keyframes gemini-bounce {
  0%, 60%, 100% {
    transform: translateY(0);
  }
  30% {
    transform: translateY(-4px);
  }
}

.gemini-fallback-indicator {
  display: block;
  font-size: 10px;
  color: #FF8F00;
  margin-top: 4px;
  font-style: italic;
}
</style>