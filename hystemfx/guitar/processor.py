import numpy as np
import librosa
import soundfile as sf

from .spatial import extract_side_channel
from .filter import bandpass_filter
from ..stft import stft
from ..istft import istft

def process_guitar_extraction(input_path, output_path):
    """
    3단계 파이프라인을 통해 기타 세션을 추출합니다.
    1. Spatial: 보컬/베이스 제거 (Center 소거)
    2. HPSS: 드럼 제거 (Harmonic 추출)
    3. Filter: 잡음 제거 (Bandpass)
    """
    print(f"Processing: {input_path}")
    
    y, sr = librosa.load(input_path, sr=None, mono=False)
    
    if y.ndim == 1:
        raise ValueError("입력 파일이 Mono입니다. Spatial 처리를 위해 Stereo 파일이 필요합니다.")

    y_side = extract_side_channel(y)

    processed_channels = []
    
    for channel in y_side:
        mag, phase = stft(channel, sr)
        
        # margin=2.0: 드럼을 좀 더 확실하게 지움
        harm, _ = librosa.decompose.hpss(mag, margin=2.0)
        
        y_harm = istft(harm, phase, sr)
        processed_channels.append(y_harm)
        
    y_hpss = np.array(processed_channels)

    y_final = bandpass_filter(y_hpss, sr, low_cut=100, high_cut=6000)

    # Normalize & Save
    y_final = librosa.util.normalize(y_final, axis=1)
    sf.write(output_path, y_final.T, sr)
    print(f"Extraction Complete: {output_path}")

# [Test]
if __name__ == "__main__":
    process_guitar_extraction("mixed.wav", "final_guitar.wav")