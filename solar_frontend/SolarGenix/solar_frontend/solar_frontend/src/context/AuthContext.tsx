import React, { createContext, useContext, useState, useCallback, useMemo } from "react";

interface AuthContextType {
    user: any;
    token: string | null;
    login: (userData: any, token: string) => void;
    logout: () => void;
    isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const getInitialUser = () => {
    const saved = localStorage.getItem("solar_user");
    try {
        return saved ? JSON.parse(saved) : null;
    } catch (e) {
        console.error("Failed to parse user from localStorage", e);
        return null;
    }
};

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const [token, setToken] = useState<string | null>(() => localStorage.getItem("solar_token"));
    const [user, setUser] = useState<any>(getInitialUser);

    const login = useCallback((userData: any, authToken: string) => {
        localStorage.setItem("solar_token", authToken);
        localStorage.setItem("solar_user", JSON.stringify(userData));
        setToken(authToken);
        setUser(userData);
    }, []);

    const logout = useCallback(() => {
        localStorage.removeItem("solar_token");
        localStorage.removeItem("solar_user");
        setToken(null);
        setUser(null);
    }, []);

    const isAuthenticated = !!token;

    const value = useMemo(() => ({
        user,
        token,
        login,
        logout,
        isAuthenticated
    }), [user, token, login, logout, isAuthenticated]);

    return (
        <AuthContext.Provider value={value}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (context === undefined) {
        throw new Error("useAuth must be used within an AuthProvider");
    }
    return context;
};
