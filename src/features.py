import librosa
import numpy as np

def extract_features(y, sr, n_fft=2048, hop_length=512):
    """
    오디오 파형에서 피아노 식별을 위한 핵심 특징들을 추출합니다.
    
    Args:
        y: 오디오 파형
        sr: 샘플링 레이트
        n_fft: FFT 크기
        hop_length: 프레임 이동 간격
        
    Returns:
        features (np.ndarray): 추출된 특징 행렬 (n_features x n_frames)
    """
    
    # 1. MFCC (Mel-frequency cepstral coefficients) - 음색(Timbre) 파악
    # 피아노의 고유한 배음 구조를 파악하는 데 가장 중요한 특징입니다.
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=20, n_fft=n_fft, hop_length=hop_length)
    
    # 2. Spectral Flatness - 소리의 선명도/노이즈 정도
    # 피아노는 타격음(Noise)과 배음(Tone)이 섞여 있어 이 특징이 유용합니다.
    flatness = librosa.feature.spectral_flatness(y=y, n_fft=n_fft, hop_length=hop_length)
    
    # 3. Onset Strength - 타격감 감지
    # 피아노는 건반을 때리는 순간 강한 에너지가 발생하므로 시작점(Onset)이 중요합니다.
    onset_env = librosa.onset.onset_strength(y=y, sr=sr, n_fft=n_fft, hop_length=hop_length)
    # 차원을 맞추기 위해 reshape (1, n_frames)
    onset_env = onset_env.reshape(1, -1)
    
    # 4. HPSS (Harmonic-Percussive Source Separation) Ratio
    # 피아노는 타악기적 요소(Percussive)와 화성적 요소(Harmonic)를 모두 가집니다.
    # 이 둘의 비율은 피아노를 구분하는 좋은 지표가 됩니다.
    y_harmonic, y_percussive = librosa.effects.hpss(y)
    
    # 각 프레임별 에너지 계산
    S_h = librosa.feature.rms(y=y_harmonic, frame_length=n_fft, hop_length=hop_length)
    S_p = librosa.feature.rms(y=y_percussive, frame_length=n_fft, hop_length=hop_length)
    
    # Harmonic 비율 계산 (0~1)
    hpss_ratio = S_h / (S_h + S_p + 1e-8)
    
    # 5. Spectral Centroid & Rolloff - 밝기 및 주파수 분포
    centroid = librosa.feature.spectral_centroid(y=y, sr=sr, n_fft=n_fft, hop_length=hop_length)
    rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr, n_fft=n_fft, hop_length=hop_length)
    
    # 모든 특징을 하나로 합칩니다.
    # MFCC(20) + Flatness(1) + Onset(1) + HPSS_Ratio(1) + Centroid(1) + Rolloff(1) = 25 features
    features = np.concatenate([
        mfcc, 
        flatness, 
        onset_env, 
        hpss_ratio,
        centroid,
        rolloff
    ], axis=0)
    
    # 프레임 수 맞추기 (가끔 1프레임 차이가 날 수 있음)
    min_frames = min(f.shape[1] for f in [mfcc, flatness, onset_env, hpss_ratio, centroid, rolloff])
    features = features[:, :min_frames]
    
    return features
