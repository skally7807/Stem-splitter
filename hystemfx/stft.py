import numpy as np
import librosa

def stft(y, sr, n_fft=2048, hop_length=512, window="hann"):
    # STFT magnitude 랑 phase 계산
    '''
    Params:
        y (np.ndarray): Audio time series
        sr (int): sample rate
        n_fft (int): FFT size
        hop_length (int): Hop size
        window (str): Window type
        
    Returns:
        mag (np.ndarray): Magnitude spectrogram
        phase (np.ndarray): Phase spectrogram
    '''
    S = librosa.stft(
        y,
        n_fft=n_fft,
        hop_length=hop_length,
        window=window,
        center=True
    )
    mag = np.abs(S)
    phase = np.angle(S)
    return mag, phase

