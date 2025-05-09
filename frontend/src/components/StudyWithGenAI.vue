<template>
  <div class="dashboard container-fluid" :class="{ 'initializing': isInitializing }">
    <header class="row py-3 bg-light">
      <div class="col">
        <h1 class="h3">Study With GenAI</h1>
        <!--        <div class="user-info small text-muted">-->
        <!--&lt;!&ndash;          <p class="mb-0">Jan 25</p>&ndash;&gt;-->
        <!--&lt;!&ndash;          <p class="mb-0">Software Engg.</p>&ndash;&gt;-->
        <!--          &lt;!&ndash;          <p class="mb-0">Hello, 21f1001247!</p>&ndash;&gt;-->
        <!--        </div>-->
      </div>
    </header>

    <div class="row main-container">
      <!-- Main Content Area -->
      <main class="col-12 col-md-6 col-lg-8 main-content">
        <div class="content-wrapper" :class="{ 'chat-maximized': isChatMaximized }">
          <div class="topic-header">
            <div class="subject-tag">Software Engineering</div>
          </div>

          <div class="study-controls">
            <v-select
                v-model="selectedWeek"
                :items="weeks"
                item-title="name"
                item-value="id"
                label="Week"
                required
                outlined
                class="mb-4"
                style="border-radius: 8px;"
            ></v-select>

            <v-select
                v-model="selectedLecture"
                :items="lectures"
                item-title="name"
                item-value="id"
                label="Lecture"
                required
                outlined
                class="mb-4"
                style="border-radius: 8px;"
            ></v-select>
          </div>

          <div class="week-title">
            <h2>{{ selectedLectureData?.name }}</h2>
            <div class="instructors">
              <p>Dr. Sridhar Iyer, IIT Bombay</p>
              <p>Dr. Prajish Prasad, FLAME University</p>
            </div>
            <div v-if="selectedContent === 'Video'" class="video-container">
              <iframe
                  width="100%"
                  height="315"
                  :src="`https://www.youtube.com/embed/${selectedLectureData?.video_id}`"
                  title="YouTube video player"
                  frameborder="0"
                  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                  allowfullscreen>
              </iframe>
            </div>
            <div v-else-if="selectedContent === 'Assignment'">
              <embed src="/Assignment 1.pdf" type="application/pdf" width="100%" height="600px"/>
            </div>
          </div>
        </div>

        <!-- Chat Interface -->
        <div class="chat-interface" :class="{ 'maximized': isChatMaximized }">
          <div class="chat-header">
            <div class="search-scope">
              <label class="switch">
                <input
                    type="checkbox"
                    v-model="searchAllLectures"
                >
                <span class="slider round"></span>
                <span class="switch-label">{{
                    searchAllLectures ? 'Searching all lectures' : 'Searching current lecture'
                  }}</span>
              </label>
            </div>
          </div>

          <div class="chat-messages" ref="chatContainer">
            <div
                v-for="msg in chatMessages"
                :key="msg.id"
                :class="['message', msg.sender === 'user' ? 'user-message' : 'ai-message']"
            >
              <div class="message-content">
                <p>{{ msg.message }}</p>
                <span class="message-time">{{ formatTimestamp(msg.created_at) }}</span>

                <!-- Update to use relevant_content instead of relevant_videos -->
                <div v-if="msg.sender === 'ai' && msg.relevant_content?.length" class="relevant-segments">
                  <div class="relevant-title">Relevant Video Segments:</div>
                  <div v-for="content in msg.relevant_content"
                       :key="content.id"
                       class="relevant-segment">
                    <div class="segment-info">
                      <span>{{ content.title }}</span>
                      <p class="segment-description">{{ content.description }}</p>
                    </div>
                    <button
                        @click="handleVideoNavigation(content)"
                        class="segment-button"
                    >
                      Watch Segment
                    </button>
                  </div>
                </div>
              </div>
            </div>

            <!-- Loading indicator - Make sure this is visible -->
            <div v-if="isLoading" class="message ai-message">
              <div class="message-content">
                <div class="typing-indicator">
                  <div class="dots">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="input-area">
            <input
                v-model="newMessage"
                type="text"
                placeholder="Type a message..."
                class="chat-input"
                @keyup.enter="sendMessage"
                :disabled="isLoading"
            />
            <button
                @click="sendMessage"
                class="send-button"
                :disabled="isLoading"
            >
              {{ isLoading ? '...' : '↑' }}
            </button>
            <button
                class="maximize-button"
                @click="toggleChatSize"
            >
              {{ isChatMaximized ? '⊟' : '⊞' }}
            </button>
          </div>
        </div>
      </main>

      <!-- Right Sidebar -->
      <aside class="col-12 col-md-6 col-lg-4 resources">
        <section class="resource-section">
          <h3>Relevant Course Videos</h3>
          <div v-if="!latestRelevantContent.length" class="no-content">
            No relevant videos found yet. Try asking a question!
          </div>
          <div v-for="content in latestRelevantContent"
               :key="content.id"
               class="resource-item">
            <div>
              <p>{{ content.title }}</p>
              <p class="timestamp">{{ content.description }}</p>
            </div>
            <button
                @click="handleVideoNavigation(content)"
                class="go-button"
            >
              Go To Video
            </button>
          </div>
        </section>

        <section class="resource-section">
          <h3>Relevant Supplementary Content</h3>
          <div v-if="!supplementaryContent.length" class="no-content">
            No supplementary content found yet. Try asking a question!
          </div>
          <div v-for="content in supplementaryContent"
               :key="content.title"
               class="resource-item">
            <div>
              <p>{{ content.title }}</p>
              <p class="timestamp">{{ content.snippet }}</p>
            </div>
            <a
                :href="content.link"
                target="_blank"
                class="go-button"
            >
              View Content
            </a>
          </div>
        </section>
      </aside>
    </div>
  </div>
</template>

<script>
import axios from "@services/http-common"
import StudyService from "@services/study"

export default {
  name: 'StudyWithGenAI',
  data() {
    return {
      selectedContent: 'Video',
      selectedWeek: 1,
      weeks: [],
      selectedLecture: 1,
      selectedLectureData: null,
      lectures: [],
      selectedSubject: 1,
      chatMessages: [],
      newMessage: "",
      currentUser: null,
      isChatMaximized: false,
      searchAllLectures: false,
      isLoading: false,
      isInitializing: false,
      latestRelevantContent: [],
      alwaysOpenNewTab: false,
      supplementaryContent: [],
    }
  },
  methods: {
    async initFromRouteParams() {
      // Check if we have lecture parameters from the route query
      const { lecture_id, lecture_name, prompt } = this.$route.query;
      
      if (lecture_id) {
        console.log(`Initializing with lecture: ${lecture_name} (ID: ${lecture_id})`);
        this.isInitializing = true;
        
        try {
          // Set the lecture ID if provided
          this.selectedLecture = parseInt(lecture_id);
          
          // Find the week for this lecture and set it
          await this.findWeekForLecture(parseInt(lecture_id));
          
          // If a prompt was provided, set it as the new message and send it
          if (prompt) {
            this.$nextTick(() => {
              this.newMessage = prompt;
              // Send the message after we're sure everything is loaded
              setTimeout(() => {
                this.sendMessage();
              }, 500);
            });
          }
        } catch (error) {
          console.error("Error initializing from route params:", error);
        } finally {
          this.isInitializing = false;
        }
      }
    },
    
    async findWeekForLecture(lectureId) {
      try {
        // First get all weeks
        await this.fetchWeeks();
        
        // Then search for the lecture in each week
        for (const week of this.weeks) {
          const response = await axios.get(`weeks/${week.id}/lectures`);
          const lectures = response.data;
          
          // Check if the lecture exists in this week
          const foundLecture = lectures.find(l => l.id === lectureId);
          if (foundLecture) {
            // Set the week and update lecture data
            this.selectedWeek = week.id;
            this.lectures = lectures;
            this.selectedLectureData = foundLecture;
            console.log(`Found lecture in week ${week.id}`);
            break;
          }
        }
      } catch (error) {
        console.error("Error finding week for lecture:", error);
      }
    },
    async fetchLectures() {
      try {
        const response = await axios.get(`weeks/${this.selectedWeek}/lectures`);
        this.lectures = response.data;
        
        // If we have a selected lecture ID from the route, try to maintain it
        const routeLectureId = parseInt(this.$route.query.lecture_id);
        const lectureExists = routeLectureId && this.lectures.some(l => l.id === routeLectureId);
        
        if (lectureExists) {
          // Keep the lecture from the route if it exists in this week
          this.selectedLecture = routeLectureId;
          this.selectedLectureData = this.lectures.find(l => l.id === routeLectureId);
        } else if (this.lectures.length > 0) {
          // Otherwise default to the first lecture
          this.selectedLecture = this.lectures[0].id;
          this.selectedLectureData = this.lectures[0];
        }
      } catch (error) {
        console.error("Error fetching lectures:", error);
      }
    },
    async fetchWeeks() {
      try {
        const response = await axios.get(`subjects/${this.selectedSubject}/weeks`);
        this.weeks = response.data;
        if (this.weeks.length > 0) {
          this.selectedWeek = this.weeks[0].id;
          await this.fetchLectures();
        }
      } catch (error) {
        console.error("Error fetching weeks:", error);
      }
    },
    initializeUser() {
      const userStr = localStorage.getItem("user");
      this.currentUser = userStr ? JSON.parse(userStr) : null;
    },
    async fetchChat() {
      try {
        const response = await axios.get(`lectures/${this.selectedLecture}/chats`);

        // Make sure to include relevant_content in chat messages
        this.chatMessages = response.data.map(msg => ({
          ...msg,
          relevant_content: msg.relevant_content || []
        }));

        // Get the latest AI message with relevant content
        const latestAiMessage = [...this.chatMessages]
            .reverse()
            .find(msg => msg.sender === 'ai' && msg.relevant_content?.length);

        // Update sidebar with latest relevant content
        this.latestRelevantContent = latestAiMessage?.relevant_content || [];

        this.scrollToBottom();
      } catch (error) {
        console.error("Error fetching chat:", error);
      }
    },

    async sendMessage() {
      if (!this.newMessage.trim() || this.isLoading) return;

      const userMessage = this.newMessage;
      this.newMessage = '';
      this.isLoading = true;

      try {
        // Add user message immediately
        this.chatMessages.push({
          sender: "user",
          message: userMessage,
          created_at: new Date().toISOString()
        });

        const response = await axios.post('chats', {
          user_id: this.currentUser.id,
          lecture_id: this.selectedLecture,
          message: userMessage,
          one: !this.searchAllLectures
        });

        // Add AI response with relevant content
        const aiMessage = {
          id: response.data.id,
          sender: response.data.sender,
          message: response.data.message,
          created_at: response.data.created_at,
          relevant_content: response.data.relevant_content || []
        };

        this.chatMessages.push(aiMessage);

        // Update sidebar with only the latest relevant content
        this.latestRelevantContent = response.data.relevant_content || [];

        // Search for supplementary content
        await this.searchSupplementaryContent(userMessage);

      } catch (error) {
        console.error("Error sending message:", error);
        this.newMessage = userMessage;
        this.chatMessages = this.chatMessages.filter(msg => msg.message !== userMessage);
      } finally {
        this.isLoading = false;
        this.scrollToBottom();
      }
    },

    async searchSupplementaryContent(query = "") {
      try {
        const response = await StudyService.searchContent(this.selectedLecture, query);
        this.supplementaryContent = response.data.results || [];
      } catch (error) {
        console.error("Error searching for supplementary content:", error);
        this.supplementaryContent = [];
      }
    },

    formatTimestamp(timestamp) {
      if (!timestamp) return "";

      const date = new Date(timestamp);

      // Get time in 12-hour format with AM/PM
      const time = date.toLocaleTimeString('en-US', {
        hour: 'numeric',
        minute: '2-digit',
        hour12: true
      });

      // Get date in readable format
      const today = new Date();
      const yesterday = new Date(today);
      yesterday.setDate(yesterday.getDate() - 1);

      // Format date based on when the message was sent
      let dateStr;
      if (date.toDateString() === today.toDateString()) {
        dateStr = 'Today';
      } else if (date.toDateString() === yesterday.toDateString()) {
        dateStr = 'Yesterday';
      } else {
        dateStr = date.toLocaleDateString('en-US', {
          day: 'numeric',
          month: 'short',
          year: 'numeric'
        });
      }

      return `${dateStr}, ${time}`;
    },

    goToVideo(video) {
      // If it's the current lecture, just update the time
      if (video.lecture_id === this.selectedLecture) {
        const iframe = document.querySelector('.video-container iframe');
        if (iframe) {
          const currentSrc = iframe.src.split('?')[0];
          iframe.src = `${currentSrc}?start=${video.timestamp}`;
        }
      } else {
        // Otherwise, change lecture and set time
        this.selectedLecture = video.lecture_id;
        // The video will be updated via watcher, then we can update time
        this.$nextTick(() => {
          const iframe = document.querySelector('.video-container iframe');
          if (iframe) {
            const currentSrc = iframe.src.split('?')[0];
            iframe.src = `${currentSrc}?start=${video.timestamp}`;
          }
        });
      }
    },

    scrollToBottom() {
      this.$nextTick(() => {
        const container = this.$refs.chatContainer;
        if (container) {
          container.scrollTop = container.scrollHeight;
        }
      });
    },
    async updateSelectedLecture(newLectureId) {
      this.selectedLectureData = this.lectures.find(lec => lec.id === newLectureId);
      this.selectedContent = this.selectedLectureData.type || 'Video';
      await this.fetchChat();
      // Fetch supplementary content when lecture changes
      await this.searchSupplementaryContent();
    },
    toggleChatSize() {
      this.isChatMaximized = !this.isChatMaximized;
      this.$nextTick(() => {
        this.scrollToBottom();
      });
    },
    handleVideoNavigation(content) {
      // Extract video ID and timestamp
      const timestamp = this.getTimestampFromUrl(content.url);
      const videoId = this.selectedLectureData?.video_id;

      // If it's a different lecture or we have a full YouTube URL
      if (content.url.includes('youtube.com')) {
        window.open(content.url, '_blank');
        return;
      }

      // If we're in the same lecture, update the current video
      if (videoId) {
        const iframe = document.querySelector('.video-container iframe');
        if (iframe) {
          iframe.src = `https://www.youtube.com/embed/${videoId}?start=${timestamp}&autoplay=1`;

          // Scroll to video
          document.querySelector('.video-container')?.scrollIntoView({
            behavior: 'smooth',
            block: 'center'
          });
        }
      }
    },

    getTimestampFromUrl(url) {
      if (!url) return 0;
      const match = url.match(/[?&]t=(\d+)/);
      return match ? parseInt(match[1]) : 0;
    },
  },
  async mounted() {
    await this.initializeUser();
    
    // Set initializing flag early
    const { lecture_id } = this.$route.query;
    if (lecture_id) {
      this.isInitializing = true;
    }
    
    await this.fetchWeeks();
    await this.fetchChat();
    
    // Process route parameters if any
    await this.initFromRouteParams();
    
    // Fetch supplementary content on initial load
    if (this.selectedLecture) {
      await this.searchSupplementaryContent();
    }
    
    this.isInitializing = false;
  },
  watch: {
    selectedLecture: {
      async handler(newVal) {
        await this.updateSelectedLecture(newVal);
        // Reset relevant content when changing lectures
        this.latestRelevantContent = [];
      }
    },
    selectedWeek() {
      this.fetchLectures();
    },
    newMessage() {
      this.scrollToBottom();
    }
  }
}
</script>

<style scoped>
/* General Styles */
.dashboard {
  max-width: 1400px;
  margin: 0 auto;
  font-family: Arial, sans-serif;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  position: relative;
}

.main-container {
  flex: 1;
  min-height: 0; /* Important for nested flex containers */
}

.main-content {
  display: flex;
  flex-direction: column;
  position: relative;
  height: calc(100vh - 70px); /* Adjust based on your header height */
  overflow: hidden;
}

.content-wrapper {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  padding-bottom: 320px; /* Larger than chat interface height to ensure content isn't hidden */
  transition: padding-bottom 0.3s ease;
}

.content-wrapper.chat-maximized {
  padding-bottom: calc(100% - 90px);
}

.chat-interface {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: white;
  padding: 10px;
  border-top: 1px solid #ddd;
  height: 300px;
  display: flex;
  flex-direction: column;
  transition: height 0.3s ease; /* Add smooth transition */
}

/* Add these new styles */
.chat-interface.maximized {
  height: calc(100% - 20px); /* Full height minus a small gap */
}

.resources {
  height: calc(100vh - 70px); /* Match main-content height */
  overflow-y: auto;
  padding: 15px;
  border-left: 1px solid #ddd;
}

/* Subject & Week Title */
.subject-tag {
  background-color: #f0f0e0;
  padding: 10px;
  margin-bottom: 20px;
}

.week-title {
  margin-bottom: 20px;
}

.instructors {
  color: #666;
  font-size: 0.9em;
  margin: 10px 0;
}

/* Study Controls */
.study-controls {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.dropdown {
  padding: 5px;
  min-width: 80px;
}

/* Sidebar & Resources */
.resource-section {
  margin-bottom: 20px;
}

.resource-section h3 {
  margin-bottom: 15px;
}

.resource-item {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 10px;
  background: white;
  border: 1px solid #dee2e6;
  border-radius: 8px;
  padding: 12px;
  margin-bottom: 10px;
  transition: all 0.3s ease;
}

.resource-item:hover {
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}

.timestamp {
  color: #6c757d;
  font-size: 0.85em;
  margin: 5px 0;
}

.description {
  font-size: 0.9em;
  color: #495057;
  margin: 5px 0;
  line-height: 1.4;
}

.go-button {
  white-space: nowrap;
  padding: 6px 12px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.go-button:hover {
  background-color: #0056b3;
}

.profile-icon {
  border-radius: 50%;
  margin-top: 10px;
}

/* Chat Interface */
.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 10px;
  background: #f0f0f0;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

/* User messages (Right-aligned, WhatsApp style) */
.user-message {
  align-self: flex-end;
  background-color: #dcf8c6;
  color: black;
  border-radius: 12px 12px 0 12px;
  padding: 10px;
  max-width: 60%;
  word-wrap: break-word;
}

/* AI messages (Left-aligned) */
.ai-message {
  align-self: flex-start;
  background-color: #ffffff;
  color: black;
  border-radius: 12px 12px 12px 0;
  padding: 10px;
  max-width: 60%;
  word-wrap: break-word;
  border: 1px solid #ddd;
}

/* Timestamp */
.message-time {
  display: block;
  text-align: right;
  font-size: 0.75rem;
  color: #666;
  margin-top: 5px;
}

/* Chat Input */
.input-area {
  display: flex;
  gap: 10px;
  padding: 10px;
  background: white;
  border-top: 1px solid #ddd;
}

.chat-input {
  flex: 1;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 20px;
}

.send-button {
  padding: 10px 20px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 20px;
  cursor: pointer;
}

.send-button:hover {
  background-color: #0056b3;
}

/* Video container */
.video-container {
  position: relative;
  width: 100%;
  margin-bottom: 20px;
}

/* Responsive adjustments */
@media (max-width: 991px) {
  .chat-interface {
    width: 50%; /* Matches col-md-6 */
  }
}

@media (max-width: 767px) {
  .chat-interface {
    width: 100%; /* Full width on mobile */
  }
}

/* Style for maximize button */
.maximize-button {
  padding: 10px 20px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 20px;
  cursor: pointer;
}

.maximize-button:hover {
  background-color: #0056b3;
}

.relevant-segments {
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px solid #eee;
}

.relevant-segment {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px;
  margin: 5px 0;
  background: #f8f9fa;
  border-radius: 6px;
  font-size: 0.9em;
}

.segment-info {
  color: #666;
}

.segment-button {
  padding: 6px 12px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.segment-button:hover {
  background-color: #0056b3;
}

.chat-header {
  padding: 10px;
  border-bottom: 1px solid #eee;
  margin-bottom: 10px;
}

.search-scope {
  display: flex;
  align-items: center;
}

/* Toggle Switch Styles */
.switch {
  position: relative;
  display: inline-flex;
  align-items: center;
  cursor: pointer;
}

.switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.slider {
  position: relative;
  display: inline-block;
  width: 50px;
  height: 24px;
  background-color: #ccc;
  border-radius: 24px;
  transition: .4s;
  margin-right: 10px;
}

.slider:before {
  position: absolute;
  content: "";
  height: 16px;
  width: 16px;
  left: 4px;
  bottom: 4px;
  background-color: white;
  border-radius: 50%;
  transition: .4s;
}

input:checked + .slider {
  background-color: #007bff;
}

input:checked + .slider:before {
  transform: translateX(26px);
}

.switch-label {
  font-size: 0.9em;
  color: #666;
}

/* Update chat interface to accommodate header */
.chat-interface {
  display: flex;
  flex-direction: column;
}

.chat-messages {
  flex: 1;
  min-height: 0; /* Important for proper scrolling */
}

/* Adjust padding for maximized state */
.chat-interface.maximized .chat-header {
  padding: 15px;
}

/* Updated Loading Animation Styles */
.typing-indicator {
  background-color: #f0f0f0;
  padding: 15px;
  border-radius: 15px;
  display: inline-block;
}

.dots {
  display: flex;
  gap: 4px;
}

.typing-indicator span {
  display: inline-block;
  width: 8px;
  height: 8px;
  background-color: #007bff;
  border-radius: 50%;
  animation: bounce 1.3s ease infinite;
  opacity: 0.6;
}

.typing-indicator span:nth-child(2) {
  animation-delay: 0.15s;
}

.typing-indicator span:nth-child(3) {
  animation-delay: 0.3s;
}

@keyframes bounce {
  0%, 60%, 100% {
    transform: translateY(0);
  }
  30% {
    transform: translateY(-4px);
  }
}

/* Disabled state styles */
.chat-input:disabled {
  background-color: #f8f9fa;
  cursor: not-allowed;
}

.send-button:disabled {
  background-color: #6c757d;
  cursor: not-allowed;
}

/* Make sure the loading indicator is visible */
.message.ai-message .typing-indicator {
  margin: 10px 0;
  min-width: 60px;
}

.no-content {
  color: #6c757d;
  font-style: italic;
  padding: 15px;
  text-align: center;
  background: #f8f9fa;
  border-radius: 8px;
  margin-bottom: 15px;
}

/* Add a full-page loading overlay */
.dashboard::before {
  content: '';
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(255, 255, 255, 0.8);
  z-index: 1000;
  display: flex;
  justify-content: center;
  align-items: center;
  pointer-events: none;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.dashboard.initializing::before {
  opacity: 1;
  pointer-events: all;
}

.dashboard::after {
  content: 'Loading...';
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 24px;
  color: #1976D2;
  z-index: 1001;
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.3s ease;
}

.dashboard.initializing::after {
  opacity: 1;
}
</style>
