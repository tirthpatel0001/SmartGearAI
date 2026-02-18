import numpy as np

def calculate_severity(signals):
    """
    signals: list of numpy arrays (x, y, z vibrations)
    """

    rms_values = []
    energy_values = []

    for sig in signals:
        rms = np.sqrt(np.mean(sig ** 2))
        energy = np.sum(sig ** 2)

        rms_values.append(rms)
        energy_values.append(energy)

    rms_avg = np.mean(rms_values)
    energy_avg = np.mean(energy_values)

    # --- Severity thresholds (tunable) ---
    if rms_avg < 0.02:
        severity = "LOW"
    elif rms_avg < 0.05:
        severity = "MODERATE"
    else:
        severity = "SEVERE"

    return severity, rms_avg, energy_avg


def maintenance_recommendation(fault, severity):
    base_actions = {
        "healthy": "No action required. Continue monitoring.",
        "gear_wear": "Inspect gears and lubrication.",
        "gear_pitting": "Schedule surface inspection.",
        "miss_teeth": "Immediate gear replacement.",
        "teeth_break": "Emergency shutdown required.",
        "teeth_crack": "Reduce load and inspect crack growth.",
        "compound_fault": "Complete gearbox inspection required."
    }

    action = base_actions.get(fault.lower(), "Consult maintenance engineer.")

    if severity == "SEVERE":
        action += " ⚠ Immediate action required."
    elif severity == "MODERATE":
        action += " ⚠ Schedule maintenance soon."

    return action
