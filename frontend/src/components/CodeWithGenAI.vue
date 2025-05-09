<template>
  <div class="student-dashboard">
    <div class="container">
      <!-- Left Panel - Chat -->
      <div class="chat-panel">
        <div class="chat-header">
          <h3>Chat with GenAI</h3>
        </div>
        <div class="chat-messages" ref="chatContainer">
          <div
              v-for="msg in chatMessages"
              :key="msg.id"
              :class="['message', msg.sender === 'user' ? 'user-message' : 'ai-message']"
          >
            <div class="message-content">
              <div v-html="formatMessage(msg.message)"></div>
              <span class="message-time">{{ formatTimestamp(msg.created_at) }}</span>
            </div>
          </div>

          <!-- Loading indicator -->
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
              placeholder="Ask about your code..."
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
        </div>
      </div>

      <!-- Center Panel - Code Editor -->
      <div class="code-panel">
        <div class="code-header">
          <h2>Code Editor</h2>
          <div class="language-selector">
            <label for="language-select">Language:</label>
            <select
                id="language-select"
                v-model="selectedLanguage"
                class="language-select"
            >
              <option value="python">Python</option>
              <option value="javascript">JavaScript</option>
              <option value="java">Java</option>
              <option value="cpp">C++</option>
              <option value="csharp">C#</option>
            </select>
          </div>
        </div>

        <!-- Question Section -->
        <div class="question-section" v-if="!currentQuestion">
          <div class="question-input">
            <div class="file-upload">
              <label for="question-file" class="file-upload-label">
                <span class="upload-icon">📄</span>
                <span>Upload File</span>
              </label>
              <input
                  type="file"
                  id="question-file"
                  class="file-input"
                  accept=".pdf,.doc,.docx,.txt"
                  @change="handleFileUpload"
              />
              <span v-if="uploadedFileName" class="file-name">{{ uploadedFileName }}</span>
            </div>
            <div class="or-divider">
              <span>OR</span>
            </div>
            <div class="text-paste">
              <textarea
                  placeholder="Paste your question statement here..."
                  v-model="questionText"
              ></textarea>
              <button
                  class="submit-question-button"
                  @click="submitQuestionText"
                  :disabled="!questionText.trim()"
              >
                Submit Question
              </button>
            </div>
          </div>
        </div>

        <!-- Active Question Display -->
        <div class="active-question" v-if="currentQuestion">
          <div class="question-header">
            <h3>Current Question</h3>
            <button class="change-question-button" @click="changeQuestion">
              Change Question
            </button>
          </div>
          <div class="question-content">
            <p class="question-text">{{ currentQuestion }}</p>
          </div>
        </div>

        <!-- Code Editor -->
        <div class="code-editor-container" v-if="currentQuestion">
          <div v-if="isGeneratingBoilerplate" class="code-editor-loading">
            <div class="loading-spinner"></div>
            <span>Generating boilerplate code...</span>
          </div>
          <div v-else class="monaco-editor-wrapper">
            <MonacoEditor
                v-model:value="codeInput"
                theme="vs-dark"
                :options="{
                language: 'python',
                automaticLayout: true,
                minimap: { enabled: true },
                scrollBeyondLastLine: false,
                fontSize: 14,
                tabSize: 4,
                renderLineHighlight: 'all',
                padding: { top: 16 },
                suggest: {
                  snippetsPreventQuickSuggestions: false
                }
              }"
                @change="handleEditorChange"
            />
          </div>
          <div class="editor-actions">
            <div class="action-buttons">
              <button
                  class="action-button run-button"
                  @click="runCode"
                  :disabled="isCodeRunning"
              >
                <span v-if="!isCodeRunning" class="button-icon">▶</span>
                <span v-else class="loading-spinner"></span>
                {{ isCodeRunning ? 'Running...' : 'Run Code' }}
              </button>
              <button
                  class="action-button clear-button"
                  @click="clearCode"
                  :disabled="isCodeRunning"
              >
                <span class="button-icon">✕</span> Clear
              </button>
            </div>
          </div>
        </div>

        <!-- Test Cases Section -->
        <div class="test-cases-container" v-if="currentQuestion">
          <div class="test-cases-header">
            <h3>Test Cases</h3>
          </div>

          <div v-if="isLoadingTestCases" class="test-cases-loading">
            <div class="loading-spinner"></div>
            <span>Loading test cases...</span>
          </div>

          <div v-else-if="testCasesList.length > 0" class="test-cases-table">
            <table>
              <thead>
              <tr>
                <th>#</th>
                <th>Test Arguments</th>
                <th>Expected Output</th>
                <th>Actual Output</th>
                <th>Status</th>
              </tr>
              </thead>
              <tbody>
              <tr v-for="(testCase, index) in testCasesList" :key="index">
                <td>{{ index + 1 }}</td>
                <td>
                  <pre>{{ testCase.input_data }}</pre>
                </td>
                <td>
                  <pre>{{ testCase.expected_output }}</pre>
                </td>
                <td>
                    <pre v-if="testCase.result" :class="{ 'output-error': !testCase.result.passed }">
                      {{ testCase.result?.actual_output || 'Not run yet' }}
                    </pre>
                  <pre v-else>Not run yet</pre>
                </td>
                <td>
                    <span
                        class="status-badge"
                        :class="{
                        'status-passed': testCase.result?.passed,
                        'status-failed': testCase.result?.passed === false,
                        'status-pending': !testCase.result
                      }"
                    >
                      {{ testCase.result ? (testCase.result.passed ? 'PASSED' : 'FAILED') : 'PENDING' }}
                    </span>
                </td>
              </tr>
              </tbody>
            </table>
          </div>

          <div v-else class="no-test-cases">
            Submit your code to generate and run test cases
          </div>
        </div>
      </div>

      <!-- Right Panel - Relevant Content -->
      <div class="relevant-content-panel">
        <div class="relevant-content-header">
          <h3>Relevant Content</h3>
        </div>
        <div class="relevant-content-body">
          <div class="search-results" v-if="searchResults.length > 0">
            <div v-for="(result, index) in searchResults" :key="index" class="search-result-item">
              <a :href="result.link" target="_blank" class="result-title">{{ result.title }}</a>
              <p class="result-snippet">{{ result.snippet }}</p>
              <div class="result-meta">
                <span class="result-source">{{ result.source }}</span>
                <span class="result-date">{{ result.date }}</span>
              </div>
            </div>
          </div>
          <div v-else class="no-content">
            No relevant content found yet. Try asking a question!
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import * as monaco from 'monaco-editor';
import {defineComponent} from 'vue';
import MonacoEditor from 'monaco-editor-vue3';
import CodeExercisesService from '@/services/code-exercises';
import {marked} from 'marked';

export default defineComponent({
  name: 'CodeWithGenAI',
  components: {
    MonacoEditor,
  },
  data() {
    return {
      chatMessages: [
        {
          id: 1,
          sender: 'ai',
          message: 'Hello! I can help you with your coding questions. Upload your code or ask me a question.',
          created_at: new Date().toISOString()
        }
      ],
      newMessage: '',
      isLoading: false,
      isCodeRunning: false,
      uploadedFileName: '',
      questionText: '',
      questionFile: null,
      questionSubmitted: false,
      questionSource: '', // 'file' or 'text'
      codeInput: '',
      testCases: '',
      expectedOutput: '',
      actualOutput: '',
      hasError: false,
      currentUser: null,
      codeChat: null,
      codeExercise: null,
      codeSubmission: null,
      testCasesList: [],
      selectedLanguage: 'python',
      currentQuestion: null,
      isSubmittingQuestion: false,
      searchResults: [],
      isGeneratingBoilerplate: false,
      isLoadingTestCases: false,
      testCasesGenerated: false,
      currentTestCaseIndex: 0,
      isLoadingNextTest: false,
      hasMoreTestCases: true,
    };
  },
  methods: {
    async initializeUser() {
      const userStr = localStorage.getItem("user");
      this.currentUser = userStr ? JSON.parse(userStr) : null;
    },

    async createCodeExercise() {
      if (!this.currentUser || !this.questionText.trim()) return;

      try {
        const response = await CodeExercisesService.createExercise({
          title: 'Custom Exercise',
          description: this.questionText,
          difficulty: 'Medium',
          category: 'Custom'
        });

        this.codeExercise = response.data;

        // Generate test cases based on the problem description
        await this.generateTestCases();

        return this.codeExercise;
      } catch (error) {
        console.error('Error creating code exercise:', error);
        this.simulateAIResponse('There was an error creating the code exercise. Please try again.');
      }
    },

    async generateTestCases() {
      if (!this.codeExercise) return;

      try {
        this.isLoading = true;
        
        // Add a message to the chat about generating test cases
        this.chatMessages.push({
          id: Date.now(),
          sender: 'ai',
          message: 'Generating test cases for your problem...',
          created_at: new Date().toISOString()
        });
        this.scrollToBottom();

        const response = await CodeExercisesService.generateTestCases({
          code_exercise_id: this.codeExercise.id,
          problem_description: this.codeExercise.description,
          sample_code: this.codeInput,
          num_test_cases: 3
        });

        // Process test cases to clean up any placeholder text
        this.testCasesList = response.data.test_cases
          .map(tc => ({
            ...tc,
            input_data: this.formatTestInput(tc.input_data),
            expected_output: this.formatTestInput(tc.expected_output)
          }));
        
        // Add a message to the chat about the generated test cases
        this.chatMessages.push({
          id: Date.now(),
          sender: 'ai',
          message: 'I\'ve generated test cases for your code. You can now run your code against these test cases.',
          created_at: new Date().toISOString()
        });
        this.scrollToBottom();

      } catch (error) {
        console.error('Error generating test cases:', error);
        this.showError('Error generating test cases: ' + (error.message || 'Unknown error'));
      } finally {
        this.isLoading = false;
      }
    },

    async runTestCases() {
      if (!this.testCasesList.length || !this.codeInput.trim()) return;

      try {
        const response = await CodeExercisesService.runTests({
          code: this.codeInput,
          language: this.selectedLanguage,
          test_cases: this.testCasesList
        });

        // Update test cases with results
        this.testCasesList = this.testCasesList.map((tc, index) => ({
          ...tc,
          result: response.data.results[index]
        }));
      } catch (error) {
        console.error('Error running test cases:', error);
      }
    },

    async submitCode() {
      if (!this.currentUser || !this.codeExercise || !this.codeInput.trim()) {
        this.actualOutput = 'Error: Please provide code and a question statement.';
        this.hasError = true;
        return;
      }

      try {
        this.isCodeRunning = true;

        const submission = {
          user_id: this.currentUser.id,
          code_exercise_id: this.codeExercise.id,
          code: this.codeInput,
          language: this.selectedLanguage
        };

        const response = await CodeExercisesService.submitCode(submission);
        this.codeSubmission = response.data;

        // Format the results for display
        const results = this.codeSubmission.results;
        this.actualOutput = `Execution completed in ${this.codeSubmission.execution_time}ms\n`;
        this.actualOutput += `Memory used: ${this.codeSubmission.memory_used}KB\n\n`;
        this.actualOutput += `Tests passed: ${results.passed}/${results.passed + results.failed}\n\n`;

        // Show detailed test results
        results.test_results.forEach((result, index) => {
          this.actualOutput += `Test Case ${index + 1}:\n`;
          this.actualOutput += `Input: ${result.input}\n`;
          this.actualOutput += `Expected Output: ${result.expected_output}\n`;
          this.actualOutput += `Actual Output: ${result.actual_output}\n`;
          this.actualOutput += `Result: ${result.passed ? 'PASSED' : 'FAILED'}\n\n`;
        });

        this.hasError = results.failed > 0;

        // Add a message to the chat about the code execution
        this.chatMessages.push({
          id: Date.now(),
          sender: 'user',
          message: 'I ran my code.',
          created_at: new Date().toISOString()
        });

        // Create or update the code chat
        if (!this.codeChat) {
          await this.createCodeChat();
        }

        // Send a message to the AI about the code execution
        if (this.codeChat) {
          await this.sendCodeChatMessage(
              'user',
              'I ran my code and got the following results: ' +
              (this.hasError ? 'Some tests failed.' : 'All tests passed.'),
              this.codeInput
          );
        }
      } catch (error) {
        console.error('Error submitting code:', error);
        this.actualOutput = `Error: ${error.message || 'An error occurred while executing your code.'}`;
        this.hasError = true;
      } finally {
        this.isCodeRunning = false;
      }
    },

    async createCodeChat() {
      if (!this.currentUser || !this.codeExercise) return;

      try {
        const response = await CodeExercisesService.createChat({
          user_id: this.currentUser.id,
          code_exercise_id: this.codeExercise.id,
          code_submission_id: this.codeSubmission?.id
        });

        this.codeChat = response.data;

        // Add the welcome message to our chat UI
        const welcomeMessage = this.codeChat.messages[0];
        if (welcomeMessage && welcomeMessage.sender === 'ai') {
          this.chatMessages.push({
            id: welcomeMessage.id,
            sender: welcomeMessage.sender,
            message: welcomeMessage.message,
            created_at: welcomeMessage.created_at
          });

          this.scrollToBottom();
        }
      } catch (error) {
        console.error('Error creating code chat:', error);
      }
    },

    async sendCodeChatMessage(sender, message, codeSnippet = null) {
      if (!this.codeChat) return;

      try {
        const response = await CodeExercisesService.addChatMessage(this.codeChat.id, {
          sender,
          message,
          code_snippet: codeSnippet
        });

        // The AI response will be automatically generated by the backend
        // and returned in subsequent calls to getCodeChat
        await this.fetchCodeChat();
      } catch (error) {
        console.error('Error sending chat message:', error);
      }
    },

    async fetchCodeChat() {
      if (!this.codeChat) return;

      try {
        const response = await CodeExercisesService.getChat(this.codeChat.id);

        // Update our local chat with any new messages
        const newMessages = response.data.messages;

        // Find messages that aren't in our current chat
        const existingIds = this.chatMessages.map(msg => msg.id);
        const messagesToAdd = newMessages.filter(msg => !existingIds.includes(msg.id));

        // Add new messages to our chat
        messagesToAdd.forEach(msg => {
          this.chatMessages.push({
            id: msg.id,
            sender: msg.sender,
            message: msg.message,
            created_at: msg.created_at
          });
        });

        if (messagesToAdd.length > 0) {
          this.scrollToBottom();
        }
      } catch (error) {
        console.error('Error fetching code chat:', error);
      }
    },

    async runCode() {
      if (!this.codeInput.trim()) {
        this.showError('Please enter some code first.');
        return;
      }

      try {
        this.isCodeRunning = true;
        
        // First generate some test cases if we don't have any
        if (this.testCasesList.length === 0) {
          await this.generateTestCases();
        }
        
        // Submit code with the generated test cases
        if (!this.currentUser || !this.codeExercise) {
          this.showError('Please ensure you have a question and are logged in.');
          return;
        }
        
        // Run the tests directly instead of using submission endpoint
        const testResponse = await CodeExercisesService.runTests({
          code: this.codeInput,
          language: this.selectedLanguage,
          test_cases: this.testCasesList
        });
        
        // Update test cases with results
        if (testResponse.data && testResponse.data.results) {
          const results = testResponse.data.results;
          let passedCount = 0;
          let failedCount = 0;
          
          this.testCasesList = this.testCasesList.map((tc, index) => {
            const resultData = results[index] || {};
            if (resultData.passed) passedCount++;
            else failedCount++;
            
            return {
              ...tc,
              result: {
                actual_output: resultData.actual_output || 'No output',
                passed: resultData.passed || false,
                error: resultData.error || null
              }
            };
          });
          
          // Add a message to the chat about the test results
          this.chatMessages.push({
            id: Date.now(),
            sender: 'ai',
            message: `I've run your code. ${passedCount} test(s) passed out of ${passedCount + failedCount} total.`,
            created_at: new Date().toISOString()
          });
          this.scrollToBottom();
        }
      } catch (error) {
        console.error('Error running code:', error);
        this.showError('Error running code: ' + (error.response?.data?.detail || error.message || 'Unknown error'));
      } finally {
        this.isCodeRunning = false;
      }
    },

    sendMessage() {
      if (!this.newMessage.trim() || this.isLoading) return;

      const userMessage = this.newMessage;
      this.newMessage = '';
      this.isLoading = true;

      // Add user message to chat
      this.chatMessages.push({
        id: Date.now(),
        sender: 'user',
        message: userMessage,
        created_at: new Date().toISOString()
      });

      // If we have a code chat, send the message to the API
      if (this.codeChat) {
        this.sendCodeChatMessage('user', userMessage);
        return;
      }

      // Otherwise, use the simulated response
      this.simulateAIResponse('I received your message: "' + userMessage + '". This is a placeholder response. In a real implementation, this would be connected to a backend API.');
    },

    async submitQuestionText() {
      if (!this.questionText.trim()) return;

      try {
        this.isLoading = true;
        this.currentQuestion = this.questionText;

        // First create the exercise
        const exerciseResponse = await CodeExercisesService.createExercise({
          title: 'Custom Exercise',
          description: this.currentQuestion,
          difficulty: 'Medium',
          category: 'Custom'
        });

        this.codeExercise = exerciseResponse.data;

        // Then generate the template
        const templateResponse = await CodeExercisesService.generateBoilerplate({
          // question: this.currentQuestion,
          exercise_id: exerciseResponse.data.id,
          language: this.selectedLanguage
        });

        // Update code input with function signature
        this.codeInput = templateResponse.data.function_signature;

        // Add AI message with the function signature
        this.chatMessages.push({
          id: Date.now(),
          sender: 'ai',
          message: "I've generated a function signature for your question. You can start implementing your solution.",
          created_at: new Date().toISOString()
        });

        // Search for relevant content
        await this.searchRelevantContent();

        // Clear the question input
        this.questionText = '';

      } catch (error) {
        console.error('Error:', error);
        this.chatMessages.push({
          id: Date.now(),
          sender: 'ai',
          message: 'Sorry, I encountered an error while processing your question.',
          created_at: new Date().toISOString()
        });
      } finally {
        this.isLoading = false;
        this.scrollToBottom();
      }
    },

    async searchRelevantContent() {
      if (!this.codeExercise?.id) return;

      try {
        // Call the backend API to search for relevant content
        const response = await CodeExercisesService.searchGoogle(this.codeExercise.id);
        
        // Update the search results
        this.searchResults = response.data.results || [];

      } catch (error) {
        console.error('Error searching for relevant content:', error);
        this.searchResults = [];
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
    async handleFileUpload(event) {
      const file = event.target.files[0];
      if (!file || this.isSubmittingQuestion) return;

      try {
        this.isSubmittingQuestion = true;
        this.uploadedFileName = file.name;
        this.questionFile = file;

        // Upload the file and get the extracted text
        const response = await CodeExercisesService.uploadQuestionFile(file);
        this.questionText = response.data.extracted_text;

        // Auto-submit the question
        await this.submitQuestionText();
      } catch (error) {
        console.error('Error uploading file:', error);
        // Add error handling UI feedback here
      } finally {
        this.isSubmittingQuestion = false;
      }
    },

    simulateAIResponse(message) {
      setTimeout(() => {
        this.chatMessages.push({
          id: Date.now() + 1,
          sender: 'ai',
          message: message.replace(/[\[\{]exact[^\]\}]*[\]\}]/g, ''),
          created_at: new Date().toISOString()
        });

        this.isLoading = false;
        this.scrollToBottom();
      }, 1000);
    },
    resetQuestionSubmission() {
      this.questionSubmitted = false;
      this.questionSource = '';
      this.uploadedFileName = '';
      this.questionText = '';
      this.questionFile = null;
    },
    clearCode() {
      this.codeInput = '';
      this.actualOutput = '';
      this.hasError = false;
    },
    async changeQuestion() {
      // Clear current question and related data
      this.currentQuestion = null;
      this.codeExercise = null;
      this.testCasesList = [];
      this.testCases = '';
      this.expectedOutput = '';
      this.actualOutput = '';
      this.codeInput = '';

      // Reset chat
      this.codeChat = null;
      this.chatMessages = [{
        id: Date.now(),
        sender: 'ai',
        message: 'Hello! I can help you with your coding questions. Upload your code or ask me a question.',
        created_at: new Date().toISOString()
      }];

      // Clear from localStorage
      localStorage.removeItem('currentQuestion');
      localStorage.removeItem('currentExerciseId');

      // Scroll chat to bottom
      this.scrollToBottom();
    },
    async initializeComponent() {
      await this.initializeUser();

      try {
        const response = await CodeExercisesService.getUserChats(this.currentUser.id);
        if (response.data && response.data.length > 0) {
          // Get the most recent chat
          const mostRecentChat = response.data[0];
          this.codeChat = mostRecentChat;

          // Load the associated exercise
          if (mostRecentChat.code_exercise_id) {
            try {
              const exerciseResponse = await CodeExercisesService.getExercise(mostRecentChat.code_exercise_id);
              this.codeExercise = exerciseResponse.data;
              this.currentQuestion = this.codeExercise.description;

              // Set the boilerplate code if it exists
              if (this.codeExercise.boilerplate_code) {
                this.codeInput = this.codeExercise.boilerplate_code;
              }

              // Set the language if it exists
              if (this.codeExercise.language) {
                this.selectedLanguage = this.codeExercise.language;
              }
              if (this.codeExercise.description) {
                await this.searchRelevantContent();
              }

              // Load the chat messages
              await this.fetchCodeChat();

              // Only try to load test cases if we have a valid exercise
              if (this.codeExercise?.id) {
                try {
                  const testCasesResponse = await CodeExercisesService.getTestCases(this.codeExercise.id);
                  this.testCasesList = testCasesResponse.data || [];
                } catch (error) {
                  if (error.response?.status === 404) {
                    console.log('No test cases found for this exercise');
                    this.testCasesList = [];
                  } else {
                    console.error('Error loading test cases:', error);
                  }
                }
              }
            } catch (error) {
              if (error.response?.status === 404) {
                console.error('Exercise not found:', mostRecentChat.code_exercise_id);
                this.showError('The associated exercise could not be found.');
              } else {
                console.error('Error loading exercise:', error);
                this.showError('Error loading the exercise.');
              }
            }
          }
        } else {
          // No existing chat, show welcome message
          this.chatMessages.push({
            id: Date.now(),
            sender: 'ai',
            message: 'Hello! I can help you with your coding questions. Upload your code or ask me a question.',
            created_at: new Date().toISOString()
          });
        }
      } catch (error) {
        console.error('Error loading existing chat:', error);
        this.chatMessages.push({
          id: Date.now(),
          sender: 'ai',
          message: 'Hello! I can help you with your coding questions. Upload your code or ask me a question.',
          created_at: new Date().toISOString()
        });
      }

      this.scrollToBottom();
    },
    async generateNextTestCase() {
      try {
        this.isGeneratingTestCase = true;
        const response = await CodeExercisesService.generateNextTestCase({
          code_exercise_id: this.codeExercise.id,
          code: this.codeInput,
          language: this.selectedLanguage
        });

        this.currentTestCase = response.data.test_case;
        this.currentTestCaseResult = response.data.result;
      } catch (error) {
        console.error('Error generating test case:', error);
        this.error = 'Failed to generate test case';
      } finally {
        this.isGeneratingTestCase = false;
      }
    },
    handleEditorChange(value) {
      this.codeInput = value;
    },
    formatTestInput(input) {
      try {
        // If input is a string representation of an object/array, parse and format it
        if (typeof input === 'string' && (input.startsWith('{') || input.startsWith('['))) {
          return JSON.stringify(JSON.parse(input), null, 2);
        }
        // If input contains [exact input] or similar placeholders, clean it
        if (input.includes('[exact') || input.includes('{exact')) {
          return input.replace(/[\[\{]exact[^\]\}]*[\]\}]/g, '').trim();
        }
        return input;
      } catch (e) {
        return input;
      }
    },
    formatMessage(message) {
      try {
        // Remove any [exact input] or similar placeholders
        message = message.replace(/[\[\{]exact[^\]\}]*[\]\}]/g, '');

        // Convert markdown to HTML
        const html = marked(message);

        // Add syntax highlighting classes
        return html.replace(/<code>/g, '<code class="hljs">');
      } catch (e) {
        return message;
      }
    },
    showError(message) {
      // Display error as a chat message
      this.chatMessages.push({
        id: Date.now(),
        sender: 'ai',
        message: `⚠️ ${message}`,
        created_at: new Date().toISOString()
      });
      this.scrollToBottom();
    },
  },
  async mounted() {
    await this.initializeComponent();
    this.scrollToBottom();
  }
});
</script>

<style scoped>
.student-dashboard {
  height: 100vh;
  background-color: #f0f2f5;
  overflow: hidden;
}

.container {
  display: grid;
  grid-template-columns: 350px 1fr 350px;
  height: 100vh;
  gap: 1px;
  background-color: #ddd;
}

/* Chat Panel Styles */
.chat-panel {
  background-color: white;
  display: flex;
  flex-direction: column;
  height: 100vh;
  overflow: hidden;
}

.chat-header {
  padding: 16px;
  background-color: #f0f2f5;
  border-bottom: 1px solid #ddd;
  flex-shrink: 0;
}

.chat-header h3 {
  margin: 0;
  font-size: 16px;
  color: #1a1a1a;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  background-color: #f0f2f5;
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-height: 0; /* Important for Firefox */
}

.message {
  max-width: 85%;
  padding: 8px 12px;
  border-radius: 12px;
  position: relative;
}

.user-message {
  align-self: flex-end;
  background-color: #dcf8c6;
  border-radius: 12px 12px 0 12px;
}

.ai-message {
  align-self: flex-start;
  background-color: white;
  border-radius: 12px 12px 12px 0;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.message-content {
  position: relative;
}

.message-time {
  font-size: 11px;
  color: #667781;
  margin-top: 4px;
  display: block;
  text-align: right;
}

.input-area {
  padding: 12px;
  background-color: #f0f2f5;
  border-top: 1px solid #ddd;
  display: flex;
  gap: 8px;
  flex-shrink: 0;
}

.chat-input {
  flex: 1;
  padding: 12px;
  border: none;
  border-radius: 24px;
  background-color: white;
  font-size: 14px;
}

.send-button {
  width: 40px;
  height: 40px;
  border: none;
  border-radius: 50%;
  background-color: #128c7e;
  color: white;
  font-size: 20px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.send-button:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

/* Code Panel Styles */
.code-panel {
  background-color: white;
  display: flex;
  flex-direction: column;
  height: 100vh;
  overflow: hidden;
}

.code-header {
  padding: 16px;
  background-color: #f0f2f5;
  border-bottom: 1px solid #ddd;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-shrink: 0;
}

.code-editor-container {
  flex: 1;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  min-height: 0; /* Important for Firefox */
  overflow: hidden;
}

.monaco-editor-wrapper {
  flex: 1;
  min-height: 0;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid #2d2d2d;
}

.monaco-editor-wrapper :deep(.monaco-editor) {
  padding: 8px 0;
}

.editor-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  flex-shrink: 0;
}

.action-buttons {
  display: flex;
  gap: 8px;
  margin-top: 16px;
}

.action-button {
  height: 36px;
  min-width: 100px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-size: 14px;
  transition: all 0.2s;
}

.run-button {
  background-color: #128c7e;
  color: white;
}

.clear-button {
  background-color: #dc3545;
  color: white;
}

.generate-button {
  background-color: #007bff;
  color: white;
}

/* Relevant Content Panel Styles */
.relevant-content-panel {
  background-color: white;
  display: flex;
  flex-direction: column;
  height: 100vh;
  border-left: 1px solid #ddd;
  overflow: hidden;
}

.relevant-content-header {
  padding: 16px;
  background-color: #f0f2f5;
  border-bottom: 1px solid #ddd;
  flex-shrink: 0;
}

.relevant-content-header h3 {
  margin: 0;
  font-size: 16px;
  color: #1a1a1a;
}

.relevant-content-body {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 24px;
  min-height: 0; /* Important for Firefox */
}

.search-results {
  background-color: #f8f9fa;
  padding: 16px;
  border-radius: 8px;
}

.search-result-item {
  background-color: white;
  padding: 16px;
  border-radius: 8px;
  margin-bottom: 12px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s;
}

.search-result-item:hover {
  transform: translateY(-2px);
}

.result-title {
  color: #128c7e;
  text-decoration: none;
  font-weight: 500;
  display: block;
  margin-bottom: 8px;
  font-size: 15px;
}

.result-title:hover {
  text-decoration: underline;
}

.result-snippet {
  font-size: 14px;
  color: #4a4a4a;
  margin: 8px 0;
  line-height: 1.5;
}

.result-meta {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #667781;
  margin-top: 8px;
}

.no-content {
  text-align: center;
  padding: 32px;
  color: #666;
  font-size: 14px;
  background-color: #f8f9fa;
  border-radius: 8px;
}

/* Test Cases Styles */
.test-cases-container {
  padding: 16px;
  background-color: #f8f9fa;
  border-radius: 8px;
  margin: 16px;
  flex-shrink: 0;
  overflow-x: auto;
}

.test-cases-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  position: sticky;
  top: 0;
  background-color: #f8f9fa;
  padding: 8px 0;
  z-index: 1;
}

.test-cases-table {
  width: 100%;
  overflow-x: auto;
}

.test-cases-table table {
  width: 100%;
  border-collapse: collapse;
  background-color: white;
  border-radius: 8px;
  overflow: hidden;
}

.test-cases-table th,
.test-cases-table td {
  padding: 12px;
  text-align: left;
  border: 1px solid #e0e0e0;
}

.test-cases-table th {
  background-color: #f0f2f5;
  font-weight: 500;
  color: #333;
  white-space: nowrap;
}

.test-cases-table td pre {
  margin: 0;
  white-space: pre-wrap;
  font-family: 'Courier New', monospace;
  font-size: 13px;
}

.test-cases-table td:first-child {
  text-align: center;
  width: 40px;
}

.status-badge {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
  text-align: center;
  white-space: nowrap;
}

.status-passed {
  background-color: #d4edda;
  color: #155724;
}

.status-failed {
  background-color: #f8d7da;
  color: #721c24;
}

.status-pending {
  background-color: #e2e3e5;
  color: #383d41;
}

.generate-button {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  height: 36px;
  white-space: nowrap;
}

.generate-button .loading-spinner {
  width: 14px;
  height: 14px;
  border-color: #ffffff;
  border-top-color: transparent;
}

.action-buttons {
  display: flex;
  gap: 8px;
  margin-top: 16px;
}

.action-button:hover {
  opacity: 0.9;
}

.action-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Question Section Styles */
.question-section {
  padding: 16px;
  flex-shrink: 0;
}

.question-input {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.file-upload {
  text-align: center;
  padding: 24px;
  border: 2px dashed #ddd;
  border-radius: 8px;
  cursor: pointer;
}

.file-upload-label {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.upload-icon {
  font-size: 24px;
}

.or-divider {
  text-align: center;
  position: relative;
}

.or-divider::before,
.or-divider::after {
  content: '';
  position: absolute;
  top: 50%;
  width: 45%;
  height: 1px;
  background-color: #ddd;
}

.or-divider::before {
  left: 0;
}

.or-divider::after {
  right: 0;
}

.text-paste textarea {
  width: 100%;
  min-height: 120px;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  resize: vertical;
}

.submit-question-button {
  padding: 8px 16px;
  background-color: #128c7e;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  margin-top: 8px;
}

.submit-question-button:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

/* Active Question Styles */
.active-question {
  padding: 16px;
  background-color: #f8f9fa;
  border-radius: 8px;
  margin: 16px;
  flex-shrink: 0;
}

.question-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.change-question-button {
  padding: 6px 12px;
  background-color: #dc3545;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

/* Loading Spinner */
.loading-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid #ffffff;
  border-top: 2px solid transparent;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

.typing-indicator {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 8px 12px;
  background-color: #f0f2f5;
  border-radius: 12px;
  width: fit-content;
}

.typing-indicator .dots {
  display: flex;
  gap: 4px;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  background-color: #128c7e;
  border-radius: 50%;
  animation: bounce 1.4s infinite ease-in-out;
}

.typing-indicator span:nth-child(1) {
  animation-delay: -0.32s;
}

.typing-indicator span:nth-child(2) {
  animation-delay: -0.16s;
}

@keyframes bounce {
  0%, 80%, 100% {
    transform: scale(0);
  }
  40% {
    transform: scale(1);
  }
}

.code-editor-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  gap: 16px;
  color: #128c7e;
  font-size: 14px;
  min-height: 0; /* Important for Firefox */
}

.message-content :deep(p) {
  margin: 0;
  line-height: 1.4;
}

.message-content :deep(code) {
  font-family: 'Courier New', monospace;
  background-color: rgba(0, 0, 0, 0.05);
  padding: 2px 4px;
  border-radius: 4px;
  font-size: 0.9em;
}

.message-content :deep(pre) {
  margin: 8px 0;
  padding: 12px;
  background-color: #f8f9fa;
  border-radius: 4px;
  overflow-x: auto;
}

.message-content :deep(pre code) {
  background-color: transparent;
  padding: 0;
  border-radius: 0;
}

.test-cases-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 32px;
  gap: 16px;
  color: #128c7e;
}

.no-test-cases {
  text-align: center;
  padding: 32px;
  color: #666;
  font-size: 14px;
  background-color: #f8f9fa;
  border-radius: 8px;
}
</style>

