import numpy as np
import librosa

def istft(mag, phase, sr, hop_length=512):
    # 역 STFT
    '''
    Params:
        mag (np.ndarray): Magnitude
        phase (np.ndarray): Phase
        sr (int): sample rate
        hop_length (int): Hop size
        
    Returns:
        y (np.ndarray): Time-domain audio signal.
    '''
    S = mag * np.exp(1j * phase)
    y = librosa.istft(S, hop_length=hop_length)
    return y