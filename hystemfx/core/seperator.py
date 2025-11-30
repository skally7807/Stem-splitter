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
        print(f"Loading Demucs model: htdemucs_6s on {self.device}...")
        
        # Demucs Pretrained 모델 로드 (htdemucs_6s 고정)
        self.model = pretrained.get_model("htdemucs_6s")
        self.model.to(self.device)
        self.sample_rate = self.model.samplerate

    def separate(self, audio: np.ndarray, sample_rate: int = 44100) -> dict:
        """
        메모리 상의 오디오 데이터를 받아서 분리된 Stems(딕셔너리)를 반환
        """
        # 차원 맞추기 (samples,) -> (1, samples)
        if audio.ndim == 1:
            audio = audio[None, :] 
        
        # 텐서 변환
        wav = torch.tensor(audio, dtype=torch.float32).to(self.device)
        
        # 모델 적용 (분리 수행)
        # shifts=1: 속도 위주
        with torch.no_grad():
            sources = apply_model(self.model, wav[None], shifts=1)[0]

        # 결과 매핑
        stems = {}
        source_names = self.model.sources # ['drums', 'bass', 'other', 'vocals', 'guitar', 'piano']
        
        for name, source in zip(source_names, sources):
            stems[name] = source.cpu().numpy()

        return stems

    def separate_file(self, audio_path: str) -> dict:
        """
        파일 경로를 입력받아 로드 후 분리 결과를 반환
        """
        print(f"Loading and separating file: {audio_path}")
        audio, sr = load_audio(audio_path, target_sr=self.sample_rate)
        return self.separate(audio, sample_rate=sr)