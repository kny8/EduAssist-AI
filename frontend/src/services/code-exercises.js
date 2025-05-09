import axios from './http-common';

/**
 * Service for interacting with the code exercises API
 */
class CodeExercisesService {
    /**
     * Get all code exercises with optional filtering
     * @param {Object} filters - Optional filters (difficulty, category, lecture_id)
     * @returns {Promise} - Promise with the list of code exercises
     */
    getExercises(filters = {}) {
        return axios.get('/code-exercises', {params: filters});
    }

    /**
     * Get a specific code exercise by ID
     * @param {number} id - The exercise ID
     * @returns {Promise} - Promise with the exercise details
     */
    getExercise(id) {
        return axios.get(`/code-exercises/${id}`);
    }

    /**
     * Create a new code exercise
     * @param {Object} data - The exercise data
     * @param {string} data.title - The title of the exercise
     * @param {string} data.description - The description/question of the exercise
     * @param {string} data.difficulty - The difficulty level
     * @param {string} data.category - The category of the exercise
     * @returns {Promise} - Response from the API
     */
    async createExercise(data) {
        return axios.post('/code-exercises', data);
    }

    /**
     * Generate test cases for a code exercise
     * @param {Object} data - The request data (code_exercise_id, problem_description, sample_code, num_test_cases)
     * @returns {Promise} - Promise with the generated test cases
     */
    generateTestCases(data) {
        return axios.post(`/code-exercises/${data.code_exercise_id}/test-cases`, data);
    }

    /**
     * Submit code for a code exercise
     * @param {Object} submission - The submission data (user_id, code_exercise_id, code, language)
     * @returns {Promise} - Promise with the submission results
     */
    submitCode(submission) {
        return axios.post('/code-exercises/submissions', submission);
    }

    /**
     * Get a specific submission by ID
     * @param {number} id - The submission ID
     * @returns {Promise} - Promise with the submission details
     */
    getSubmission(id) {
        return axios.get(`/code-exercises/submissions/${id}`);
    }

    /**
     * Get all submissions for a user
     * @param {number} userId - The user ID
     * @param {number} exerciseId - Optional exercise ID to filter by
     * @returns {Promise} - Promise with the list of submissions
     */
    getUserSubmissions(userId, exerciseId = null) {
        let url = `/code-exercises/submissions/user/${userId}`;
        if (exerciseId) {
            url += `?exercise_id=${exerciseId}`;
        }
        return axios.get(url);
    }

    /**
     * Create a new code chat session
     * @param {Object} chat - The chat data (user_id, code_exercise_id, code_submission_id)
     * @returns {Promise} - Promise with the created chat
     */
    createChat(chat) {
        return axios.post('/code-exercises/chat', chat);
    }

    /**
     * Get a specific chat by ID
     * @param {number} id - The chat ID
     * @returns {Promise} - Promise with the chat details
     */
    getChat(id) {
        return axios.get(`/code-exercises/chat/${id}`);
    }

    /**
     * Add a message to a chat
     * @param {number} chatId - The chat ID
     * @param {Object} message - The message data (sender, message, code_snippet)
     * @returns {Promise} - Promise with the created message
     */
    addChatMessage(chatId, message) {
        return axios.post(`/code-exercises/chat/${chatId}/messages`, message);
    }

    /**
     * Get all chats for a user
     * @param {number} userId - The ID of the user
     * @returns {Promise} - Response from the API
     */
    async getUserChats(userId) {
        return axios.get(`/code-exercises/chat/user/${userId}`);
    }

    /**
     * Upload a question file and extract text from it
     * @param {File} file - The file to upload
     * @returns {Promise} - Promise with the extracted text
     */
    uploadQuestionFile(file) {
        const formData = new FormData();
        formData.append('file', file);

        return axios.post('/code-exercises/upload-question', formData, {
            headers: {
                'Content-Type': 'multipart/form-data'
            }
        });
    }


    /**
     * Generate boilerplate code based on the question and selected language
     * @param {Object} data - The request data (question, language)
     * @returns {Promise} - Promise with the generated boilerplate code
     */
    generateBoilerplate(data) {
        return axios.post(`/code-exercises/${data.exercise_id}/generate-boilerplate`, data);
    }


    /**
     * Update a code exercise
     * @param {number} id - The ID of the exercise to update
     * @param {Object} data - The update data
     * @returns {Promise} - Promise with the updated exercise
     */
    updateExercise(id, data) {
        return axios.put(`/code-exercises/${id}`, data);
    }

    /**
     * Get existing test cases for a code exercise
     * @param {number} exerciseId - The ID of the code exercise
     * @returns {Promise} - Response from the API
     */
    async getTestCases(exerciseId) {
        return axios.get(`/code-exercises/${exerciseId}/test-cases`);
    }

    /**
     * Get the next test case for a code exercise
     * @param {number} exerciseId - The ID of the code exercise
     * @param {number} testCaseIndex - The index of the test case to get
     * @returns {Promise} - Response from the API with the next test case
     */
    async getNextTestCase(exerciseId, testCaseIndex) {
        return axios.get(`/code-exercises/${exerciseId}/test-cases/${testCaseIndex}`);
    }

    /**
     * Run a single test case
     * @param {Object} data - The test data
     * @param {string} data.code - The code to test
     * @param {Object} data.testCase - The test case to run
     * @returns {Promise} - Response from the API
     */
    async runSingleTest(data) {
        return axios.post('/code-exercises/run-single-test', data);
    }

    /**
     * Run multiple test cases
     * @param {Object} data - The test data
     * @param {string} data.code - The code to test
     * @param {string} data.language - The programming language
     * @param {Array} data.test_cases - Array of test cases to run
     * @returns {Promise} - Response from the API
     */
    async runTests(data) {
        return axios.post('/code-exercises/run-tests', data);
    }

    /**
     * Search Google for relevant content related to the coding question
     * @param {string} exercise_id - The ID of the code exercise
     * @returns {Promise} - Response from the API with search results
     */
    async searchGoogle(exercise_id) {
        return axios.post(`/code-exercises/${exercise_id}/search-google`, {
            exercise_id: exercise_id
        });
    }


}

export default new CodeExercisesService(); 