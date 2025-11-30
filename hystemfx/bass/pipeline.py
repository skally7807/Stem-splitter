import os
import sys
import soundfile as sf
import torch
import numpy as np

# =================================================================
# [경로 설정]
# =================================================================
current_file_path = os.path.abspath(__file__)
root_path = os.path.dirname(os.path.dirname(os.path.dirname(current_file_path)))
if root_path not in sys.path:
    sys.path.append(root_path)
from hystemfx.core.seperator import DemucsSeparator


from hystemfx.bass.effects import BassRack

class BassPipeline:
    def __init__(self, device=None):
        
        self.device = device if device else ('cuda' if torch.cuda.is_available() else 'cpu')
        
        if DemucsSeparator:
            try:
                self.separator = DemucsSeparator(device=self.device)
                print(f"분리기 로드 성공 (Device: {self.device})")
            except Exception as e:
                print(f"초기화 중 에러 발생: {e}")
                self.separator = None
        else:
            self.separator = None

        self.fx_rack = BassRack()

    def process_file(self, input_path, output_path, preset="default", seed=None):
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"File not found: {input_path}")

        print(f"▶ Processing: {input_path} (Preset: {preset})")

        raw_bass = None
        sr = 44100 

        if self.separator:
            try:
                stems = self.separator.separate_file(input_path)
                
                if isinstance(stems, dict) and 'bass' in stems:
                    raw_bass = stems['bass']
                    print("  Bass Stem 추출 완료")
                else:
                    print(" fail")
                    
            except Exception as e:
                print(f" 에러 발생: {e}")

        # [예외 처리] 분리 실패 시 원본 사용
        if raw_bass is None:
            print("수정예정")
            raw_bass, sr = sf.read(input_path)
            if raw_bass.ndim > 1 and raw_bass.shape[0] > raw_bass.shape[1]:
                raw_bass = raw_bass.T
            if raw_bass.ndim == 1:
                raw_bass = raw_bass[np.newaxis, :]

        
        self.fx_rack.load_preset(preset)
        
        if seed is not None:
            self.fx_rack.randomize_parameters(seed)

        processed = self.fx_rack.process(raw_bass, sr)

        if processed.ndim > 1 and processed.shape[0] < processed.shape[1]:
            processed = processed.T
            
        sf.write(output_path, processed, sr)
        print(f"저장 위치 :  {output_path}")