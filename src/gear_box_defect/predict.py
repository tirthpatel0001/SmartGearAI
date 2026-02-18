import os
import joblib
import numpy as np
from .data_loader import load_csv
from .preprocessing import transform_signal_with_scaler
from .dataset_builder import extract_features
from .recommendation import calculate_severity, maintenance_recommendation

# new utilities and result container
from . import maintenance_utils
from .predictive_maintenance import (
    predict_failure_risk,
    remaining_useful_life,
    health_score,
    maintenance_scheduler,
    failure_trend,
    enhanced_recommendation,
)
from .result import GearboxAnalysis


BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "gearbox_model.pkl")

def predict_fault_and_severity(csv_path):
    saved = joblib.load(MODEL_PATH)
    model = saved["model"]
    encoder = saved["encoder"]
    scaler = saved["scaler"]

    df = load_csv(csv_path)

    features = []
    raw_signals = []

    for col in df.columns:
        raw_signal = df[col].dropna().values
        raw_signals.append(raw_signal)

        signal = transform_signal_with_scaler(df[col], scaler)
        features.extend(extract_features(signal))

    features = np.array(features).reshape(1, -1)
    pred = model.predict(features)[0]
    fault = encoder.inverse_transform([pred])[0]

    severity, rms, energy = calculate_severity(raw_signals)
    recommendation_base = maintenance_recommendation(fault, severity)

    # --- predictive maintenance calculations ---
    risk_label, risk_prob = predict_failure_risk(severity)
    rul = remaining_useful_life(risk_prob)
    health = health_score(risk_prob)
    schedule = maintenance_scheduler(rul)
    trend = failure_trend([risk_prob])

    # update recommendation with risk awareness
    recommendation = enhanced_recommendation(fault, severity, risk_label)

    # ---------- new features ----------
    cost = maintenance_utils.predict_failure_cost(risk_prob)
    parts = maintenance_utils.spare_parts_recommendation(fault)
    root_cause = maintenance_utils.root_cause_analysis(fault, severity)
    chatbot_intro = maintenance_utils.chatbot_response(risk_label)
    digital_summary = maintenance_utils.digital_twin_simulation(risk_prob)

    # compose results dataclass
    result = GearboxAnalysis(
        fault=fault,
        severity=severity,
        rms=rms,
        energy=energy,
        recommendation=recommendation,
        risk_label=risk_label,
        risk_probability=risk_prob,
        remaining_life=rul,
        schedule=schedule,
        health_score=health,
        trend=trend,
        failure_cost=cost,
        spare_parts=parts,
        root_cause=root_cause,
        chatbot_intro=chatbot_intro,
        digital_twin_summary=digital_summary,
    )

    return result


if __name__ == "__main__":
    test_file = r"C:\Users\TIRTH PATEL\OneDrive\Desktop\tirth.csv"
    result = predict_fault_and_severity(test_file)
    print(result)
