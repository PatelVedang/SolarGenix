import joblib
from pathlib import Path
import pandas as pd
import numpy as np
import math


class BillPredictionService:
    """
    Service responsible for predicting the NEXT bi-monthly electricity bill
    using trained ML models. Routes to different models based on usage scale.

    Design principles:
    - Frontend sends ONLY raw consumption data
    - Backend handles ALL feature engineering
    - Model routing: last_bill_kWh >= 1200 leads to high-usage model
    """

    def __init__(self):
        """
        Load both general and high-usage models at service initialization.
        """
        self.base_dir = Path(__file__).resolve().parent.parent.parent
        self.models_dir = self.base_dir / "models"
        
        self.general_model_path = self.models_dir / "bill_prediction_model.pkl"
        self.high_usage_model_path = self.models_dir / "bill_prediction_high_usage_model.pkl"
        
        self.general_model = self._load_model(self.general_model_path)
        self.high_usage_model = self._load_model(self.high_usage_model_path)

    def _load_model(self, path):
        """
        Safely load a trained model from disk.
        """
        if not path.exists():
            print(f"Model not found at {path}")
            return None

        try:
            return joblib.load(path)
        except Exception as e:
            print(f"Failed to load model {path.name}: {e}")
            return None

    def predict_bill(self, consumption_history, cycle_index):
        """
        Predict the electricity consumption (kWh) for a target bi-monthly cycle.
        Automatically routes between high-consumption and general models.
        """

        try:
            # --------------------------------------------------
            # 1. INPUT VALIDATION
            # --------------------------------------------------

            if consumption_history is None:
                return {"error": "consumption_history is required"}, 400

            if not isinstance(consumption_history, list) or len(consumption_history) != 6:
                return {
                    "error": "consumption_history must be a list of exactly 6 numeric values"
                }, 400

            try:
                consumption_history = [float(v) for v in consumption_history]
            except (ValueError, TypeError):
                return {
                    "error": "All values in consumption_history must be numeric"
                }, 400

            if cycle_index is None:
                return {"error": "cycle_index is required"}, 400

            try:
                cycle_index = int(cycle_index)
                if not (1 <= cycle_index <= 6):
                    raise ValueError
            except ValueError:
                return {
                    "error": "cycle_index must be an integer between 1 and 6"
                }, 400

            # --------------------------------------------------
            # 2. FEATURE ENGINEERING (RELEVANT FOR ROUTING)
            # --------------------------------------------------

            last_bill_kWh = consumption_history[-1]
            target_cycle = cycle_index

            # Calculate basic stats
            avg_last_2_bills_kWh = float(np.mean(consumption_history[-2:]))
            avg_last_3_bills_kWh = float(np.mean(consumption_history[-3:]))

            # --------------------------------------------------
            # 3. MODEL ROUTING LOGIC
            # --------------------------------------------------
            # High-consumption users scale: >= 1200 kWh
            
            if last_bill_kWh >= 1200:
                selected_model = self.high_usage_model
                model_used = "high_consumption"
            else:
                selected_model = self.general_model
                model_used = "general"

            if not selected_model:
                return {"error": f"Selected model ({model_used}) not loaded"}, 500

            # --------------------------------------------------
            # 4. REMAINING FEATURE ENGINEERING
            # --------------------------------------------------

            # Population standard deviation
            std_last_3_bills_kWh = float(np.std(consumption_history[-3:], ddof=0))

            # Linear trend (slope)
            slope_last_3_bills = float(np.polyfit([0, 1, 2], consumption_history[-3:], 1)[0])

            # Seasonal anchors & changes
            same_period_last_year_kWh = avg_last_3_bills_kWh
            
            if avg_last_3_bills_kWh <= 0:
                relative_change_last_bill = 1.0
            else:
                relative_change_last_bill = last_bill_kWh / avg_last_3_bills_kWh

            # Clamp relative change
            relative_change_last_bill = max(0.5, min(2.0, float(relative_change_last_bill)))

            # Cyclical encoding
            cycle_sin = float(math.sin(2 * math.pi * target_cycle / 6))
            cycle_cos = float(math.cos(2 * math.pi * target_cycle / 6))

            # --------------------------------------------------
            # 5. BUILD MODEL INPUT (EXACT FEATURE ORDER)
            # --------------------------------------------------

            X_pred = pd.DataFrame(
                [[
                    last_bill_kWh,
                    avg_last_2_bills_kWh,
                    avg_last_3_bills_kWh,
                    std_last_3_bills_kWh,
                    slope_last_3_bills,
                    same_period_last_year_kWh,
                    relative_change_last_bill,
                    cycle_sin,
                    cycle_cos
                ]],
                columns=[
                    "last_bill_kWh",
                    "avg_last_2_bills_kWh",
                    "avg_last_3_bills_kWh",
                    "std_last_3_bills_kWh",
                    "slope_last_3_bills",
                    "same_period_last_year_kWh",
                    "relative_change_last_bill",
                    "cycle_sin",
                    "cycle_cos"
                ]
            )

            # --------------------------------------------------
            # 6. MODEL PREDICTION
            # --------------------------------------------------

            prediction = selected_model.predict(X_pred)[0]
            predicted_value = round(float(prediction), 2)
            predicted_value = max(0.0, predicted_value)

            # --------------------------------------------------
            # 7. RESPONSE
            # --------------------------------------------------

            return {
                "predicted_next_bill_kWh": predicted_value,
                "predicted_cycle": target_cycle,
                "last_bill_kWh": round(last_bill_kWh, 2),
                "model_used": model_used,
                "features_used": {
                    "avg_last_2_bills_kWh": round(avg_last_2_bills_kWh, 4),
                    "avg_last_3_bills_kWh": round(avg_last_3_bills_kWh, 4),
                    "std_last_3_bills_kWh": round(std_last_3_bills_kWh, 4),
                    "slope_last_3_bills": round(slope_last_3_bills, 4),
                    "relative_change_last_bill": round(relative_change_last_bill, 4),
                    "cycle_sin": round(cycle_sin, 4),
                    "cycle_cos": round(cycle_cos, 4)
                }
            }, 200

        except Exception as e:
            # --------------------------------------------------
            # 8. FAIL-SAFE ERROR HANDLING
            # --------------------------------------------------
            return {
                "error": "Internal Server Error",
                "details": str(e)
            }, 500
