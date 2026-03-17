import os
import pickle
from typing import Dict, Any, Optional

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.model_selection import train_test_split

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATA_CSV_PATH = os.path.join(PROJECT_ROOT, "data", "raw", "gear_sales_data.csv")
MODEL_DIR = os.path.join(PROJECT_ROOT, "data", "models")
MODEL_FILE = os.path.join(MODEL_DIR, "sales_forecast.pkl")


def _load_data() -> pd.DataFrame:
    if not os.path.exists(DATA_CSV_PATH):
        raise FileNotFoundError(f"Sales dataset not found at {DATA_CSV_PATH}")

    df = pd.read_csv(DATA_CSV_PATH)
    if df.empty:
        raise ValueError("Sales dataset is empty")
    return df


def _preprocess(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    if "Date" not in df.columns:
        raise ValueError("Date column is required")

    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df["Month"] = df["Date"].dt.month
    df["Year"] = df["Date"].dt.year

    target_col = None
    for name in ["Quantity_Sold", "Quantity Sold", "quantity_sold", "Quantity"]:
        if name in df.columns:
            target_col = name
            break
    if target_col is None:
        raise ValueError("Quantity_Sold target column is required")

    df["Quantity_Sold"] = pd.to_numeric(df[target_col], errors="coerce")

    # Handle missing values
    df["Gear_Type"] = df.get("Gear_Type", "Unknown").fillna("Unknown")
    df["Region"] = df.get("Region", "Global").fillna("Global")
    df["Customer_Type"] = df.get("Customer_Type", "Retail").fillna("Retail")

    df = df.dropna(subset=["Date", "Month", "Year", "Quantity_Sold"])
    df["Month"] = df["Month"].astype(int)
    df["Year"] = df["Year"].astype(int)

    return df[["Month", "Year", "Gear_Type", "Region", "Customer_Type", "Quantity_Sold"]]


def _prepare_features(df: pd.DataFrame, fit_cols: Optional[list] = None) -> tuple[pd.DataFrame, list]:
    base = df[["Month", "Year", "Gear_Type", "Region", "Customer_Type"]].copy()
    encoded = pd.get_dummies(base, columns=["Gear_Type", "Region", "Customer_Type"], dummy_na=False)
    if fit_cols is not None:
        for col in fit_cols:
            if col not in encoded.columns:
                encoded[col] = 0
    encoded = encoded.reindex(columns=sorted(encoded.columns))
    return encoded, encoded.columns.tolist()


def train_model(test_size: float = 0.2, random_state: int = 42) -> Dict[str, Any]:
    df = _load_data()
    df = _preprocess(df)

    if len(df) < 15:
        raise ValueError("Need at least 15 rows for training")

    X_raw = df[["Month", "Year", "Gear_Type", "Region", "Customer_Type"]]
    y = df["Quantity_Sold"]
    X, feature_columns = _prepare_features(X_raw)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=random_state)
    model = RandomForestRegressor(n_estimators=200, random_state=random_state)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    mae = float(mean_absolute_error(y_test, y_pred))
    rmse = float(np.sqrt(mean_squared_error(y_test, y_pred)))
    avg_sales = float(y.mean())

    os.makedirs(MODEL_DIR, exist_ok=True)
    with open(MODEL_FILE, "wb") as f:
        pickle.dump({
            "model": model,
            "average_sales": avg_sales,
            "features": feature_columns,
            "history": df,
        }, f)

    insights = _generate_insights(df)
    return {
        "status": "trained",
        "rows": len(df),
        "mae": round(mae, 4),
        "rmse": round(rmse, 4),
        "average_sales": round(avg_sales, 2),
        "insights": insights,
    }


def _load_model() -> Dict[str, Any]:
    if not os.path.exists(MODEL_FILE):
        raise FileNotFoundError("Model not trained yet. Run train_model first.")
    with open(MODEL_FILE, "rb") as f:
        saved = pickle.load(f)
    if "model" not in saved or "features" not in saved:
        raise ValueError("Invalid model file")
    return saved


def predict_sales(month: int, year: int, gear_type: str = "Unknown", region: str = "Global", customer_type: str = "Retail") -> Dict[str, Any]:
    month = int(month)
    year = int(year)
    if not (1 <= month <= 12):
        raise ValueError("month must be 1..12")

    saved = _load_model()
    model = saved["model"]
    avg = saved.get("average_sales", 0.0)
    features = saved["features"]

    new_df = pd.DataFrame([{
        "Month": month,
        "Year": year,
        "Gear_Type": gear_type or "Unknown",
        "Region": region or "Global",
        "Customer_Type": customer_type or "Retail",
    }])
    X_new, _ = _prepare_features(new_df)
    for c in features:
        if c not in X_new.columns:
            X_new[c] = 0
    X_new = X_new[features]

    pred = float(model.predict(X_new)[0])
    pred = max(pred, 0.0)
    insight = "High demand expected" if pred > avg else "Low demand expected"
    rec = "Increase production" if pred > avg else "Reduce inventory" if pred < avg else "Maintain stock"

    return {
        "predicted_sales": round(pred, 2),
        "average_sales": round(avg, 2),
        "insight": insight,
        "recommendation": rec,
        "input": {
            "month": month,
            "year": year,
            "gear_type": gear_type,
            "region": region,
            "customer_type": customer_type,
        },
    }


def product_wise_forecast() -> Dict[str, Any]:
    saved = _load_model()
    history = saved.get("history")
    if history is None or history.empty:
        return {"error": "No history available"}

    data = history.groupby("Gear_Type")["Quantity_Sold"].sum().sort_values(ascending=False)
    return {"product_wise": data.to_dict()}


def region_wise_forecast() -> Dict[str, Any]:
    saved = _load_model()
    history = saved.get("history")
    if history is None or history.empty:
        return {"error": "No history available"}
    data = history.groupby("Region")["Quantity_Sold"].sum().sort_values(ascending=False)
    return {"region_wise": data.to_dict()}


def _generate_insights(df: pd.DataFrame) -> Dict[str, Any]:
    best_gear = df.groupby("Gear_Type")["Quantity_Sold"].sum().idxmax()
    latest_year = df["Year"].max()
    previous_year = latest_year - 1
    prev = df[df["Year"] == previous_year]["Quantity_Sold"].sum()
    latest = df[df["Year"] == latest_year]["Quantity_Sold"].sum()
    trend = "growing" if latest > prev else "declining" if latest < prev else "flat"
    return {
        "top_selling_gear_type": str(best_gear),
        "growth_trend": trend,
        "message": "High demand expected" if trend == "growing" else "Low demand expected",
    }


def forecast_insights() -> Dict[str, Any]:
    saved = _load_model()
    history = saved.get("history")
    if history is None:
        return {"error": "No training history"}
    return _generate_insights(history)


def monthly_history() -> Dict[str, Any]:
    saved = _load_model()
    history = saved.get("history")
    if history is None or history.empty:
        return {"error": "No history"}
    monthly = history.groupby(["Year", "Month"])["Quantity_Sold"].sum().reset_index()
    monthly["period"] = monthly.apply(lambda r: f"{int(r['Year'])}-{int(r['Month']):02d}", axis=1)
    monthly = monthly.sort_values(["Year", "Month"])
    return {"monthly_history": monthly[["period", "Quantity_Sold"]].to_dict(orient="records")}


def price_optimization() -> Dict[str, Any]:
    df = _load_data()
    df = df.copy()
    price_col = None
    for p in ["Price", "price", "Unit_Price", "Unit Price"]:
        if p in df.columns:
            price_col = p
            break
    if price_col is None or "Quantity_Sold" not in df.columns and "Quantity" not in df.columns:
        return {"error": "Need Price and Quantity data columns in CSV"}
    qty_col = "Quantity_Sold" if "Quantity_Sold" in df.columns else "Quantity" if "Quantity" in df.columns else "Quantity_Sold"
    df = df[[price_col, qty_col]].dropna()
    if df.empty:
        return {"error": "No valid price/quantity data"}

    X = df[[price_col]].astype(float)
    y = df[qty_col].astype(float)
    if len(X) < 5:
        return {"error": "Insufficient data for price optimization"}

    # linear fit for price-demand relationship
    a, b = np.polyfit(X[price_col], y, 1)
    predicted_current = (a * X[price_col] + b).mean()
    price_drop = 0.95
    predicted_dropped = (a * (X[price_col] * price_drop) + b).mean()
    demand_change_pct = ((predicted_dropped - predicted_current) / predicted_current) * 100 if predicted_current != 0 else 0

    # approximate revenue optimization using simple grid search
    min_price, max_price = X[price_col].min(), X[price_col].max()
    prices = np.linspace(min_price, max_price, 50)
    revenues = prices * (a * prices + b)
    best_idx = int(np.nanargmax(revenues))
    best_price = float(prices[best_idx])
    best_demand = float(a * best_price + b)

    return {
        "price_coefficient": round(float(a), 6),
        "intercept": round(float(b), 2),
        "current_average_demand": round(float(predicted_current), 2),
        "demand_with_5pct_price_drop": round(float(predicted_dropped), 2),
        "demand_change_pct": round(float(demand_change_pct), 2),
        "optimal_price_revenue": round(float(best_price), 2),
        "optimal_quantity_at_optimal_price": round(float(best_demand), 2),
        "message": f"If price reduced by 5%, demand changes by {demand_change_pct:.2f}%"
    }


def demand_segmentation() -> Dict[str, Any]:
    df = _load_data()
    df = _preprocess(df)

    # OEM vs Retail customer behavior
    if "Customer_Type" not in df.columns:
        return {"error": "Customer_Type column required for segmentation"}

    cust_group = df.groupby(["Customer_Type", "Gear_Type"])["Quantity_Sold"].sum().reset_index()
    top_by_customer = cust_group.loc[cust_group.groupby("Customer_Type")["Quantity_Sold"].idxmax()]
    messages = []
    for _, row in top_by_customer.iterrows():
        messages.append(f"{row['Customer_Type']} customers prefer {row['Gear_Type']} gears")

    # high-value vs low-value by monthly quantity average
    customer_qty = df.groupby("Customer_Type")["Quantity_Sold"].sum().reset_index()
    high_low = []
    high = customer_qty[customer_qty["Quantity_Sold"] >= customer_qty["Quantity_Sold"].mean()]
    low = customer_qty[customer_qty["Quantity_Sold"] < customer_qty["Quantity_Sold"].mean()]
    if not high.empty:
        high_names = ", ".join(high["Customer_Type"].tolist())
        high_low.append(f"High-demand segments: {high_names}")
    if not low.empty:
        low_names = ", ".join(low["Customer_Type"].tolist())
        high_low.append(f"Low-demand segments: {low_names}")

    return {
        "customer_behavior": messages,
        "segment_summary": high_low,
        "top_segments": top_by_customer.to_dict(orient="records"),
    }


def detect_anomalies() -> Dict[str, Any]:
    saved = _load_model()
    history = saved.get("history")
    if history is None or history.empty:
        return {"error": "No history"}
    monthly = history.groupby(["Year", "Month"])["Quantity_Sold"].sum().reset_index()
    mu = monthly["Quantity_Sold"].mean()
    sigma = monthly["Quantity_Sold"].std(ddof=0)
    threshold = sigma * 2
    anomalies = monthly[np.abs(monthly["Quantity_Sold"] - mu) > threshold]
    results = []
    for _, row in anomalies.iterrows():
        results.append({
            "year": int(row["Year"]),
            "month": int(row["Month"]),
            "value": float(row["Quantity_Sold"]),
            "reason": "spike/drop",
        })
    return {"baseline_mean": round(float(mu), 2), "baseline_std": round(float(sigma), 2), "threshold": round(float(threshold), 2), "anomalies": results}
