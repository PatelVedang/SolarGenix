# Solar Prediction API

REST API for two services:
- Solar generation forecast for the next 10 days based on location, sunlight hours, and panel condition.
- Electricity bill prediction for the next bi-monthly cycle using past six bills.

## Stack
- Django + Django REST Framework
- scikit-learn models loaded from `models/`
- External data: OpenStreetMap Nominatim (geocoding), Open-Meteo (weather)

## Quickstart
1. Create and activate a virtual environment.
2. Install dependencies: `pip install -r requirements.txt`.
3. Run the server: `python manage.py runserver` (default http://127.0.0.1:8000).
4. API base path: `/solar_generation/`.

## API Reference

### 1) Predict Solar Generation
- **Method:** GET
- **Path:** `/solar_generation/predict-production/`
- **Query parameters:**
  - `pincode` (string, required): Indian postal code used for geocoding.
  - `sunlight_time` (number, optional, hours, default 8): Daily sunlight hours you expect on-site.
  - `panels` (integer, optional, default 1): Number of panels.
  - `panel_condition` (string, optional, default `average`): One of `good`, `average`, `bad`.
- **Behavior:**
  - Looks up latitude/longitude via Nominatim using `pincode`.
  - Pulls 10-day forecast from Open-Meteo.
  - Derives effective radiation, applies trained model (`models/solar_generation_model.pkl`), and sums kWh.
- **Example:**
  ```bash
  curl "http://127.0.0.1:8000/solar_generation/predict-production/?pincode=560001&sunlight_time=7.5&panels=4&panel_condition=good"
  ```
- **Success (200) payload (trimmed):**
  ```json
  {
    "pincode": "560001",
    "latitude": 12.97,
    "longitude": 77.59,
    "number_of_panels": 4,
    "panel_condition": "good",
    "panel_efficiency": 0.2,
    "sunlight_time_hours": 7.5,
    "total_energy_10_days_kWh": 123.456,
    "daily_predictions": [
      {
        "date": "2026-01-18",
        "predicted_energy_kWh": 12.345,
        "ambient_temperature": 28.1,
        "shortwave_radiation_sum": 5.6,
        "effective_radiation": 4.321
      }
      // ...9 more days
    ],
    "weather_api_response": { /* raw Open-Meteo response */ }
  }
  ```
- **Errors:**
  - `400` when required/invalid params (e.g., missing `pincode`, bad `sunlight_time`).
  - `404` when `pincode` not found.
  - `500` when model not loaded or external APIs fail.

### 2) Predict Electricity Bill
- **Method:** GET
- **Path:** `/solar_generation/predict-bill/`
- **Query parameters:**
  - `consumption_history` (list, required): Exactly 6 numeric values (kWh) passed as repeated query keys.
    - Example: `?consumption_history=100&consumption_history=120&consumption_history=140&consumption_history=160&consumption_history=180&consumption_history=200`
  - `cycle_index` (integer, required): Target bi-monthly cycle, 1 through 6.
- **Behavior:**
  - Validates input, computes features (averages, std dev, slope, seasonal encodings).
  - Routes to high-usage model (`bill_prediction_high_usage_model.pkl`) if last bill >= 1200 kWh; otherwise uses general model (`bill_prediction_model.pkl`).
- **Example:**
  ```bash
  curl "http://127.0.0.1:8000/solar_generation/predict-bill/?consumption_history=100&consumption_history=120&consumption_history=140&consumption_history=160&consumption_history=180&consumption_history=200&cycle_index=3"
  ```
- **Success (200) payload:**
  ```json
  {
    "predicted_next_bill_kWh": 210.5,
    "predicted_cycle": 3,
    "last_bill_kWh": 200.0,
    "model_used": "general",
    "features_used": {
      "avg_last_2_bills_kWh": 190.0,
      "avg_last_3_bills_kWh": 180.0,
      "std_last_3_bills_kWh": 20.0,
      "slope_last_3_bills": 20.0,
      "relative_change_last_bill": 1.11,
      "cycle_sin": 0.866,
      "cycle_cos": -0.5
    }
  }
  ```
- **Errors:**
  - `400` when params are missing/invalid (must be 6 numbers; `cycle_index` 1-6).
  - `500` when the selected model is not loaded.

## Docs and Testing
- Swagger UI: `/swagger/`
- ReDoc: `/redoc/`

## Notes
- All endpoints are GET for now.
- External calls require internet access; failures return a `500` error.
- Models must exist in `models/` relative to project root.
