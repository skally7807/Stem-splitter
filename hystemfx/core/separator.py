import torch
import numpy as np
from demucs import pretrained
from demucs.apply import apply_model

from .io import load_audio 

class DemucsSeparator:
    def __init__(self, device=None):
        """
        Demucs 모델 초기화
        :param device: cuda 또는 cpu (기본값: 자동 설정)
        """
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        print(f"[Init] Loading Demucs model: htdemucs_6s on {self.device}...")
        
        # Demucs Pretrained 모델 로드 (htdemucs_6s 고정)
        self.model = pretrained.get_model("htdemucs_6s")
        self.model.to(self.device)
        self.sample_rate = self.model.samplerate

    def separate_memory(self, audio: np.ndarray, shifts=0) -> dict:
        """
        메모리 상의 오디오 데이터를 받아서 분리된 Stems(딕셔너리)를 반환
        :param audio: (Channels, Time) 또는 (Time,) 형태의 Numpy 배열
        :param shifts: 0=fast(추천), 1=high-quality
        :return: {'vocals': array, 'guitar': array, ...}
        """
        # 차원 (Demucs [Batch, Channels, Time])
        if audio.ndim == 1:
            # Mono: (Samples,) -> (1, 1, Samples)
            audio = audio[None, None, :] 
        elif audio.ndim == 2:
            # Stereo: Ensure (Channels, Samples)
            if audio.shape[0] > audio.shape[1]:
                audio = audio.T
            # Add batch dim: (Channels, Samples) -> (1, Channels, Samples)
            audio = audio[None, :, :]
        
        # 텐서 변환
        wav = torch.tensor(audio, dtype=torch.float32).to(self.device)
        
        # 모델 적용 (분리 수행)
        with torch.no_grad():
            sources = apply_model(
                self.model, 
                wav,
                split=True,
                overlap=0.25,
                shifts=shifts
            )[0]

        stems = {}
        source_names = self.model.sources # ['drums', 'bass', 'other', 'vocals', 'guitar', 'piano']
        
        for name, source in zip(source_names, sources):
            stems[name] = source.cpu().numpy()

        return stems

    def separate_file(self, audio_path: str, shifts=0) -> dict:
        """
        파일 경로를 받아 로드 후 즉시 분리하여 메모리 데이터로 반환
        """
        print(f"Loading: {audio_path}")
        # Use standardized load_audio
        audio, _ = load_audio(audio_path, sr=self.sample_rate)
        
        print(f"Separating in memory (shifts={shifts})...")
        return self.separate_memory(audio, shifts=shifts)
    
    
if __name__ == "__main__":
    import sys
    import os
    import time
    import soundfile as sf

    sys.path.append(os.getcwd())

    test_file = "mixed.wav"
    
    if not os.path.exists(test_file):
        print(f"{test_file} 없음")
    else:
        print("--- Test Mode ---")
        
        sep = DemucsSeparator()
        
        print(f"분리 시작: {test_file}")
        t_start = time.time()
        
        result = sep.separate_file(test_file, shifts=0)
        
        t_end = time.time()
        print(f"소요 시간: {t_end - t_start:.2f}s")
        
        os.makedirs("test_debug", exist_ok=True)
        
        for stem_name, audio_data in result.items():
            save_path = f"test_debug/{stem_name}.wav"
            
            if audio_data.ndim == 2:
                audio_data = audio_data.T
                
            sf.write(save_path, audio_data, sep.sample_rate)
            print(f"저장됨: {save_path}")

        print("--- Done ---")