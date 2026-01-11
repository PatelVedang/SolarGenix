import joblib
from pathlib import Path
import sys
import numpy as np
import pandas as pd
import math

# Simulate the same path logic as the service
BASE_DIR = Path(__file__).resolve().parent.parent
models_dir = BASE_DIR / "models"
gen_path = models_dir / "bill_prediction_model.pkl"
high_path = models_dir / "bill_prediction_high_usage_model.pkl"

def test_routing(consumption_history, cycle_index):
    last_bill = consumption_history[-1]
    if last_bill >= 1200:
        path = high_path
        model_name = "high_consumption"
    else:
        path = gen_path
        model_name = "general"
    
    print(f"\n--- Testing for last_bill={last_bill} (Expected: {model_name}) ---")
    
    if not path.exists():
        print(f"ERROR: Model file missing at {path}")
        return

    try:
        model = joblib.load(path)
        print(f"SUCCESS: {model_name} model loaded.")
        
        # Features calculation
        avg2 = np.mean(consumption_history[-2:])
        avg3 = np.mean(consumption_history[-3:])
        std3 = np.std(consumption_history[-3:], ddof=0)
        slope = np.polyfit([0, 1, 2], consumption_history[-3:], 1)[0]
        rel_change = max(0.5, min(2.0, last_bill / avg3 if avg3 > 0 else 1.0))
        sin = math.sin(2 * math.pi * cycle_index / 6)
        cos = math.cos(2 * math.pi * cycle_index / 6)
        
        X_pred = pd.DataFrame([[
            last_bill, avg2, avg3, std3, slope, avg3, rel_change, sin, cos
        ]], columns=[
            "last_bill_kWh", "avg_last_2_bills_kWh", "avg_last_3_bills_kWh",
            "std_last_3_bills_kWh", "slope_last_3_bills", "same_period_last_year_kWh",
            "relative_change_last_bill", "cycle_sin", "cycle_cos"
        ])
        
        prediction = model.predict(X_pred)[0]
        print(f"Model: {model_name}")
        print(f"Prediction: {prediction}")
    except Exception as e:
        print(f"ERROR: {e}")

# Case 1: General (Below 1200)
test_routing([200, 250, 180, 220, 240, 210], 1)

# Case 2: High Consumption (Above 1200)
test_routing([1100, 1150, 1180, 1220, 1250, 1300], 1)

print("\nVerification complete.")
