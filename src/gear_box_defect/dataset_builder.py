import numpy as np
from scipy.stats import kurtosis, skew
from scipy.fft import fft

def extract_features(signal):
    mean = np.mean(signal)
    std = np.std(signal)
    rms = np.sqrt(np.mean(signal ** 2))
    kurt = kurtosis(signal)
    sk = skew(signal)
    ptp = np.ptp(signal)

    fft_vals = abs(fft(signal))
    fft_mean = np.mean(fft_vals)
    fft_max = np.max(fft_vals)
    energy = np.sum(fft_vals ** 2)

    return [
        mean, std, rms,
        kurt, sk, ptp,
        fft_mean, fft_max, energy
    ]
