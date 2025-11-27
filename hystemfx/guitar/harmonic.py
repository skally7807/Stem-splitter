import librosa
import soundfile as sf
import numpy as np
# import sys
# import os

# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from stft import stft
from istft import istft

def extract_harmonic_component(input_path, output_path, margin=2.0):
    """
    HPSS 알고리즘을 사용하여 오디오에서 Harmonic(화성/기타/보컬) 성분만 추출합니다.
    Percussive(드럼/타격음) 성분은 제거됩니다.
    """
    print(f"[Processing] Loading: {input_path}")
    
    y, sr = librosa.load(input_path, sr=None, mono=False) # Stereo 유지

    if y.ndim == 1:
        y = np.stack([y, y])

    # Process each channel
    output_channels = []
    
    for channel_y in y:
        mag, phase = stft(channel_y, sr)

        # HPSS 분리
        # (기본값 1.0 ~ 3.0)
        harm, perc = librosa.decompose.hpss(mag, margin=margin)

        # 사용자 정의 함수 사용 (src/istft.py)
        # Harmonic 성분만 사용하여 복원
        y_harmonic = istft(harm, phase, sr)
        output_channels.append(y_harmonic)

    # Save
    y_out = np.array(output_channels)
    
    # Normalize
    y_out = librosa.util.normalize(y_out, axis=1)
    
    sf.write(output_path, y_out.T, sr)
    print(f"[Done] Saved to: {output_path}")

# [Test]
if __name__ == "__main__":
    input_file = "mixed.wav" 
    output_file = "guitar_harmonic_only.wav"
    
    try:
        extract_harmonic_component(input_file, output_file)
    except Exception as e:
        print(f"Error: {e}")