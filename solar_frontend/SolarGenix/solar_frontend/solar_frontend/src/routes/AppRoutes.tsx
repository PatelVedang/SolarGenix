import { BrowserRouter, Route, Routes } from "react-router-dom";
import Navbar from "../components/Navbar";
import BillPredictionPage from "../pages/BillPredictionPage";
import DashboardPage from "../pages/DashboardPage";
import HomePage from "../pages/HomePage";
import SolarPredictionPage from "../pages/SolarPredictionPage";

const AppRoutes = () => {
    return (
        <BrowserRouter>
            <Navbar />
            <Routes>
                <Route path="/" element={<HomePage />} />
                <Route path="/dashboard" element={<DashboardPage />} />


                <Route path="/solar-predict" element={<SolarPredictionPage />} />
                <Route path="/bill-predict" element={<BillPredictionPage />} />

            </Routes>
        </BrowserRouter>
    );
};

export default AppRoutes;
