import pandas as pd
import numpy as np
import os

project_root = r"C:\Projects\SGMAS"
raw_data_path = os.path.join(project_root, "data", "raw")
os.makedirs(raw_data_path, exist_ok=True)

def create_gear_price_dataset(num_samples=20000):
    """
    Generates a large realistic synthetic gear dataset for ML price prediction.
    """
    np.random.seed(42)

    gear_types = ["Spur", "Helical", "Bevel"]
    materials = ["Steel", "Alloy Steel", "Carbon Steel"]
    surface_treatments = ["None", "Hardening", "Coating"]

    data = []
    for _ in range(num_samples):
        gear_type = np.random.choice(gear_types)
        material = np.random.choice(materials)
        diameter = np.random.randint(50, 300)   # mm
        teeth = np.random.randint(int(diameter*0.3), int(diameter*0.6))
        thickness = np.random.randint(int(diameter*0.05), int(diameter*0.2))
        quantity = np.random.randint(1, 500)
        special_req = np.random.choice(surface_treatments)

        # Approximate weight in kg
        outer_radius = diameter / 2
        inner_radius = outer_radius * 0.3
        volume_cm3 = 3.1416 * (outer_radius**2 - inner_radius**2) * thickness * 0.1
        material_density = {'Steel': 7.85, 'Alloy Steel': 7.8, 'Carbon Steel': 7.7}
        weight_kg = volume_cm3 * material_density[material] / 1000

        # Base price formula
        material_rate = {'Steel': 150, 'Alloy Steel': 200, 'Carbon Steel': 170}[material]
        treatment_cost = {'None': 0, 'Hardening': 800, 'Coating': 500}[special_req]
        labor_rate = 300
        machine_rate = 400
        labor_hours_per_gear = 0.5 + 0.01*teeth
        machine_hours_per_gear = 0.5 + 0.005*diameter
        urgency_multiplier = 1 + np.random.randint(0, 21)/100  # 0–20% urgency

        base_price = (
            weight_kg * material_rate +
            labor_hours_per_gear * labor_rate +
            machine_hours_per_gear * machine_rate +
            treatment_cost
        ) * urgency_multiplier

        total_price = base_price * quantity

        data.append({
            "Gear_Type": gear_type,
            "Material": material,
            "Diameter_mm": diameter,
            "Teeth_Count": teeth,
            "Thickness_mm": thickness,
            "Quantity": quantity,
            "Special_Requirement": special_req,
            "Weight_kg": round(weight_kg,2),
            "Total_Price": round(total_price,2)
        })

    df = pd.DataFrame(data)
    file_path = os.path.join(raw_data_path, "gear_price_data.csv")
    df.to_csv(file_path, index=False)
    print(f"Dataset created successfully at:\n{file_path}")
    return df

if __name__ == "__main__":
    create_gear_price_dataset()
