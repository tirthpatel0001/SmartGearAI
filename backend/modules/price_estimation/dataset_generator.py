import pandas as pd
import numpy as np
import os
from pathlib import Path

def generate_price_dataset(num_rows=10000, output_path=None):
    """Generate synthetic gear price dataset"""
    
    np.random.seed(42)
    
    gear_types = ['Spur', 'Helical', 'Bevel', 'Worm']
    gearbox_types = ['Industrial', 'Marine', 'Automotive', 'Aerospace', 'Agricultural']
    materials = ['Steel', 'Alloy Steel', 'Cast Iron', 'Stainless Steel']
    surface_finishes = ['Ground', 'Polished', 'Honed', 'Raw']
    delivery_types = ['Normal', 'Urgent']
    
    data = {
        'gear_type': np.random.choice(gear_types, num_rows),
        'gearbox_type': np.random.choice(gearbox_types, num_rows),
        'material': np.random.choice(materials, num_rows),
        'module': np.random.uniform(1, 10, num_rows),
        'teeth': np.random.randint(12, 200, num_rows),
        'load': np.random.uniform(100, 10000, num_rows),
        'speed': np.random.uniform(100, 5000, num_rows),
        'gear_ratio': np.random.uniform(1, 100, num_rows),
        'heat_treatment': np.random.choice([True, False], num_rows),
        'surface_finish': np.random.choice(surface_finishes, num_rows),
        'quantity': np.random.choice([1, 5, 10, 25, 50, 100], num_rows),
        'delivery_type': np.random.choice(delivery_types, num_rows),
    }
    
    df = pd.DataFrame(data)
    
    # Calculate price based on technical specifications and material
    base_price = 40000  # Base price in Indian Rupees
    
    # Material multiplier
    material_multiplier = {
        'Steel': 1.0,
        'Alloy Steel': 1.3,
        'Cast Iron': 0.8,
        'Stainless Steel': 1.5
    }
    
    # Gear type multiplier
    gear_type_multiplier = {
        'Spur': 1.0,
        'Helical': 1.2,
        'Bevel': 1.4,
        'Worm': 1.6
    }
    
    df['price'] = (
        base_price +
        df['module'] * 50 +
        df['teeth'] * 2 +
        df['load'] * 0.01 +
        df['speed'] * 0.02 +
        np.random.normal(0, 5000, num_rows)  # Add noise in INR
    )
    
    # Apply multipliers
    df['price'] *= df['material'].map(material_multiplier)
    df['price'] *= df['gear_type'].map(gear_type_multiplier)
    
    # Heat treatment increases price
    df.loc[df['heat_treatment'], 'price'] *= 1.1
    
    # Surface finish multiplier
    finish_multiplier = {
        'Ground': 1.1,
        'Polished': 1.2,
        'Honed': 1.15,
        'Raw': 1.0
    }
    df['price'] *= df['surface_finish'].map(finish_multiplier)
    
    # Bulk discount
    quantity_discount = {
        1: 1.0,
        5: 0.95,
        10: 0.90,
        25: 0.85,
        50: 0.80,
        100: 0.75
    }
    df['price'] *= df['quantity'].map(quantity_discount)
    
    # Urgent delivery surcharge
    df.loc[df['delivery_type'] == 'Urgent', 'price'] *= 1.15
    
    df['price'] = df['price'].round(2)
    
    if output_path is None:
        output_path = Path(__file__).parent / 'gear_price_dataset.csv'
    else:
        output_path = Path(output_path)
    
    os.makedirs(output_path.parent, exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Dataset generated: {output_path}")
    print(f"Shape: {df.shape}")
    print(f"Price range: ₹{df['price'].min():.2f} - ₹{df['price'].max():.2f}")
    
    return df

if __name__ == '__main__':
    generate_price_dataset()
