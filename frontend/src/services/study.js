import axios from "@services/http-common";

export default {
    /**
     * Search for relevant study content
     * @param {number} lecture_id - The ID of the lecture
     * @param {string} query - Optional search query
     * @returns {Promise} - Response from the API with search results
     */
    async searchContent(lecture_id, query = "") {
        return axios.post(`/lectures/search-google`, {
            lecture_id,
            query
        });
    },
    async fetchContent(lecture_id, query = "") {
        return axios.get(`/lectures/${lecture_id}/search-google`);
    },

    /**
     * Get relevant content for a lecture
     * @param {number} lecture_id - The ID of the lecture
     * @returns {Promise} - Response from the API with relevant content
     */
    async getRelevantContent(lecture_id) {
        return axios.get(`/relevant-content/${lecture_id}`);
    }
}; 