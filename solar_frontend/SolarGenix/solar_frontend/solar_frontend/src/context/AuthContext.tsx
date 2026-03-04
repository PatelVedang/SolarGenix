import React, { createContext, useContext, useEffect, useState } from "react";

interface AuthContextType {
    user: any;
    token: string | null;
    login: (userData: any, token: string) => void;
    logout: () => void;
    isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const [user, setUser] = useState<any>(null);
    const [token, setToken] = useState<string | null>(localStorage.getItem("solar_token"));

    useEffect(() => {
        const savedUser = localStorage.getItem("solar_user");
        if (savedUser && token) {
            setUser(JSON.parse(savedUser));
        }
    }, [token]);

    const login = (userData: any, authToken: string) => {
        setUser(userData);
        setToken(authToken);
        localStorage.setItem("solar_token", authToken);
        localStorage.setItem("solar_user", JSON.stringify(userData));
    };

    const logout = () => {
        setUser(null);
        setToken(null);
        localStorage.removeItem("solar_token");
        localStorage.removeItem("solar_user");
    };

    const isAuthenticated = !!token;

    return (
        <AuthContext.Provider value={{ user, token, login, logout, isAuthenticated }}>
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
