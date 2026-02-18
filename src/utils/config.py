import json
import os

CONFIG_FILE = r"C:\Projects\SGMAS\data\config.json"

def load_config():
    """
    Load cost factors from JSON if exists, otherwise use default.
    """
    default_config = {
        "material_rate_per_kg": {
            "Steel": 150,
            "Alloy Steel": 200,
            "Carbon Steel": 170
        },
        "labor_rate_per_hour": 300,
        "machine_hourly_cost": 400,
        "surface_treatment_charge": {
            "None": 0,
            "Hardening": 800,
            "Coating": 500
        },
        "urgency_percentage": 10  # %
    }

    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)

    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                config = json.load(f)
            return config
        except:
            return default_config
    else:
        return default_config

def save_config(config: dict):
    """
    Save updated cost factors to JSON.
    """
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)
