import axios from "axios"
import router from '@/router'

const backend_base_url = import.meta.env.VITE_HMS_BACKEND_BASE_URL
const axios_instance = axios.create({
    baseURL: backend_base_url
})

const getAuthTokens = () => {
    const authTokens = localStorage.getItem('tokens')
    return authTokens ? JSON.parse(authTokens) : null
}

// Interceptor to add Authorization header to each request for the protected end points
axios_instance.interceptors.request.use(config => {
    const tokens = getAuthTokens()
    if (tokens?.access_token) {
        config.headers.Authorization = `Bearer ${tokens.access_token}`
    }
    return config
})

// If the Authentication token is expired or invalid for a request this interceptor will handle that
axios_instance.interceptors.response.use((response) => {
    return response;
}, async (error) => {
    const initialRequest = error.config;
    if (error.response?.status === 401){
        localStorage.clear();
        router.replace('/login');
        return Promise.reject(error);
    }
    // If the access token is expired then retry to get a new one
    if (error.response?.status === 403 && !initialRequest._retry && !initialRequest.url.includes('/api/token/refresh')){
        initialRequest._retry = true;
        const tokens = getAuthTokens()
        try {
            const retry_response = await axios.post(`${backend_base_url}/api/token/refresh`, {}, {
                headers: {
                    'Authorization': `Bearer ${tokens?.refresh_token}`
                }
            })

            const access_token = retry_response.data.access_token;

            // Store the new access_token created in the local storage and set the header again
            const newTokens = {
                ...tokens,
                access_token: access_token
            }

            localStorage.setItem('tokens', JSON.stringify(newTokens))
            initialRequest.headers.Authorization = `Bearer ${access_token}`

            return axios_instance(initialRequest);

        } catch (refreshError) {
            // If the refresh token is also expired, clear the local storage and through user to login
            // console.error("Refresh token expired.");
            localStorage.clear();
            router.replace('/login');
            return Promise.reject(refreshError);
        }
    }
    return Promise.reject(error);
    
})

export default axios_instance