from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import requests
import pandas as pd
import joblib
from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parent.parent
model_path = BASE_DIR / "models" / "solar_generation_model.pkl"

if not model_path.exists():
    print(f"Model not found at {model_path}")

try:
    gb_model = joblib.load(model_path)
except Exception as e:
    print(f"Failed to load model: {e}")
    gb_model = None


class SolarGenerationPrediction(APIView):

    def get(self, request):

        pincode = request.GET.get("pincode")
        sunlight_time = request.GET.get("sunlight_time")      # hours
        panels = request.GET.get("panels")
        panel_condition = request.GET.get("panel_condition")  # good / average / bad

        if not pincode:
            return Response(
                {"error": "pincode is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if sunlight_time is None:
            sunlight_time_hours = 8
        else:
            try:
                sunlight_time_hours = float(sunlight_time)
            except ValueError:
                return Response(
                    {"error": "sunlight_time must be a number (hours)"},
                    status=status.HTTP_400_BAD_REQUEST
                )

        sunlight_time_seconds = sunlight_time_hours * 3600

        if panels is None:
            number_of_panels = 1
        else:
            try:
                number_of_panels = int(panels)
                if number_of_panels <= 0:
                    raise ValueError
            except ValueError:
                return Response(
                    {"error": "panels must be a positive integer"},
                    status=status.HTTP_400_BAD_REQUEST
                )

        PANEL_EFFICIENCY_MAP = {
            "good": 0.20,
            "average": 0.17,
            "bad": 0.14
        }

        if panel_condition is None:
            panel_condition = "average"

        panel_condition = panel_condition.lower()

        if panel_condition not in PANEL_EFFICIENCY_MAP:
            return Response(
                {
                    "error": "panel_condition must be one of: good, average, bad"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        panel_efficiency = PANEL_EFFICIENCY_MAP[panel_condition]

        geo_url = "https://nominatim.openstreetmap.org/search"
        geo_params = {
            "postalcode": pincode,
            "country": "India",
            "format": "json"
        }

        headers = {
            "User-Agent": "SolarPredictionAPI/1.0"
        }

        geo_data = requests.get(
            geo_url,
            params=geo_params,
            headers=headers
        ).json()

        if not geo_data:
            return Response(
                {"error": "Invalid pincode"},
                status=status.HTTP_404_NOT_FOUND
            )

        latitude = float(geo_data[0]["lat"])
        longitude = float(geo_data[0]["lon"])

        weather_url = "https://api.open-meteo.com/v1/forecast"
        weather_params = {
            "latitude": latitude,
            "longitude": longitude,
            "daily": "shortwave_radiation_sum,sunshine_duration,temperature_2m_mean",
            "forecast_days": 10,
            "timezone": "auto"
        }

        weather = requests.get(weather_url, params=weather_params).json()
        daily = weather.get("daily")

        if not daily:
            return Response(
                {"error": "Weather data unavailable"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

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

        df["predicted_energy_kWh"] = gb_model.predict(X_pred)
        total_energy = float(df["predicted_energy_kWh"].sum())
        return Response(
            {
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
                        "predicted_energy_kWh": round(float(row["predicted_energy_kWh"]), 3)
                    }
                    for _, row in df.iterrows()
                ]
            },
            status=status.HTTP_200_OK
        )

