import pickle
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from pathlib import Path
import os

class PriceEstimationModel:
    def __init__(self, model_path=None):
        self.model_path = model_path or Path(__file__).parent / 'price_model.pkl'
        self.label_encoders = {}
        self.feature_names = None
        self.model = None
        self.categorical_features = ['gear_type', 'gearbox_type', 'material', 'surface_finish', 'delivery_type']
        
    def train(self, dataset_path, test_size=0.2):
        """Train the ML model on dataset"""
        df = pd.read_csv(dataset_path)
        
        # Prepare features and target
        X = df.drop('price', axis=1)
        y = df['price']
        
        # Encode categorical features
        X_encoded = X.copy()
        for col in self.categorical_features:
            if col in X_encoded.columns:
                le = LabelEncoder()
                X_encoded[col] = le.fit_transform(X_encoded[col])
                self.label_encoders[col] = le
        
        self.feature_names = X_encoded.columns.tolist()
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X_encoded, y, test_size=test_size, random_state=42
        )
        
        # Train model
        self.model = RandomForestRegressor(
            n_estimators=100,
            max_depth=20,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1
        )
        
        self.model.fit(X_train, y_train)
        
        # Evaluate
        train_score = self.model.score(X_train, y_train)
        test_score = self.model.score(X_test, y_test)
        
        print(f"Train R² Score: {train_score:.4f}")
        print(f"Test R² Score: {test_score:.4f}")
        
        # Save model
        self.save()
        
    def predict(self, input_data):
        """Predict price for given input"""
        if self.model is None:
            self.load()
        
        # Ensure input_data is a DataFrame
        if not isinstance(input_data, pd.DataFrame):
            input_data = pd.DataFrame([input_data])
        
        X_encoded = input_data.copy()
        
        # Encode categorical features
        for col in self.categorical_features:
            if col in X_encoded.columns:
                if col in self.label_encoders:
                    le = self.label_encoders[col]
                    # Handle unknown categories
                    X_encoded[col] = X_encoded[col].map(
                        lambda x: le.transform([x])[0] if x in le.classes_ else 0
                    )
        
        # Ensure all features are present
        for col in self.feature_names:
            if col not in X_encoded.columns:
                X_encoded[col] = 0
        
        X_encoded = X_encoded[self.feature_names]
        
        prediction = self.model.predict(X_encoded)[0]
        return max(prediction, 100)  # Minimum price of $100
    
    def save(self):
        """Save model and encoders"""
        os.makedirs(self.model_path.parent, exist_ok=True)
        with open(self.model_path, 'wb') as f:
            pickle.dump({
                'model': self.model,
                'label_encoders': self.label_encoders,
                'feature_names': self.feature_names,
                'categorical_features': self.categorical_features
            }, f)
        print(f"Model saved to {self.model_path}")
    
    def load(self):
        """Load model and encoders"""
        if self.model_path.exists():
            with open(self.model_path, 'rb') as f:
                data = pickle.load(f)
                self.model = data['model']
                self.label_encoders = data['label_encoders']
                self.feature_names = data['feature_names']
                self.categorical_features = data['categorical_features']
            print(f"Model loaded from {self.model_path}")
        else:
            raise FileNotFoundError(f"Model not found at {self.model_path}")

if __name__ == '__main__':
    # Generate dataset first
    from dataset_generator import generate_price_dataset
    
    dataset_path = Path(__file__).parent / 'gear_price_dataset.csv'
    
    if not dataset_path.exists():
        print("Generating dataset...")
        generate_price_dataset(output_path=dataset_path)
    
    print("Training model...")
    price_model = PriceEstimationModel()
    price_model.train(dataset_path)
    print("Model training complete!")
