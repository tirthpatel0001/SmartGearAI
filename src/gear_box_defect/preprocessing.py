import numpy as np
from sklearn.preprocessing import StandardScaler

def transform_signal_with_scaler(signal, scaler):
    signal = signal.dropna().values.reshape(-1, 1)
    return scaler.transform(signal).flatten()
