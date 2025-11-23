import scipy.signal
import numpy as np

def bandpass_filter(y, sr, low_cut=80, high_cut=6000):
    """
    기타 주파수 대역에 맞는 Bandpass Filter를 적용
    
    Params:
        y (np.ndarray): Audio time series
        sr (int): Sample rate
        low_cut (int): 최저 주파수 (Hz) - 그 이하는 자름 (Bass 제거)
        high_cut (int): 최고 주파수 (Hz) - 그 이상은 자름 (Noise 제거)
    """
   
    sos = scipy.signal.butter(N=4, Wn=[low_cut, high_cut], btype='bandpass', fs=sr, output='sos')

    if y.ndim == 2:
        y_filtered = np.array([scipy.signal.sosfilt(sos, ch) for ch in y])
    else:
        y_filtered = scipy.signal.sosfilt(sos, y)
        
    return y_filtered