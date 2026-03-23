#!/usr/bin/env python3
"""
Setup script for Price Estimation Module
Run this to generate the dataset and train the ML model
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Add backend to path
backend_path = project_root / 'backend' / 'modules' / 'price_estimation'

def setup_price_estimation():
    """Setup price estimation module"""
    print("=" * 60)
    print("PRICE ESTIMATION MODULE SETUP")
    print("=" * 60)
    
    try:
        print("\n[1/2] Generating synthetic dataset...")
        from backend.modules.price_estimation.dataset_generator import generate_price_dataset
        
        dataset_path = backend_path / 'gear_price_dataset.csv'
        generate_price_dataset(num_rows=10000, output_path=dataset_path)
        print("✓ Dataset generated successfully")
        
        print("\n[2/2] Training ML model...")
        from backend.modules.price_estimation.model import PriceEstimationModel
        
        price_model = PriceEstimationModel()
        price_model.train(dataset_path)
        print("✓ Model trained and saved successfully")
        
        print("\n" + "=" * 60)
        print("✅ SETUP COMPLETE!")
        print("=" * 60)
        print("\nThe Price Estimation Module is now ready to use.")
        print(f"Model saved at: {price_model.model_path}")
        print(f"Dataset saved at: {dataset_path}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Setup failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = setup_price_estimation()
    sys.exit(0 if success else 1)
