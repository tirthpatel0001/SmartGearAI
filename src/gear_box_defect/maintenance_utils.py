import random


def predict_failure_cost(risk_prob: float, base_cost: float = 1000.0) -> float:
    """Estimate a rough cost of failure based on risk probability."""
    # simple linear scaling; could be replaced by logistic regression with real data
    return round(base_cost * risk_prob * (1 + random.uniform(-0.1, 0.1)), 2)


def spare_parts_recommendation(fault: str) -> list[str]:
    """Return a list of suggested spare parts given a fault type."""
    suggestions = {
        "gear_wear": ["Replacement gear set", "Lubricant"],
        "gear_pitting": ["Surface-treated gears", "Inspection kit"],
        "miss_teeth": ["Complete gearbox assembly", "Fasteners"],
        "teeth_break": ["High-strength gears", "Support bearings"],
        "teeth_crack": ["Reinforced gear", "Crack monitoring sensor"],
        "compound_fault": ["Inspection tools", "Full gearbox kit"],
        "healthy": []
    }
    return suggestions.get(fault.lower(), ["Consult parts catalogue"])


def root_cause_analysis(fault: str, severity: str) -> str:
    """Provide a short explanation of possible root causes."""
    mapping = {
        "gear_wear": "Likely due to inadequate lubrication or prolonged operation under load.",
        "gear_pitting": "Surface fatigue from micro-cracking, often caused by contamination or shock loads.",
        "miss_teeth": "Mechanical impact or poor manufacturing leading to missing teeth.",
        "teeth_break": "Overloading or material defect resulting in broken teeth.",
        "teeth_crack": "Progressive stress cycles creating cracks in the gear tooth.",
        "compound_fault": "Combination of wear, overload, or misalignment issues.",
        "healthy": "No faults detected; root cause analysis not required."
    }
    return mapping.get(fault.lower(), "Fault cause unclear; further analysis needed.")


def chatbot_response(risk_label: str) -> str:
    """Return a simple chatbot-style explanation about the risk label."""
    if "High" in risk_label:
        return (
            "⚠ The failure risk is high. Your gearbox is likely to fail soon. "
            "Consider immediately scheduling maintenance or replacement."
        )
    elif "Medium" in risk_label:
        return (
            "🔍 The risk is moderate. Monitor the system closely and plan maintenance "
            "within the next few days."
        )
    else:
        return (
            "✅ Low risk detected. The gearbox appears healthy for the near future. "
            "Continue with normal inspection cycles."
        )


def digital_twin_simulation(risk_prob: float) -> str:
    """Provide a placeholder description of a digital twin simulation result."""
    if risk_prob > 0.7:
        return "Simulation indicates imminent failure under current load conditions."
    elif risk_prob > 0.3:
        return "Simulation shows gradual degradation; lifetime may be extended with maintenance."
    else:
        return "Simulation projects stable operation; no anomalies detected."
