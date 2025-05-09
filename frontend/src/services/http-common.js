import axios from 'axios';
import authHeader from "@/services/auth-header";


const instance = axios.create({
    baseURL: 'http://127.0.0.1:8000/',
    withCredentials: true,
    headers: {
        'Content-Type': 'application/json',
    },
});
// instance.defaults.baseURL="http://127.0.0.1:5000/"

// Add a request interceptor to include the Authorization header
instance.interceptors.request.use(
    (config) => {
        const tokenHeader = authHeader();
        if (tokenHeader) {
            config.headers = {...config.headers, ...tokenHeader};
        }
        return config;
    },
    (error) => {
        // Do something with request error
        return Promise.reject(error);
    }
);

export default instance;