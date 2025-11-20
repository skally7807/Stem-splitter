import os
import librosa
import numpy as np
import matplotlib.pyplot as plt
from utils import audio_to_spectrogram, slice_spectrogram

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

# --- 테스트 코드 ---
if __name__ == "__main__":
    # data_loader 모듈 가져오기
    try:
        from data_loader import load_paired_dataset
    except ImportError:
        import sys
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from data_loader import load_paired_dataset

    print("시각화 모듈 테스트 시작...")
    
    # 프로젝트 루트 경로 찾기
    current_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(current_dir)
    data_path = os.path.join(root_dir, 'data')
    
    # 1. 데이터 로드 (10초만)
    print(f"데이터 폴더: {data_path}")
    mixed_list, target_list = load_paired_dataset(data_dir=data_path, duration=10.0)
    
    if not mixed_list:
        print("데이터를 찾을 수 없습니다! 대신 랜덤 노이즈로 테스트합니다.")
        sample_audio = np.random.rand(22050 * 5)
    else:
        sample_audio = mixed_list[0]
        print(f"첫 번째 곡 데이터를 사용합니다. (길이: {len(sample_audio)/22050:.1f}초)")
    
    # 2. 변환 (utils 모듈 사용)
    mag, phase = audio_to_spectrogram(sample_audio)
    print(f"스펙트로그램 변환 완료. 크기: {mag.shape}")
    
    # 3. 슬라이싱 (utils 모듈 사용)
    patches = slice_spectrogram(mag, patch_width=32)
    print(f"패치 슬라이싱 완료. 생성된 조각 수: {len(patches)}개")

    # 4. 저장 테스트
    output_dir = "test_outputs_viz"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    print(f"\n이미지 저장 중... ('{output_dir}' 폴더 확인)")
    for i, patch in enumerate(patches[:5]):
        save_path = os.path.join(output_dir, f"viz_patch_{i}.png")
        save_spectrogram_image(patch, save_path)
        print(f"  Saved: {save_path}")
        
    print("완료! 폴더를 확인해보세요.")
