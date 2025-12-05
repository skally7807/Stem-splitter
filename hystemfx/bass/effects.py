import numpy as np
import random
import logging
from typing import Optional, Dict, Union, Tuple

from pedalboard import (
    Pedalboard, 
    NoiseGate, 
    Compressor, 
    Distortion, 
    LowShelfFilter, 
    PeakFilter, 
    HighShelfFilter,
    Chorus, 
    Limiter,
    Gain
)

# 로깅 설정 (디버깅 용도)
logger = logging.getLogger("BassFX")

class BassRack:
    """
    Bass Guitar Processing Rack
    
    베이스 기타의 음향적 특성(Low-end retention, Dynamic consistency)을 고려하여
    설계된 직렬 이펙트 체인 클래스입니다.
    
    구조 (Signal Flow):
    1. Input Cleaning (Noise Gate)
    2. Dynamics (Compressor)
    3. Tone Shaping (Distortion -> EQ)
    4. Modulation (Chorus - Optional)
    5. Output Control (Limiter)
    """

    # 기본 설정값 상수 정의 (Default Configuration)
    DEFAULT_CONFIG = {
        # Section 1: Dynamics & Clean
        'gate_threshold_db': -55.0,
        'gate_ratio': 10.0,
        'comp_threshold_db': -20.0,
        'comp_ratio': 4.0,
        'comp_attack_ms': 20.0,
        'comp_release_ms': 100.0,
        
        # Section 2: Tone & Color
        'drive_db': 8.0,            # Saturation 양
        'low_shelf_freq': 80.0,     # Sub-bass 기준점
        'low_shelf_gain': 2.0,      # Sub-bass 부스트 양
        'mid_scoop_freq': 400.0,    # Muddy 대역
        'mid_scoop_gain': -3.0,     # Scoop 양
        'mid_scoop_q': 1.5,         # Scoop 대역폭
        
        # Section 3: Space & Modulation
        'chorus_rate_hz': 0.5,
        'chorus_depth': 0.15,
        'chorus_mix': 0.3,
        
        # Section 4: Output
        'limiter_threshold_db': -0.5,
        'output_gain_db': 0.0
    }

    def __init__(self, preset: str = "default", verbose: bool = False):
        """
        BassRack 초기화
    
        """
        self.verbose = verbose
        if self.verbose:
            print(f"[BassRack] Initializing with preset: '{preset}'")
        self.current_settings = self.DEFAULT_CONFIG.copy()
        
        # 내부 Pedalboard 객체
        self.board: Optional[Pedalboard] = None
        
        # 프리셋 적용 및 보드 빌드
        if preset != "default":
            self.load_preset(preset)
        else:
            self._build_board()

    def _build_board(self) -> None:
        """
        """
        s = self.current_settings
        effects_list = []

        # 빈 구간 노이즈 정리.
        effects_list.append(
            NoiseGate(
                threshold_db=s['gate_threshold_db'], 
                ratio=s['gate_ratio'], 
                release_ms=100
            )
        )

        # 펀치감을 만들고 다이내믹을 평탄화(README참고  )
        effects_list.append(
            Compressor(
                threshold_db=s['comp_threshold_db'],
                ratio=s['comp_ratio'],
                attack_ms=s['comp_attack_ms'],
                release_ms=s['comp_release_ms']
            )
        )

        #배음(Harmonics) 추가하여 존재감 부각
        if s['drive_db'] > 0:
            effects_list.append(Distortion(drive_db=s['drive_db']))

        # 베이스 톤 메이킹의 핵심
        #  (저음 보강)
        effects_list.append(
            LowShelfFilter(
                cutoff_frequency_hz=s['low_shelf_freq'], 
                gain_db=s['low_shelf_gain']
            )
        )
        #(깔끔한 톤을 위해 중음역대 정리)
        effects_list.append(
            PeakFilter(
                cutoff_frequency_hz=s['mid_scoop_freq'], 
                gain_db=s['mid_scoop_gain'], 
                q=s['mid_scoop_q']
            )
        )

        # 스테레오 이미지 확장 (옵션)
        if s['chorus_mix'] > 0:
            effects_list.append(
                Chorus(
                    rate_hz=s['chorus_rate_hz'], 
                    depth=s['chorus_depth'], 
                    mix=s['chorus_mix']
                )
            )

        # Safety & Output
        effects_list.append(
            Limiter(
                threshold_db=s['limiter_threshold_db'], 
                release_ms=100
            )
        )
        
        #객체 생성
        self.board = Pedalboard(effects_list)
        
        if self.verbose:
            print("[BassRack] Effect chain rebuilt successfully.")

    def process(self, audio: np.ndarray, sample_rate: int) -> np.ndarray:
        
        # 방어 코드
        if self.board is None:
            self._build_board()

        input_audio = audio.copy()
        
        
        if input_audio.ndim == 1:
            input_audio = input_audio[np.newaxis, :]

        transposed = False
        if input_audio.shape[0] > input_audio.shape[1]:
            input_audio = input_audio.T
            transposed = True

        processed_audio = self.board(input_audio, sample_rate)

        # 복구
        if transposed:
            processed_audio = processed_audio.T

        return processed_audio

    def load_preset(self, preset_name: str) -> 'BassRack':
        updates = {}
        
        if preset_name == "default":
            self.current_settings = self.DEFAULT_CONFIG.copy()
            
        elif preset_name == "vintage":
            updates = {
                'drive_db': 12.0,
                'low_shelf_gain': 3.5,
                'mid_scoop_gain': -1.0,     # 중음을 덜 깎는 효과.
                'chorus_mix': 0.0,          # 코러스 끔
                'comp_attack_ms': 35.0      
            }
            
        elif preset_name == "modern":
            updates = {
                'drive_db': 6.0,
                'low_shelf_gain': 2.0,
                'mid_scoop_gain': -5.0,     
                'chorus_mix': 0.25,
                'comp_ratio': 6.0           # 강한 압축
            }
            
        elif preset_name == "fuzz":
            updates = {
                'drive_db': 22.0,           # 아주 강한 드라이브
                'gate_threshold_db': -40.0, # 노이즈 게이트 강화
                'mid_scoop_gain': 0.0,      # 미드 복구 (존재감 확보)
                'comp_threshold_db': -25.0
            }
        else:
            print(f"[Warning] Unknown preset '{preset_name}'. Loading default.")
            self.current_settings = self.DEFAULT_CONFIG.copy()

        if updates:
            self.current_settings.update(updates)
            
        self._build_board()
        return self  # Method Chaining 지원

    def randomize_parameters(self, seed: Optional[int] = None) -> 'BassRack':
        
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)
            
        # 랜덤화 범위 정의 (Min, Max)
        ranges = {
            'drive_db': (0.0, 15.0),
            'comp_ratio': (3.0, 6.0),
            'low_shelf_gain': (0.0, 4.0),
            'mid_scoop_gain': (-6.0, -1.0),
            'chorus_mix': (0.0, 0.4),
            'chorus_depth': (0.1, 0.3)
        }
        
        # 랜덤 값 생성 및 적용
        random_updates = {}
        for key, (min_val, max_val) in ranges.items():
            random_updates[key] = random.uniform(min_val, max_val)
            
        # 미세 조정
        random_updates['comp_threshold_db'] = random.uniform(-25.0, -15.0)

        if self.verbose:
            print("[BassRack] Applying random parameters for augmentation...")
            
        self.current_settings.update(random_updates)
        self._build_board()
        
        return self

    def get_current_settings(self) -> Dict[str, float]:
        """현재 적용된 파라미터 값을 반환합니다. (로깅/저장용)"""
        return self.current_settings.copy()

# =============================================================================
# Helper Function
# =============================================================================

def apply_bass_effects(
    audio: np.ndarray, 
    sample_rate: int, 
    preset: str = "default",
    seed: Optional[int] = None
) -> np.ndarray:
    """
    외부에서 BassRack 클래스를 직접 인스턴스화하지 않고
    함수 호출 한 번으로 이펙트를 적용할 수 있는 래퍼(Wrapper) 함수입니다.
    
    Args:
        audio: 입력 오디오 데이터
        sample_rate: 샘플링 레이트
        preset: 프리셋 이름
        seed: 랜덤 시드 (None이 아닐 경우 랜덤화 적용)
        
    Returns:
        처리된 오디오 데이터
    """
    rack = BassRack(preset=preset)
    
    # 시드 값이 들어오면 랜덤 모드로 동작 (Data Augmentation)
    if seed is not None:
        rack.randomize_parameters(seed=seed)
        
    return rack.process(audio, sample_rate)