import axios from "axios";

const BASE_URL = "http://127.0.0.1:8000"; // Django server

// 🌞 1️⃣ Solar Generation Prediction
export const predictSolarGeneration = async (params: {
  pincode: string;
  sunlight_time: number;
  panels: number;
  panel_condition: "good" | "average" | "bad";
}) => {
  try {
    const response = await axios.get(
      `${BASE_URL}/solar_generation/predict-production/`,
      {
        params: {
          pincode: params.pincode,
          sunlight_time: params.sunlight_time,
          panels: params.panels,
          panel_condition: params.panel_condition,
        },
      }
    );

    return response.data;
  } catch (error: any) {
    console.error("Solar Prediction Error:", error.response?.data || error.message);
    throw error;
  }
};

// 💡 2️⃣ Electricity Bill Prediction
export const predictElectricityBill = async (params: {
  consumption_history: number[];
  cycle_index: number;
}) => {
  try {
    const response = await axios.get(
      `${BASE_URL}/solar_generation/predict-bill/`,
      {
        params: {
          cycle_index: params.cycle_index,
          consumption_history: params.consumption_history, // send array directly
        },
        paramsSerializer: (params) => {
          const searchParams = new URLSearchParams();
          
          // append each value separately
          params.consumption_history.forEach((val: number) => {
            searchParams.append("consumption_history", val.toString());
          });

          searchParams.append("cycle_index", params.cycle_index.toString());

          return searchParams.toString();
        },
      }
    );

    return response.data;
  } catch (error: any) {
    console.error("Bill Prediction Error:", error.response?.data || error.message);
    throw error;
  }
};