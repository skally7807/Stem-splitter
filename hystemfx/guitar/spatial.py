import numpy as np

def extract_side_channel(y):
    """
    스테레오 오디오에서 Side(양옆) 성분만 추출
    Center(중앙)에 위치한 보컬, 베이스, 킥 드럼이 제거됩니다.
    
    Params:
        y (np.ndarray): Audio time series (2, samples) - Stereo essential
        
    Returns:
        y_side (np.ndarray): Side component audio
    """
    if y.ndim == 1:
        return np.stack([y, y])
        
    side = (y[0] - y[1]) * 0.5
    
    y_side = np.stack([side, side])
    
    return y_side