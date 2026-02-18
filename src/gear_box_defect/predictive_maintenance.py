import numpy as np


def risk_category(probability: float) -> str:
    """Convert a failure probability (0..1) to a human-readable category."""
    if probability < 0.3:
        return "Low Risk"
    elif probability < 0.7:
        return "Medium Risk"
    else:
        return "High Risk"


def predict_failure_risk(severity: str) -> tuple[str, float]:
    """Estimate the probability of a gearbox failure based on current severity.

    This is a placeholder heuristic that maps the discrete severity level
    into a probability. A real implementation would use a time‑series model or
    a trained regression network using historical data.

    Returns
    -------
    risk_label : str
        One of "Low Risk", "Medium Risk", "High Risk".
    probability : float
        Numeric probability between 0 and 1.
    """
    sev = (severity or "").strip().upper()
    mapping = {
        "LOW": 0.20,
        "MODERATE": 0.50,
        "SEVERE": 0.85,
    }
    prob = mapping.get(sev, 0.50)
    return risk_category(prob), prob


def remaining_useful_life(failure_prob: float, base_hours: int = 500) -> float:
    """Compute a rudimentary remaining useful life (RUL) estimate.

    The formula used here is simply `(1 - prob) * base_hours`.  Replace with a
    data-driven regression if you have historical failure records.
    """
    return max(0.0, (1.0 - failure_prob) * base_hours)


def health_score(failure_prob: float) -> float:
    """Give an overall health percentage derived from the failure risk."""
    return max(0.0, min(100.0, (1.0 - failure_prob) * 100.0))


def maintenance_scheduler(rul_hours: float) -> str:
    """Generate human‑readable advice about when maintenance should occur."""
    if rul_hours > 72:
        return f"Routine check in approximately {int(rul_hours)} hours."
    elif rul_hours > 24:
        return f"Schedule maintenance within {int(rul_hours)} hours."
    elif rul_hours > 0:
        return f"Perform maintenance immediately ({int(rul_hours)} hours remaining)!"
    else:
        return "Failure imminent – shut down and repair immediately."


def failure_trend(history: list[float] | None = None, periods: int = 10) -> list[float]:
    """Generate a simple future failure‑probability trend curve.

    In a real system this could be produced by a time‑series forecasting model
    such as ARIMA/Prophet or an RNN.  Here we just extrapolate linearly from the
    last known probability.
    """
    if history is None or len(history) == 0:
        history = [0.0]
    last = history[-1]
    step = 0.05
    trend = []
    for i in range(1, periods + 1):
        trend.append(min(1.0, last + step * i))
    return trend


def enhanced_recommendation(fault: str, severity: str, risk_label: str) -> str:
    """Combine diagnosis and risk information to give a more actionable suggestion."""
    base = maintenance_recommendation(fault, severity)
    if "High" in risk_label:
        return base + " 🔥 Risk is high; expedite maintenance."
    elif "Medium" in risk_label:
        return base + " ⚠ Medium risk – monitor closely."
    else:
        return base + " ✅ Low risk, normal procedures."  # type: ignore


# import from same package after function definitions to avoid circular import
from .recommendation import maintenance_recommendation
