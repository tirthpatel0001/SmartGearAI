import pandas as pd
import joblib
import os
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor

# Paths
project_root = r"C:\Projects\SGMAS"
data_path = os.path.join(project_root, "data", "raw", "gear_price_data.csv")
model_path = os.path.join(project_root, "data", "models")
os.makedirs(model_path, exist_ok=True)
model_file = os.path.join(model_path, "gear_price_model.pkl")

# Load dataset
df = pd.read_csv(data_path)

# Features and target
X = df.drop("Total_Price", axis=1)
y = df["Total_Price"]

# One-hot encoding for categorical features
categorical_features = ["Gear_Type", "Material", "Special_Requirement"]
numerical_features = [col for col in X.columns if col not in categorical_features]

preprocessor = ColumnTransformer(
    transformers=[
        ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_features)
    ],
    remainder="passthrough"
)

# Model pipeline
pipeline = Pipeline([
    ("preprocessor", preprocessor),
    ("regressor", RandomForestRegressor(n_estimators=200, random_state=42))
])

# Split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train
pipeline.fit(X_train, y_train)

# Evaluate
y_pred = pipeline.predict(X_test)
rmse = ((y_test - y_pred)**2).mean() ** 0.5
print(f"Price Prediction RMSE: {rmse:.2f}")

# Save model
joblib.dump(pipeline, model_file)
print(f"Model saved at:\n{model_file}")
