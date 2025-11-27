"""
Synth/Piano/Keyboard Effects Chain Module
신디사이저, 피아노, 키보드 전용 이펙트 체인

Pedalboard를 사용하여 신디사이저/피아노/키보드 사운드에
최적화된 이펙트 체인을 적용합니다.
"""

import numpy as np
from typing import Optional, Dict, Union, Tuple
from pathlib import Path
import random


class SynthEffectsChain:
    """
    신디사이저/피아노/키보드 전용 이펙트 체인
    
    이펙트 순서:
    1. Noise Gate: 노이즈 및 아티팩트 제거
    2. High-pass Filter: 저역 럼블 제거
    3. Compressor: 다이내믹 레인지 균일화
    4. EQ (Parametric): 주요 주파수 대역 강조
    5. Chorus: 스테레오 이미지 확장 및 공간감
    6. Reverb: 자연스러운 앰비언스 추가
    7. Limiter: 최종 출력 레벨 제한
    """
    
    def __init__(
        self,
        # Noise Gate parameters
        gate_threshold_db: float = -60.0,
        gate_ratio: float = 10.0,
        gate_attack_ms: float = 1.0,
        gate_release_ms: float = 100.0,
        
        # High-pass Filter parameters
        highpass_cutoff_hz: float = 80.0,
        
        # Compressor parameters
        comp_threshold_db: float = -20.0,
        comp_ratio: float = 3.0,
        comp_attack_ms: float = 5.0,
        comp_release_ms: float = 50.0,
        
        # EQ parameters (mid-range boost for piano/keys)
        eq_low_gain_db: float = 0.0,       # ~200Hz
        eq_mid_gain_db: float = 2.0,       # ~1-3kHz (presence)
        eq_high_gain_db: float = 1.0,      # ~8kHz (brightness)
        
        # Chorus parameters
        chorus_rate_hz: float = 0.8,
        chorus_depth: float = 0.25,
        chorus_centre_delay_ms: float = 7.0,
        chorus_feedback: float = 0.0,
        chorus_mix: float = 0.3,
        
        # Reverb parameters
        reverb_room_size: float = 0.35,
        reverb_damping: float = 0.5,
        reverb_wet_level: float = 0.25,
        reverb_dry_level: float = 0.8,
        reverb_width: float = 1.0,
        
        # Limiter parameters
        limiter_threshold_db: float = -1.0,
        limiter_release_ms: float = 100.0
    ):
        """
        Parameters:
            gate_threshold_db: Noise gate threshold (낮을수록 더 많은 신호 통과)
            gate_ratio: Noise gate ratio
            gate_attack_ms: Noise gate attack time
            gate_release_ms: Noise gate release time
            
            highpass_cutoff_hz: High-pass filter cutoff frequency
            
            comp_threshold_db: Compressor threshold
            comp_ratio: Compressor ratio (높을수록 강한 압축)
            comp_attack_ms: Compressor attack time
            comp_release_ms: Compressor release time
            
            eq_low_gain_db: Low frequency gain (200Hz 부근)
            eq_mid_gain_db: Mid frequency gain (1-3kHz 음의 존재감)
            eq_high_gain_db: High frequency gain (8kHz 밝기)
            
            chorus_rate_hz: Chorus LFO rate
            chorus_depth: Chorus depth (0.0-1.0)
            chorus_centre_delay_ms: Chorus center delay
            chorus_feedback: Chorus feedback
            chorus_mix: Chorus dry/wet mix (0.0=dry, 1.0=wet)
            
            reverb_room_size: Reverb room size (0.0-1.0)
            reverb_damping: Reverb damping (고주파 감쇠)
            reverb_wet_level: Reverb wet level
            reverb_dry_level: Reverb dry level
            reverb_width: Reverb stereo width
            
            limiter_threshold_db: Limiter threshold
            limiter_release_ms: Limiter release time
        """
        try:
            from pedalboard import (
                Pedalboard, Compressor, Gain, Chorus, Reverb, 
                Limiter, HighpassFilter, LowShelfFilter, 
                HighShelfFilter, PeakFilter
            )
        except ImportError:
            raise ImportError(
                "Pedalboard is not installed. Please install it with:\n"
                "pip install pedalboard"
            )
        
        # Store parameters
        self.params = {
            'gate_threshold_db': gate_threshold_db,
            'gate_ratio': gate_ratio,
            'gate_attack_ms': gate_attack_ms,
            'gate_release_ms': gate_release_ms,
            'highpass_cutoff_hz': highpass_cutoff_hz,
            'comp_threshold_db': comp_threshold_db,
            'comp_ratio': comp_ratio,
            'comp_attack_ms': comp_attack_ms,
            'comp_release_ms': comp_release_ms,
            'eq_low_gain_db': eq_low_gain_db,
            'eq_mid_gain_db': eq_mid_gain_db,
            'eq_high_gain_db': eq_high_gain_db,
            'chorus_rate_hz': chorus_rate_hz,
            'chorus_depth': chorus_depth,
            'chorus_centre_delay_ms': chorus_centre_delay_ms,
            'chorus_feedback': chorus_feedback,
            'chorus_mix': chorus_mix,
            'reverb_room_size': reverb_room_size,
            'reverb_damping': reverb_damping,
            'reverb_wet_level': reverb_wet_level,
            'reverb_dry_level': reverb_dry_level,
            'reverb_width': reverb_width,
            'limiter_threshold_db': limiter_threshold_db,
            'limiter_release_ms': limiter_release_ms,
        }
        
        # Build effect chain
        self.board = Pedalboard([
            # 1. Noise Gate (using Compressor with high ratio)
            Compressor(
                threshold_db=gate_threshold_db,
                ratio=gate_ratio,
                attack_ms=gate_attack_ms,
                release_ms=gate_release_ms
            ),
            
            # 2. High-pass Filter (저역 럼블 제거)
            HighpassFilter(cutoff_frequency_hz=highpass_cutoff_hz),
            
            # 3. Compressor (다이내믹 레인지 균일화)
            Compressor(
                threshold_db=comp_threshold_db,
                ratio=comp_ratio,
                attack_ms=comp_attack_ms,
                release_ms=comp_release_ms
            ),
            
            # 4. EQ - Low Shelf (200Hz 부근)
            LowShelfFilter(
                cutoff_frequency_hz=200.0,
                gain_db=eq_low_gain_db,
                q=0.707
            ),
            
            # 5. EQ - Mid Peak (1.5kHz - presence)
            PeakFilter(
                cutoff_frequency_hz=1500.0,
                gain_db=eq_mid_gain_db,
                q=1.0
            ),
            
            # 6. EQ - High Shelf (8kHz - brightness)
            HighShelfFilter(
                cutoff_frequency_hz=8000.0,
                gain_db=eq_high_gain_db,
                q=0.707
            ),
            
            # 7. Chorus (스테레오 이미지 확장)
            Chorus(
                rate_hz=chorus_rate_hz,
                depth=chorus_depth,
                centre_delay_ms=chorus_centre_delay_ms,
                feedback=chorus_feedback,
                mix=chorus_mix
            ),
            
            # 8. Reverb (공간감)
            Reverb(
                room_size=reverb_room_size,
                damping=reverb_damping,
                wet_level=reverb_wet_level,
                dry_level=reverb_dry_level,
                width=reverb_width
            ),
            
            # 9. Limiter (출력 레벨 제한)
            Limiter(
                threshold_db=limiter_threshold_db,
                release_ms=limiter_release_ms
            )
        ])
    
    def process(
        self, 
        audio: np.ndarray, 
        sample_rate: int,
        reset: bool = True
    ) -> np.ndarray:
        """
        오디오에 이펙트 체인 적용
        
        Parameters:
            audio (np.ndarray): 입력 오디오 [channels, samples] 또는 [samples]
            sample_rate (int): 샘플레이트
            reset (bool): 각 처리마다 이펙트 상태를 리셋할지 여부
            
        Returns:
            np.ndarray: 이펙트가 적용된 오디오
        """
        # Ensure audio is in correct shape
        if audio.ndim == 1:
            audio = audio[np.newaxis, :]
        
        # Transpose if needed: Pedalboard expects [channels, samples]
        # but if shape is [samples, channels], transpose it
        if audio.shape[0] > audio.shape[1] and audio.shape[0] > 100000:
            audio = audio.T
        
        # Apply effects
        effected = self.board(audio, sample_rate, reset=reset)
        
        return effected
    
    def get_params(self) -> Dict[str, float]:
        """현재 이펙트 파라미터 반환"""
        return self.params.copy()
    
    def update_params(self, **kwargs):
        """
        이펙트 파라미터 업데이트 및 보드 재구성
        
        Example:
            chain.update_params(
                comp_ratio=4.0,
                reverb_room_size=0.5,
                chorus_mix=0.4
            )
        """
        # Update stored parameters
        for key, value in kwargs.items():
            if key in self.params:
                self.params[key] = value
        
        # Rebuild the board with new parameters
        self.__init__(**self.params)


class RandomizedSynthEffects:
    """
    데이터 증강을 위한 랜덤화된 신디사이저 이펙트 체인
    
    각 처리마다 지정된 범위 내에서 파라미터를 무작위로 변경하여
    다양한 음향 특성을 가진 데이터를 생성합니다.
    """
    
    def __init__(
        self,
        # Parameter ranges (min, max)
        gate_threshold_range: Tuple[float, float] = (-70.0, -50.0),
        comp_ratio_range: Tuple[float, float] = (2.0, 5.0),
        comp_threshold_range: Tuple[float, float] = (-30.0, -10.0),
        eq_mid_gain_range: Tuple[float, float] = (0.0, 4.0),
        chorus_mix_range: Tuple[float, float] = (0.2, 0.5),
        reverb_room_size_range: Tuple[float, float] = (0.2, 0.5),
        reverb_wet_range: Tuple[float, float] = (0.15, 0.35),
        seed: Optional[int] = None
    ):
        """
        Parameters:
            gate_threshold_range: Noise gate threshold range (dB)
            comp_ratio_range: Compressor ratio range
            comp_threshold_range: Compressor threshold range (dB)
            eq_mid_gain_range: Mid EQ gain range (dB)
            chorus_mix_range: Chorus mix range (0.0-1.0)
            reverb_room_size_range: Reverb room size range (0.0-1.0)
            reverb_wet_range: Reverb wet level range (0.0-1.0)
            seed: Random seed for reproducibility
        """
        self.ranges = {
            'gate_threshold': gate_threshold_range,
            'comp_ratio': comp_ratio_range,
            'comp_threshold': comp_threshold_range,
            'eq_mid_gain': eq_mid_gain_range,
            'chorus_mix': chorus_mix_range,
            'reverb_room_size': reverb_room_size_range,
            'reverb_wet': reverb_wet_range,
        }
        
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)
    
    def create_random_chain(self) -> SynthEffectsChain:
        """
        랜덤 파라미터를 가진 이펙트 체인 생성
        
        Returns:
            SynthEffectsChain: 랜덤화된 이펙트 체인
        """
        params = {
            'gate_threshold_db': random.uniform(*self.ranges['gate_threshold']),
            'comp_threshold_db': random.uniform(*self.ranges['comp_threshold']),
            'comp_ratio': random.uniform(*self.ranges['comp_ratio']),
            'eq_mid_gain_db': random.uniform(*self.ranges['eq_mid_gain']),
            'chorus_mix': random.uniform(*self.ranges['chorus_mix']),
            'reverb_room_size': random.uniform(*self.ranges['reverb_room_size']),
            'reverb_wet_level': random.uniform(*self.ranges['reverb_wet']),
        }
        
        return SynthEffectsChain(**params)
    
    def process(
        self, 
        audio: np.ndarray, 
        sample_rate: int
    ) -> Tuple[np.ndarray, Dict[str, float]]:
        """
        랜덤 파라미터로 오디오 처리
        
        Parameters:
            audio (np.ndarray): 입력 오디오
            sample_rate (int): 샘플레이트
            
        Returns:
            Tuple[np.ndarray, Dict]: (처리된 오디오, 사용된 파라미터)
        """
        chain = self.create_random_chain()
        processed = chain.process(audio, sample_rate)
        return processed, chain.get_params()


def apply_synth_effects(
    audio: np.ndarray,
    sample_rate: int,
    preset: str = "default",
    **custom_params
) -> np.ndarray:
    """
    편의 함수: 신디사이저/피아노 이펙트 적용
    
    Parameters:
        audio (np.ndarray): 입력 오디오
        sample_rate (int): 샘플레이트
        preset (str): 프리셋 이름 ("default", "bright", "warm", "spacious")
        **custom_params: 커스텀 파라미터 (프리셋 오버라이드)
        
    Returns:
        np.ndarray: 이펙트가 적용된 오디오
    """
    # Preset configurations
    presets = {
        "default": {},
        
        "bright": {
            "eq_mid_gain_db": 3.0,
            "eq_high_gain_db": 2.5,
            "chorus_mix": 0.4,
        },
        
        "warm": {
            "eq_low_gain_db": 1.5,
            "eq_mid_gain_db": 1.0,
            "eq_high_gain_db": -1.0,
            "reverb_damping": 0.7,
        },
        
        "spacious": {
            "chorus_mix": 0.5,
            "chorus_depth": 0.4,
            "reverb_room_size": 0.6,
            "reverb_wet_level": 0.4,
            "reverb_width": 1.0,
        },
        
        "tight": {
            "comp_threshold_db": -25.0,
            "comp_ratio": 5.0,
            "reverb_room_size": 0.2,
            "reverb_wet_level": 0.15,
            "chorus_mix": 0.2,
        }
    }
    
    # Get preset params
    params = presets.get(preset, {})
    
    # Override with custom params
    params.update(custom_params)
    
    # Create and apply effects chain
    chain = SynthEffectsChain(**params)
    return chain.process(audio, sample_rate)