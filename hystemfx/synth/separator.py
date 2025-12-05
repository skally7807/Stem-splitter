"""
Synth Separator Module
신디사이저/피아노 분리 모듈
"""

import numpy as np
from typing import Optional, Union, Dict
from hystemfx.core.separator import DemucsSeparator

class SynthSeparator(DemucsSeparator):
    """
    신디사이저/피아노 분리 전용 클래스
    DemucsSeparator를 상속받아 'piano' 스템을 추출합니다.
    """
    
    def __init__(self, model_name: str = "htdemucs_6s", device: Optional[str] = None):
        """
        초기화
        
        Parameters:
            model_name (str): 사용할 Demucs 모델 이름 (기본값: "htdemucs_6s")
            device (str): 실행 디바이스 ('cuda', 'cpu' 등)
        """
        # DemucsSeparator는 model_name을 인자로 받지 않고 내부에서 고정하지만,
        # 확장성을 위해 인자는 받아둡니다. (현재는 부모 init 호출 시 무시됨)
        super().__init__(device=device)
        self.target_stem = "piano"

    def separate(
        self, 
        audio: np.ndarray, 
        sample_rate: int, 
        return_all_stems: bool = False
    ) -> Union[np.ndarray, Dict[str, np.ndarray]]:
        """
        오디오에서 신디사이저/피아노 성분 분리
        
        Parameters:
            audio (np.ndarray): 입력 오디오 배열
            sample_rate (int): 샘플레이트
            return_all_stems (bool): True일 경우 모든 스템을 딕셔너리로 반환
            
        Returns:
            np.ndarray: 분리된 신디사이저 오디오 (return_all_stems=False)
            Dict[str, np.ndarray]: 모든 스템 (return_all_stems=True)
        """
        # DemucsSeparator.separate_memory 사용
        stems = self.separate_memory(audio)
        
        if return_all_stems:
            return stems
            
        # piano 스템 반환 (없으면 other 반환하거나 에러 처리?)
        # htdemucs_6s는 ['drums', 'bass', 'other', 'vocals', 'guitar', 'piano'] 반환
        if self.target_stem in stems:
            return stems[self.target_stem]
        else:
            print(f"Warning: '{self.target_stem}' stem not found. Returning 'other' instead.")
            return stems.get("other", audio)

def separate_synth(
    audio: np.ndarray, 
    sample_rate: int, 
    device: Optional[str] = None
) -> np.ndarray:
    """
    편의 함수: 신디사이저 분리
    
    Parameters:
        audio (np.ndarray): 입력 오디오
        sample_rate (int): 샘플레이트
        device (str): 디바이스
        
    Returns:
        np.ndarray: 분리된 신디사이저 오디오
    """
    separator = SynthSeparator(device=device)
    return separator.separate(audio, sample_rate)
