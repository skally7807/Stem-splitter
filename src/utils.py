import librosa
import numpy as np

def audio_to_spectrogram(y, n_fft=2048, hop_length=512):
    """
    오디오 파형(y)을 스펙트로그램 이미지(Magnitude)와 위상(Phase)으로 변환합니다.
    
    Args:
        y: 오디오 파형 데이터
        n_fft: FFT 윈도우 크기 (주파수 해상도)
        hop_length: 프레임 이동 간격 (시간 해상도)
        
    Returns:
        magnitude (np.ndarray): 에너지 스펙트로그램 (이미지 분석용)
        phase (np.ndarray): 위상 정보 (나중에 소리로 복원할 때 필요)
    """
    # STFT 변환 (소리 -> 주파수 도메인)
    D = librosa.stft(y, n_fft=n_fft, hop_length=hop_length)
    
    # 에너지(크기)와 위상 분리
    magnitude = np.abs(D)
    phase = np.angle(D)
    
    return magnitude, phase

def spectrogram_to_audio(magnitude, phase, n_fft=2048, hop_length=512):
    """
    (나중에 사용) 스펙트로그램과 위상을 다시 오디오로 복원합니다 (ISTFT).
    """
    # 복소수 스펙트로그램 재구성
    D = magnitude * np.exp(1j * phase)
    
    # ISTFT (주파수 도메인 -> 소리)
    y = librosa.istft(D, hop_length=hop_length, n_fft=n_fft)
    return y

def slice_spectrogram(magnitude, patch_width=32):
    """
    긴 스펙트로그램을 작은 '이미지 조각(Patch)'들로 자릅니다.
    
    Args:
        magnitude: 전체 스펙트로그램 (Freq x Time)
        patch_width: 조각의 너비 (프레임 수). 
                     기본값 32는 약 0.7초(22050Hz 기준)에 해당합니다.
                     
    Returns:
        patches (list): 잘라진 조각들의 리스트
    """
    n_frames = magnitude.shape[1]
    patches = []
    
    # patch_width 간격으로 슬라이싱
    for i in range(0, n_frames, patch_width):
        patch = magnitude[:, i:i+patch_width]
        
        # 마지막 조각이 너무 짧으면 버림 (데이터 균일성을 위해)
        if patch.shape[1] == patch_width:
            patches.append(patch)
            
    return patches
