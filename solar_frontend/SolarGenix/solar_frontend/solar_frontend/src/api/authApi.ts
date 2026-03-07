import { authApi } from "./apiClient";

export const loginUser = async (credentials: any) => {
    try {
        const response = await authApi.post(`/api/auth/login`, credentials);
        return response.data;
    } catch (error: any) {
        console.error("Login Error:", error.response?.data || error.message);
        throw error;
    }
};

export const registerUser = async (userData: any) => {
    try {
        const response = await authApi.post(`/api/auth/register`, userData);
        return response.data;
    } catch (error: any) {
        console.error("Registration Error:", error.response?.data || error.message);
        throw error;
    }
};

export const sendOtp = async (email: string) => {
    try {
        const response = await authApi.post(`/api/auth/send-otp`, { email });
        return response.data;
    } catch (error: any) {
        console.error("Send OTP Error:", error.response?.data || error.message);
        throw error;
    }
};

export const resetPasswordOtp = async (data: any) => {
    try {
        const response = await authApi.post(`/api/auth/reset-password-otp`, data);
        return response.data;
    } catch (error: any) {
        console.error("Reset Password Error:", error.response?.data || error.message);
        throw error;
    }
};
