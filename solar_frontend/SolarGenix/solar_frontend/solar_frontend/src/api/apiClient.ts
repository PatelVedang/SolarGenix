import axios from "axios";

const AUTH_BASE_URL = "http://localhost:5000";
const PREDICTION_BASE_URL = "http://127.0.0.1:8000";

// ─── Token helpers ──────────────────────────────────────────────
export const getAccessToken = () => localStorage.getItem("solar_token");
export const getRefreshToken = () => localStorage.getItem("solar_refresh_token");

export const setTokens = (access: string, refresh: string) => {
    localStorage.setItem("solar_token", access);
    localStorage.setItem("solar_refresh_token", refresh);
};

export const clearTokens = () => {
    localStorage.removeItem("solar_token");
    localStorage.removeItem("solar_refresh_token");
    localStorage.removeItem("solar_user");
};

// ─── Refresh logic ──────────────────────────────────────────────
let isRefreshing = false;
let failedQueue: Array<{
    resolve: (token: string) => void;
    reject: (err: any) => void;
}> = [];

const processQueue = (error: any, token: string | null = null) => {
    failedQueue.forEach((prom) => {
        if (token) prom.resolve(token);
        else prom.reject(error);
    });
    failedQueue = [];
};

const attemptTokenRefresh = async (): Promise<string> => {
    const refreshToken = getRefreshToken();
    if (!refreshToken) throw new Error("No refresh token");

    const res = await axios.post(`${AUTH_BASE_URL}/api/auth/refresh-token`, {
        refresh: refreshToken,
    });

    // Response format: { data: { access: { token, expires }, refresh: { token, expires } } }
    const { access, refresh } = res.data.data;
    setTokens(access.token, refresh.token);
    return access.token;
};

// ─── Axios instance for prediction API ──────────────────────────
export const predictionApi = axios.create({
    baseURL: PREDICTION_BASE_URL,
});

// Attach access token to every request
predictionApi.interceptors.request.use((config) => {
    const token = getAccessToken();
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

// On 401 → try to silently refresh, then retry the original request
predictionApi.interceptors.response.use(
    (response) => response,
    async (error) => {
        const originalRequest = error.config;

        // Only intercept 401s, and only once per request
        if (error.response?.status !== 401 || originalRequest._retry) {
            return Promise.reject(error);
        }

        // If we're already refreshing, queue this request
        if (isRefreshing) {
            return new Promise<string>((resolve, reject) => {
                failedQueue.push({ resolve, reject });
            })
                .then((newToken) => {
                    originalRequest.headers.Authorization = `Bearer ${newToken}`;
                    return predictionApi(originalRequest);
                })
                .catch((err) => Promise.reject(err));
        }

        originalRequest._retry = true;
        isRefreshing = true;

        try {
            const newToken = await attemptTokenRefresh();
            processQueue(null, newToken);
            originalRequest.headers.Authorization = `Bearer ${newToken}`;
            return predictionApi(originalRequest);
        } catch (refreshError) {
            processQueue(refreshError, null);
            // Refresh failed → tokens are dead → redirect to login
            clearTokens();
            window.location.href = "/login";
            return Promise.reject(refreshError);
        } finally {
            isRefreshing = false;
        }
    }
);

// ─── Plain axios instance for auth API (no interceptors) ────────
export const authApi = axios.create({
    baseURL: AUTH_BASE_URL,
});
