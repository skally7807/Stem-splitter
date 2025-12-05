"""
Vocal Separator Module
보컬 분리 모듈
"""

import numpy as np
from typing import Optional, Union, Dict
from hystemfx.core.separator import DemucsSeparator

class VocalSeparator(DemucsSeparator):
    """
    보컬 분리 전용 클래스임.
    DemucsSeparator를 상속받아 'vocals' 스템을 추출함.
    """
    
    def __init__(self, model_name: str = "htdemucs_6s", device: Optional[str] = None):
        """
        초기화함.
        
        Parameters:
            model_name (str): 사용할 Demucs 모델 이름 (기본값: "htdemucs_6s")
            device (str): 실행 디바이스 ('cuda', 'cpu' 등)
        """
        super().__init__(device=device)
        self.target_stem = "vocals"

    def separate(
        self, 
        audio: np.ndarray, 
        sample_rate: int, 
        return_all_stems: bool = False
    ) -> Union[np.ndarray, Dict[str, np.ndarray]]:
        """
        오디오에서 보컬 성분을 분리함.
        
        Parameters:
            audio (np.ndarray): 입력 오디오 배열
            sample_rate (int): 샘플레이트
            return_all_stems (bool): True일 경우 모든 스템을 딕셔너리로 반환함.
            
        Returns:
            np.ndarray: 분리된 보컬 오디오 (return_all_stems=False)
            Dict[str, np.ndarray]: 모든 스템 (return_all_stems=True)
        """
        stems = self.separate_memory(audio)
        
        if return_all_stems:
            return stems
            
        if self.target_stem in stems:
            return stems[self.target_stem]
        else:
            print(f"Warning: '{self.target_stem}' stem not found. Returning 'other' instead.")
            return stems.get("other", audio)

def separate_vocal(
    audio: np.ndarray, 
    sample_rate: int, 
    device: Optional[str] = None
) -> np.ndarray:
    """
    편의 함수: 보컬 분리함.
    
    Parameters:
        audio (np.ndarray): 입력 오디오
        sample_rate (int): 샘플레이트
        device (str): 디바이스
        
    Returns:
        np.ndarray: 분리된 보컬 오디오
    """
    separator = VocalSeparator(device=device)
    return separator.separate(audio, sample_rate)
