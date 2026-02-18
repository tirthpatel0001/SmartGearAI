import pandas as pd

VIB_COLUMNS = [
    "gearbox_vibration_x",
    "gearbox_vibration_y",
    "gearbox_vibration_z"
]

def load_csv(file_path):
    df = pd.read_csv(file_path)

    for col in VIB_COLUMNS:
        if col not in df.columns:
            raise ValueError(f"Missing column {col} in {file_path}")

    return df[VIB_COLUMNS]
