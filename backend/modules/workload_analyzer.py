import os
import traceback
from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, accuracy_score
import joblib

BASE_DIR = Path("C:/Projects/SGMAS")
MODEL_DIR = BASE_DIR / "models"
MODEL_DIR.mkdir(parents=True, exist_ok=True)
LEAD_MODEL_PATH = MODEL_DIR / "workload_lead_time.pkl"
RISK_MODEL_PATH = MODEL_DIR / "workload_risk.pkl"

# Model containers
_lead_model = None
_risk_model = None


def _load_gears_data():
    # Prefer gear_custom_data_4500.xlsx; fallback to CSV if available.
    file_xlsx = BASE_DIR / "data" / "raw" / "gear_custom_data_4500.xlsx"
    file_csv = BASE_DIR / "data" / "raw" / "gear_custom_data.csv"
    if file_xlsx.exists():
        df = pd.read_excel(file_xlsx)
    elif file_csv.exists():
        df = pd.read_csv(file_csv)
    else:
        raise FileNotFoundError("Gear custom dataset not found under data/raw.")
    return df


def _load_ai4i_data():
    file_csv = BASE_DIR / "data" / "raw" / "ai4i2020.csv"
    if not file_csv.exists():
        file_csv = BASE_DIR / "data" / "raw" / "ai4i_machine_data.csv"
    if not file_csv.exists():
        raise FileNotFoundError("AI4I dataset not found under data/raw.")
    return pd.read_csv(file_csv)


def _train_lead_time_model():
    df = _load_gears_data()
    # required columns: Teeth, Diameter, Process_Steps, Lead_Time
    for col in ["Teeth", "Diameter", "Process_Steps", "Lead_Time"]:
        if col not in df.columns:
            raise ValueError(f"Missing {col} in gear dataset")
    clean = df[["Teeth", "Diameter", "Process_Steps", "Lead_Time"]].dropna()
    clean["complexity_score"] = clean["Teeth"] * clean["Process_Steps"]
    clean["size_factor"] = clean["Diameter"] / clean["Teeth"].replace(0, np.nan)
    clean = clean.replace([np.inf, -np.inf], np.nan).dropna()

    X = clean[["Teeth", "Diameter", "Process_Steps", "complexity_score", "size_factor"]]
    y = clean["Lead_Time"]
    if len(X) < 10:
        raise ValueError("Not enough rows to train workload lead-time model.")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    score = r2_score(y_test, y_pred)
    joblib.dump(model, LEAD_MODEL_PATH)
    return model, score


def _train_risk_model():
    df = _load_ai4i_data()
    # required columns for risk label: Machine failure or Machine Failure or Drive Failure
    target_col = None
    for c in ["Machine failure", "machine_failure", "Machine Failure", "failure"]:
        if c in df.columns:
            target_col = c
            break
    if target_col is None:
        raise ValueError("No target machine failure column found in AI4I data")

    features = []
    for c in ["Rotational speed [rpm]", "Torque [Nm]", "Tool wear [min]", "Air temperature [K]", "Process temperature [K]"]:
        if c in df.columns:
            features.append(c)
    if len(features) < 3:
        raise ValueError("Insufficient numeric features in AI4I data for risk training")
    clean = df[features + [target_col]].dropna()
    clean[target_col] = clean[target_col].astype(int)

    X = clean[features]
    y = clean[target_col]
    if len(X) < 50:
        raise ValueError("Not enough AI4I rows to train risk model")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X_train, y_train)
    y_pred = clf.predict(X_test)
    score = accuracy_score(y_test, y_pred)
    joblib.dump(clf, RISK_MODEL_PATH)
    return clf, score


def _load_model_or_train():
    global _lead_model, _risk_model
    # Ensure directory exists
    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    if LEAD_MODEL_PATH.exists():
        try:
            _lead_model = joblib.load(LEAD_MODEL_PATH)
        except Exception:
            _lead_model, _ = _train_lead_time_model()
    else:
        _lead_model, _ = _train_lead_time_model()

    if RISK_MODEL_PATH.exists():
        try:
            _risk_model = joblib.load(RISK_MODEL_PATH)
        except Exception:
            _risk_model, _ = _train_risk_model()
    else:
        _risk_model, _ = _train_risk_model()


def initialize_models():
    try:
        _load_model_or_train()
    except Exception:
        traceback.print_exc()
        # fallback: attempt to retrain if model loading fails
        _lead_model, _ = _train_lead_time_model()
        _risk_model, _ = _train_risk_model()


def predict_lead_time(teeth: float, diameter: float, process_steps: float):
    global _lead_model
    if _lead_model is None:
        initialize_models()
    features = np.array([[teeth, diameter, process_steps, teeth * process_steps, diameter / (teeth or 1)]])
    pred = float(_lead_model.predict(features)[0])
    return max(pred, 0.0)


def predict_machine_risk(air_temp: float, process_temp: float, speed: float, torque: float, tool_wear: float):
    global _risk_model
    if _risk_model is None:
        initialize_models()
    features = np.array([[air_temp, process_temp, speed, torque, tool_wear]])
    risk_prob = float(_risk_model.predict_proba(features)[0][1]) if hasattr(_risk_model, 'predict_proba') else float(_risk_model.predict(features)[0])
    return "high" if risk_prob >= 0.4 else "normal"


def _gear_type_factor(gear_type: str):
    gt = str(gear_type or "").strip().lower()
    if gt == "helical":
        return 1.15
    if gt == "bevel":
        return 1.25
    return 1.0


def _machine_requirement(teeth: float, process_steps: float):
    complexity = max(1.0, teeth * process_steps / 50.0)
    count = int(np.ceil(complexity / 2.0))
    return max(1, count)


def _workload_status(current_jobs: float, machine_capacity: float):
    if machine_capacity <= 0:
        return "unknown"
    ratio = current_jobs / machine_capacity
    if ratio > 1.0:
        return "overloaded"
    if ratio >= 0.75:
        return "normal"
    return "underutilized"


def predict_workload(payload: dict):
    # required workload inputs
    gear_type = payload.get("gear_type", "spur")
    teeth = float(payload.get("teeth", 0))
    diameter = float(payload.get("diameter", 0))
    process_steps = float(payload.get("process_steps", 0))
    machine_count = int(payload.get("machine_count", 1))
    current_jobs = float(payload.get("current_jobs", 1))
    machine_capacity = float(payload.get("machine_capacity", 5))
    progress = float(payload.get("progress", 0.0))

    # optional machine risk sensor values
    air_temp = float(payload.get("air_temperature", 298.0))
    process_temp = float(payload.get("process_temperature", 308.0))
    speed = float(payload.get("rotational_speed", 1500.0))
    torque = float(payload.get("torque", 50.0))
    tool_wear = float(payload.get("tool_wear", 5.0))

    lead_time = predict_lead_time(teeth, diameter, process_steps)
    gear_factor = _gear_type_factor(gear_type)
    lead_time *= gear_factor

    machine_risk = predict_machine_risk(air_temp, process_temp, speed, torque, tool_wear)
    if machine_risk == "high" or tool_wear > 8:
        lead_time = lead_time * 1.20

    machine_needed = _machine_requirement(teeth, process_steps)
    machine_needed = max(machine_needed, 1)

    if progress > 0 and progress <= 100:
        remaining_time = lead_time * (1 - progress / 100.0)
    else:
        remaining_time = lead_time

    status = _workload_status(current_jobs, machine_capacity)

    # Setup human friendly messages
    msg = {
        "lead_time_text": f"This gearbox will take {lead_time:.1f} hours",
        "machine_requirement_text": f"You need {machine_needed} machines",
        "workload_status": status,
        "remaining_time_text": f"{remaining_time:.1f} hours remaining",
        "machine_risk": machine_risk,
    }

    return {
        "lead_time": round(lead_time, 2),
        "machine_needed": machine_needed,
        "workload_status": status,
        "remaining_time": round(remaining_time, 2),
        "machine_risk": machine_risk,
        "messages": msg,
    }


# initialize at import time to satisfy the startup auto training requirement
try:
    initialize_models()
except Exception:
    pass
