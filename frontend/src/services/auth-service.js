import axios from './http-common';
import store from "../store"; // Assuming this is your Axios instance

class AuthService {
    async login(user) {
        try {
            const response = await axios.post('auth/login', {
                email: user.email,
                password: user.password,
            });
            console.log(response.data)
            const {access_token, token_type} = response.data
            localStorage.setItem('token', access_token)

            return response.data; // Return the response data, including the token
        } catch (error) {
            console.error('Login failed in AuthService:', error);
            throw error; // Rethrow the error so the component can handle it
        }

    }

    async getUser() {
        const response = await axios.get('auth/me')
        console.log(response)
        localStorage.setItem('user', JSON.stringify(response.data))
        return response.data
    }

    async logout() {
        // await store.dispatch('auth/logout'); // Dispatch logout action to Vuex
    }
}

export default new AuthService();