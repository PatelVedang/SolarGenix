import axios from "axios";

const AUTH_BASE_URL = "http://localhost:5000"; // Authentication API

export const loginUser = async (credentials: any) => {
    try {
        const response = await axios.post(`${AUTH_BASE_URL}/users/login/`, credentials);
        return response.data;
    } catch (error: any) {
        console.error("Login Error:", error.response?.data || error.message);
        throw error;
    }
};

export const registerUser = async (userData: any) => {
    try {
        const response = await axios.post(`${AUTH_BASE_URL}/users/register/`, userData);
        return response.data;
    } catch (error: any) {
        console.error("Registration Error:", error.response?.data || error.message);
        throw error;
    }
};
