import os
import numpy as np
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix

from .data_loader import load_csv
from .preprocessing import fit_scaler, transform_signal, scaler
from .dataset_builder import extract_features


# ================= PATHS =================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data", "raw")
MODEL_PATH = os.path.join(BASE_DIR, "gearbox_model.pkl")

print("BASE DIR:", BASE_DIR)
print("DATA DIR:", DATA_DIR)

# ================= LOAD DATA =================
X, y = [], []
all_signals = []

print("\n[1/5] Scanning dataset folders...")

total_files = 0
for label in sorted(os.listdir(DATA_DIR)):
    class_dir = os.path.join(DATA_DIR, label)
    if not os.path.isdir(class_dir):
        continue
    csvs = [f for f in os.listdir(class_dir) if f.endswith(".csv")]
    print(f"  Class '{label}': {len(csvs)} files")
    total_files += len(csvs)

print(f"\nTotal CSV files found: {total_files}")
if total_files == 0:
    raise RuntimeError("NO CSV FILES FOUND. Check data/raw path.")

# ================= FIT SCALER =================
print("\n[2/5] Reading signals to fit scaler...")

file_count = 0
for label in sorted(os.listdir(DATA_DIR)):
    class_dir = os.path.join(DATA_DIR, label)
    if not os.path.isdir(class_dir):
        continue

    for file in os.listdir(class_dir):
        if not file.endswith(".csv"):
            continue

        file_count += 1
        print(f"  Reading ({file_count}/{total_files}): {label}/{file}")

        df = load_csv(os.path.join(class_dir, file))
        for col in df.columns:
            all_signals.append(df[col].dropna().values)

print("\nFitting scaler on all signals...")
fit_scaler(all_signals)

# ================= FEATURE EXTRACTION =================
print("\n[3/5] Extracting features...")

file_count = 0
for label in sorted(os.listdir(DATA_DIR)):
    class_dir = os.path.join(DATA_DIR, label)

    for file in os.listdir(class_dir):
        if not file.endswith(".csv"):
            continue

        file_count += 1
        print(f"  Processing ({file_count}/{total_files}): {label}/{file}")

        df = load_csv(os.path.join(class_dir, file))

        features = []
        for col in df.columns:
            signal = transform_signal(df[col])
            features.extend(extract_features(signal))

        X.append(features)
        y.append(label)

X = np.array(X)
y = np.array(y)

print("\n[4/5] Dataset ready")
print("Samples:", X.shape[0])
print("Features per sample:", X.shape[1])

# ================= LABEL ENCODING =================
encoder = LabelEncoder()
y_encoded = encoder.fit_transform(y)

print("\nClass Mapping:")
for i, cls in enumerate(encoder.classes_):
    print(f"{i} -> {cls}")

# ================= TRAIN =================
print("\n[5/5] Training model...")

X_train, X_test, y_train, y_test = train_test_split(
    X, y_encoded,
    test_size=0.2,
    stratify=y_encoded,
    random_state=42
)

model = RandomForestClassifier(
    n_estimators=300,   # reduced for faster first run
    class_weight="balanced",
    random_state=42,
    n_jobs=-1
)

model.fit(X_train, y_train)

y_pred = model.predict(X_test)

print("\nClassification Report:\n")
print(classification_report(y_test, y_pred, target_names=encoder.classes_))

print("\nConfusion Matrix:\n")
print(confusion_matrix(y_test, y_pred))

joblib.dump(
    {"model": model, "encoder": encoder, "scaler": scaler},
    MODEL_PATH
)

print("\n✅ Training completed successfully")
print("Model saved at:", MODEL_PATH)
