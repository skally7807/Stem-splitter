import os
import librosa
import numpy as np
import matplotlib.pyplot as plt

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

def save_spectrogram_image(spectrogram, file_path):
    """
    스펙트로그램(또는 조각)을 이미지 파일로 저장합니다.
    사람이 보기 좋게 데시벨(dB) 스케일로 변환하여 저장합니다.
    """
    # 선형 스케일 -> 데시벨(dB) 스케일로 변환 (로그 변환)
    # 이렇게 하면 작은 소리도 더 밝게 잘 보입니다.
    spectrogram_db = librosa.amplitude_to_db(spectrogram, ref=np.max)

    plt.figure(figsize=(4, 4))
    # origin='lower'는 저주파가 아래쪽에 오게 함
    # aspect='auto'는 픽셀을 정사각형으로 강제하지 않음
    plt.imshow(spectrogram_db, aspect='auto', origin='lower', cmap='magma')
    plt.axis('off') # 축과 라벨 숨김
    plt.tight_layout()
    plt.savefig(file_path)
    plt.close()

# --- 테스트 코드 (이 파일만 실행 시 작동) ---
if __name__ == "__main__":
    # 테스트용 더미 데이터 생성
    print("유틸리티 테스트 중...")
    dummy_audio = np.random.rand(22050 * 5) # 5초짜리 랜덤 노이즈
    
    # 1. 변환 테스트
    mag, phase = audio_to_spectrogram(dummy_audio)
    print(f"스펙트로그램 변환 완료. 크기: {mag.shape}")
    
    # 2. 슬라이싱 테스트
    patches = slice_spectrogram(mag, patch_width=32)
    print(f"패치 슬라이싱 완료. 생성된 조각 수: {len(patches)}개")
    print(f"   조각 크기: {patches[0].shape}")

    # 3. 저장 테스트
    output_dir = "test_outputs"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    print(f"\n이미지 저장 테스트 중... ('{output_dir}' 폴더 확인)")
    # 처음 5개 조각만 저장해봅니다
    for i, patch in enumerate(patches[:5]):
        save_path = os.path.join(output_dir, f"patch_{i}.png")
        save_spectrogram_image(patch, save_path)
        print(f"  Saved: {save_path}")
        
    print("완료! 폴더를 확인해보세요.")