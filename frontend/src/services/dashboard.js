import axios from './http-common';

export const DashboardService = {
    async getQuizzes(weekId) {
        try {
            const response = await axios.get(`/quizzes?week_id=${weekId}`);
            return response.data;
        } catch (error) {
            console.error('Error fetching quizzes:', error);
            throw error;
        }
    },

    async getUpcomingQuizzes() {
        try {
            const response = await axios.get('/quizzes/upcoming');
            return response.data;
        } catch (error) {
            console.error('Error fetching upcoming quizzes:', error);
            throw error;
        }
    },
    async getStudentDashboard() {
        try {
            const response = await axios.get('/dashboards/student_dashboard');
            return response.data;
        } catch (error) {
            console.error('Error fetching dashboard data:', error);
            throw error;
        }
    },
    
    async getTeacherDashboard(weekId) {
        try {
            const url = weekId ? `/dashboards/teacher_dashboard?week_id=${weekId}` : '/dashboards/teacher_dashboard';
            const response = await axios.get(url);
            return response.data;
        } catch (error) {
            console.error('Error fetching teacher dashboard data:', error);
            throw error;
        }
    },
    
    async getQuizzesForWeek(weekId) {
        try {
            const response = await axios.get(`/dashboards/quizzes_for_week/${weekId}`);
            return response.data;
        } catch (error) {
            console.error('Error fetching quizzes for week:', error);
            throw error;
        }
    },
    
    async getQuizPerformance(quizId) {
        try {
            const response = await axios.get(`/dashboards/quiz_performance/${quizId}`);
            return response.data;
        } catch (error) {
            console.error('Error fetching quiz performance data:', error);
            throw error;
        }
    }
}; 