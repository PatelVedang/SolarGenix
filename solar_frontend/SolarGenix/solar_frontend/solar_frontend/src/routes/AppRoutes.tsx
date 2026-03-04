import { BrowserRouter, Route, Routes } from "react-router-dom";
import Navbar from "../components/Navbar";
import ProtectedRoute from "../components/ProtectedRoute";
import { AuthProvider } from "../context/AuthContext";
import BillOptimizationPage from "../pages/BillOptimizationPage";
import BillPredictionPage from "../pages/BillPredictionPage";
import DashboardPage from "../pages/DashboardPage";
import HomePage from "../pages/HomePage";
import LoginPage from "../pages/LoginPage";
import RegisterPage from "../pages/RegisterPage";
import SolarPredictionPage from "../pages/SolarPredictionPage";

const AppRoutes = () => {
    return (
        <AuthProvider>
            <BrowserRouter>
                <Navbar />
                <Routes>
                    <Route
                        path="/"
                        element={
                            <ProtectedRoute>
                                <HomePage />
                            </ProtectedRoute>
                        }
                    />
                    <Route path="/login" element={<LoginPage />} />
                    <Route path="/register" element={<RegisterPage />} />

                    <Route
                        path="/dashboard"
                        element={
                            <ProtectedRoute>
                                <DashboardPage />
                            </ProtectedRoute>
                        }
                    />
                    <Route
                        path="/solar-predict"
                        element={
                            <ProtectedRoute>
                                <SolarPredictionPage />
                            </ProtectedRoute>
                        }
                    />
                    <Route
                        path="/bill-predict"
                        element={
                            <ProtectedRoute>
                                <BillPredictionPage />
                            </ProtectedRoute>
                        }
                    />
                    <Route
                        path="/bill-optimization"
                        element={
                            <ProtectedRoute>
                                <BillOptimizationPage />
                            </ProtectedRoute>
                        }
                    />
                </Routes>
            </BrowserRouter>
        </AuthProvider>
    );
};

export default AppRoutes;
