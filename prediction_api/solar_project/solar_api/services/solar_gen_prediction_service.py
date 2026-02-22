import pandas as pd
import joblib
from pathlib import Path
import requests

class SolarPredictionService:
    def __init__(self):
        self.base_dir = Path(__file__).resolve().parent.parent.parent
        self.model_path = self.base_dir / "models" / "solar_generation_model.pkl"
        self.model = self._load_model()
        self.panel_efficiency_map = {
            "good": 0.20,
            "average": 0.17,
            "bad": 0.14
        }
    def _load_model(self):
        if not self.model_path.exists():
            print(f"Model not found at {self.model_path}")
            return None
        try:
            return joblib.load(self.model_path)
        except Exception as e:
            print(f"Failed to load model: {e}")
            return None

    def predict_generation(self, pincode, sunlight_time, panels, panel_condition):
        if not pincode:
            return {"error": "pincode is required"}, 400

        if sunlight_time is None:
            sunlight_time_hours = 8
        else:
            try:
                sunlight_time_hours = float(sunlight_time)
            except ValueError:
                return {"error": "sunlight_time must be a number (hours)"}, 400

        sunlight_time_seconds = sunlight_time_hours * 3600

        if panels is None:
            number_of_panels = 1
        else:
            try:
                number_of_panels = int(panels)
                if number_of_panels <= 0:
                    raise ValueError
            except ValueError:
                return {"error": "panels must be a positive integer"}, 400

        if panel_condition is None:
            panel_condition = "average"
        
        panel_condition = panel_condition.lower()
        if panel_condition not in self.panel_efficiency_map:
            return {"error": "panel_condition must be one of: good, average, bad"}, 400
            
        panel_efficiency = self.panel_efficiency_map[panel_condition]

        # Geo API
        geo_url = "https://nominatim.openstreetmap.org/search"
        geo_params = {
            "postalcode": pincode,
            "country": "India",
            "format": "json"
        }
        headers = {"User-Agent": "SolarPredictionAPI/1.0"}

        try:
            geo_response = requests.get(geo_url, params=geo_params, headers=headers)
            geo_data = geo_response.json()
        except Exception:
             return {"error": "External Geo API failed"}, 500

        if not geo_data:
            return {"error": "Invalid pincode"}, 404

        latitude = float(geo_data[0]["lat"])
        longitude = float(geo_data[0]["lon"])

        # Weather API
        weather_url = "https://api.open-meteo.com/v1/forecast"
        weather_params = {
            "latitude": latitude,
            "longitude": longitude,
            "daily": "shortwave_radiation_sum,sunshine_duration,temperature_2m_mean",
            "forecast_days": 10,
            "timezone": "auto"
        }

        try:
            weather = requests.get(weather_url, params=weather_params).json()
        except Exception:
            return {"error": "External Weather API failed"}, 500

        daily = weather.get("daily")
        if not daily:
            return {"error": "Weather data unavailable"}, 500

        df = pd.DataFrame({
            "date": daily["time"],
            "shortwave_radiation_sum": daily["shortwave_radiation_sum"],
            "ambient_temperature": daily["temperature_2m_mean"]
        })

        df["sunshine_duration"] = sunlight_time_seconds
        sunshine_ratio = (df["sunshine_duration"] / 45000).clip(0, 1)

        df["effective_radiation"] = (
            df["shortwave_radiation_sum"] *
            (0.6 + 0.4 * sunshine_ratio)
        )

        X_pred = pd.DataFrame({
            "effective_radiation": df["effective_radiation"],
            "ambient_temperature": df["ambient_temperature"],
            "number_of_panels": number_of_panels,
            "panel_efficiency": panel_efficiency
        })

        if self.model:
            df["predicted_energy_kWh"] = self.model.predict(X_pred)
        else:
            return {"error": "Model not loaded"}, 500

        total_energy = float(df["predicted_energy_kWh"].sum())

        result = {
            "pincode": pincode,
            "latitude": latitude,
            "longitude": longitude,
            "number_of_panels": number_of_panels,
            "panel_condition": panel_condition,
            "panel_efficiency": panel_efficiency,
            "sunlight_time_hours": sunlight_time_hours,
            "total_energy_10_days_kWh": round(total_energy, 3),
            "daily_predictions": [
                {
                    "date": row["date"],
                    "predicted_energy_kWh": round(float(row["predicted_energy_kWh"]), 3),
                    "ambient_temperature": row["ambient_temperature"],
                    "shortwave_radiation_sum": row["shortwave_radiation_sum"],
                    "effective_radiation": round(float(row["effective_radiation"]), 3)
                }
                for _, row in df.iterrows()
            ],
            "weather_api_response": weather
        }
        
        return result, 200
