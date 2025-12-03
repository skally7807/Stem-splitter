"""
Synth/Piano/Keyboard Source Separation Module
신디사이저, 피아노, 키보드 분리를 위한 모듈

Demucs의 htdemucs_6s 모델을 사용해 전체 믹스에서 
신디사이저/피아노/키보드 성분을 분리합니다.
"""

import numpy as np
import torch
from typing import Optional, Union
from pathlib import Path


class SynthSeparator:
    """
    Demucs 기반 신디사이저/피아노/키보드 분리기
    
    htdemucs_6s 모델은 다음 6개 stem을 분리합니다:
    - drums, bass, guitar, vocals, piano, other
    
    본 모듈은 'piano' stem을 추출하여 신디사이저/피아노/키보드 성분으로 활용합니다.
    """
    
    def __init__(self, model_name: str = "htdemucs_6s", device: Optional[str] = None):
        """
        Parameters:
            model_name (str): Demucs 모델 이름. 기본값은 'htdemucs_6s'
            device (str): 'cuda', 'cpu' 또는 None (자동 선택)
        """
        self.model_name = model_name
        
        # Device 설정
        if device is None:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device
            
        self.model = None
        self._load_model()
        
    def _load_model(self):
        """Demucs 모델 로드"""
        try:
            from demucs.pretrained import get_model
            from demucs.apply import apply_model
            
            print(f"Loading Demucs model: {self.model_name} on {self.device}")
            self.model = get_model(self.model_name)
            self.model.to(self.device)
            self.model.eval()
            self.apply_model = apply_model
            
        except ImportError:
            raise ImportError(
                "Demucs is not installed. Please install it with:\n"
                "pip install demucs"
            )
        except Exception as e:
            raise RuntimeError(f"Failed to load Demucs model: {e}")
    
    def separate(
        self, 
        audio: np.ndarray, 
        sample_rate: int,
        return_all_stems: bool = False
    ) -> Union[np.ndarray, dict]:
        """
        오디오에서 신디사이저/피아노/키보드 성분 분리
        
        Parameters:
            audio (np.ndarray): 입력 오디오 (shape: [channels, samples] 또는 [samples])
            sample_rate (int): 샘플레이트
            return_all_stems (bool): True면 모든 stem 반환, False면 piano만 반환
            
        Returns:
            np.ndarray 또는 dict: 분리된 신디사이저/피아노 오디오 또는 모든 stem
        """
        if self.model is None:
            raise RuntimeError("Model is not loaded")
        
        # Audio를 올바른 shape로 변환
        audio = self._prepare_audio(audio)
        
        # NumPy array를 PyTorch tensor로 변환
        audio_tensor = torch.from_numpy(audio).float().to(self.device)
        
        # 배치 차원 추가 [batch, channels, samples]
        if audio_tensor.ndim == 2:
            audio_tensor = audio_tensor.unsqueeze(0)
        
        # Demucs 모델 적용
        with torch.no_grad():
            stems = self.apply_model(
                self.model, 
                audio_tensor,
                device=self.device,
                split=True,  # 메모리 효율을 위해 split 사용
                overlap=0.25
            )
        
        # stems shape: [batch, n_stems, channels, samples]
        # htdemucs_6s의 stem 순서: drums, bass, other, vocals, guitar, piano
        stems = stems[0].cpu().numpy()  # 배치 차원 제거
        
        # Stem 이름 매핑
        stem_names = ["drums", "bass", "other", "vocals", "guitar", "piano"]
        stem_dict = {name: stems[i] for i, name in enumerate(stem_names)}
        
        if return_all_stems:
            return stem_dict
        else:
            # Piano stem만 반환 (신디사이저/피아노/키보드)
            return stem_dict["piano"]
    
    def _prepare_audio(self, audio: np.ndarray) -> np.ndarray:
        """
        오디오를 Demucs 입력 형식으로 준비
        
        Parameters:
            audio (np.ndarray): 입력 오디오
            
        Returns:
            np.ndarray: [channels, samples] 형태의 오디오
        """
        # 1D array인 경우 [1, samples]로 변환
        if audio.ndim == 1:
            audio = audio[np.newaxis, :]
        
        # [samples, channels]인 경우 transpose
        elif audio.ndim == 2 and audio.shape[0] > audio.shape[1]:
            # 일반적으로 samples > channels 이므로
            if audio.shape[0] > 100000:  # 임의의 threshold
                audio = audio.T
        
        # Mono를 Stereo로 변환 (Demucs는 stereo 선호)
        if audio.shape[0] == 1:
            audio = np.repeat(audio, 2, axis=0)
        
        return audio
    
    def separate_file(
        self,
        input_path: Union[str, Path],
        output_path: Optional[Union[str, Path]] = None,
        return_audio: bool = True
    ) -> Optional[np.ndarray]:
        """
        파일에서 직접 신디사이저/피아노/키보드 분리
        
        Parameters:
            input_path (str | Path): 입력 오디오 파일 경로
            output_path (str | Path): 출력 파일 경로 (선택사항)
            return_audio (bool): 오디오를 반환할지 여부
            
        Returns:
            np.ndarray: 분리된 오디오 (return_audio=True일 때)
        """
        try:
            from pedalboard.io import AudioFile
        except ImportError:
            raise ImportError(
                "Pedalboard is not installed. Please install it with:\n"
                "pip install pedalboard"
            )
        
        # 오디오 파일 로드
        with AudioFile(str(input_path)) as f:
            audio = f.read(f.frames)
            sample_rate = f.samplerate
        
        # 분리 수행
        separated = self.separate(audio, sample_rate)
        
        # 파일로 저장
        if output_path is not None:
            with AudioFile(
                str(output_path), 
                'w', 
                sample_rate, 
                separated.shape[0]
            ) as f:
                f.write(separated)
            print(f"Separated synth/piano saved to: {output_path}")
        
        if return_audio:
            return separated
        return None


def separate_synth(
    audio: np.ndarray,
    sample_rate: int,
    model_name: str = "htdemucs_6s",
    device: Optional[str] = None
) -> np.ndarray:
    """
    편의 함수: 신디사이저/피아노/키보드 성분 분리
    
    Parameters:
        audio (np.ndarray): 입력 오디오
        sample_rate (int): 샘플레이트
        model_name (str): Demucs 모델 이름
        device (str): 'cuda', 'cpu' 또는 None
        
    Returns:
        np.ndarray: 분리된 신디사이저/피아노 오디오
    """
    separator = SynthSeparator(model_name=model_name, device=device)
    return separator.separate(audio, sample_rate)
