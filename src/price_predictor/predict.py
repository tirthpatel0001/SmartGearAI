import pandas as pd
import joblib
import os

# -----------------------------
# Load model
# -----------------------------
project_root = r"C:\Projects\SGMAS"
model_path = os.path.join(project_root, 'data', 'models', 'gear_price_model.pkl')

if not os.path.exists(model_path):
    raise FileNotFoundError(f"Trained model not found at {model_path}. Please run train_model.py first.")

model = joblib.load(model_path)

# -----------------------------
# Example customer input
# -----------------------------
customer_input = {
    'Gear_Type': ['Helical'],
    'Material': ['Alloy Steel'],
    'Diameter_mm': [120],
    'Teeth_Count': [60],
    'Thickness_mm': [20],
    'Quantity': [150],
    'Special_Requirement': ['Hardening'],
    'Weight_kg': [12]  # approximate weight
}

df_input = pd.DataFrame(customer_input)

# -----------------------------
# Predict price
# -----------------------------
predicted_price = model.predict(df_input)[0]
print(f"Predicted Price for the given gear: ₹{predicted_price:.2f}")
