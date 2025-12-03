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
    1. Noise Gate: 노이즈 및 아티팩트 제거 (Compressor를 high ratio로 사용)
    2. High-pass Filter: 저역 럼블 제거
    3. Compressor: 다이내믹 레인지 균일화
    4. EQ (Parametric): 주요 주파수 대역 강조
    5. Chorus: 스테레오 이미지 확장 및 공간감
    6. Reverb: 자연스러운 앰비언스 추가
    7. Limiter: 최종 출력 레벨 제한
    
    Note: Noise Gate는 Compressor를 high ratio(10:1)로 설정하여 구현합니다.
          이는 threshold 이하의 신호를 효과적으로 감쇠시켜 노이즈를 제거합니다.
    """
    
    def __init__(
        self,
        # Noise Gate parameters (Compressor를 high ratio로 사용)
        gate_threshold_db: float = -60.0,   # dB threshold: 이 값 이하는 노이즈로 간주
        gate_ratio: float = 10.0,            # 10:1 압축으로 강력한 게이팅 효과
        gate_attack_ms: float = 1.0,         # 빠른 attack으로 피아노 음의 트랜지언트 보존
        gate_release_ms: float = 100.0,      # 자연스러운 감쇠를 위한 release
        
        # High-pass Filter parameters
        highpass_cutoff_hz: float = 80.0,    # 80Hz 이하의 저역 럼블 제거
        
        # Compressor parameters (다이내믹 레인지 제어용)
        comp_threshold_db: float = -20.0,    # -20dB 이상에서 압축 시작
        comp_ratio: float = 3.0,             # 3:1 압축 비율
        comp_attack_ms: float = 5.0,         # 빠른 attack으로 피크 제어
        comp_release_ms: float = 50.0,       # 자연스러운 release
        
        # EQ parameters (mid-range boost for piano/keys)
        eq_low_gain_db: float = 0.0,         # ~200Hz: 저음역 풀바디감
        eq_mid_gain_db: float = 2.0,         # ~1.5kHz: 음의 존재감(presence)
        eq_high_gain_db: float = 1.0,        # ~8kHz: 밝기(brightness)와 명료도
        
        # Chorus parameters
        chorus_rate_hz: float = 0.8,         # LFO 속도: 0.8Hz의 느린 변조
        chorus_depth: float = 0.25,          # 변조 깊이: 0.0(off)~1.0(max)
        chorus_centre_delay_ms: float = 7.0, # 기본 딜레이 시간
        chorus_feedback: float = 0.0,        # 피드백: 0.0(no feedback)
        chorus_mix: float = 0.3,             # Dry/Wet mix: 0.3 = 30% wet
        
        # Reverb parameters
        reverb_room_size: float = 0.35,      # Room size: 0.0(small)~1.0(large)
        reverb_damping: float = 0.5,         # 고주파 감쇠: 0.0(bright)~1.0(dark)
        reverb_wet_level: float = 0.25,      # Wet level: reverb 신호 레벨
        reverb_dry_level: float = 0.8,       # Dry level: 원본 신호 레벨
        reverb_width: float = 1.0,           # Stereo width: 0.0(mono)~1.0(wide)
        
        # Limiter parameters
        limiter_threshold_db: float = -1.0,  # -1dB에서 리미팅 시작
        limiter_release_ms: float = 100.0    # Release time
    ):
        """
        신디사이저/피아노/키보드 이펙트 체인 초기화
        
        Noise Gate Parameters:
            gate_threshold_db: 
                - 노이즈 게이트 임계값 (dB)
                - 낮을수록 더 많은 신호 통과 (예: -70dB는 미세한 노이즈까지 보존)
                - 높을수록 더 적극적인 노이즈 제거 (예: -50dB는 강력한 노이즈 제거)
                - 권장값: -60dB ~ -70dB (피아노), -50dB ~ -60dB (신디 리드)
                
            gate_ratio: 
                - 압축 비율 (threshold 이하 신호를 얼마나 감쇠시킬지)
                - 10:1 = threshold 이하 신호를 1/10로 감쇠
                - 높을수록 강력한 게이팅 (10 이상 권장)
                
            gate_attack_ms: 
                - Attack time (ms) - 신호가 threshold를 넘을 때 게이트가 열리는 속도
                - 빠를수록 (0.1~2ms) 음의 attack이 명확함 (피아노 타건음)
                - 느릴수록 (5~10ms) 부드러운 페이드인
                - 피아노: 0.5~1ms, Pad 신디: 5~10ms 권장
                
            gate_release_ms: 
                - Release time (ms) - 신호가 threshold 아래로 떨어질 때 게이트가 닫히는 속도
                - 빠를수록 (10~50ms) 짧은 음에 적합하지만 노이즈가 끊김
                - 느릴수록 (100~300ms) 자연스러운 감쇠, 피아노 페달 효과
                - 피아노: 100~200ms, 신디 리드: 50~100ms 권장
        
        High-pass Filter Parameters:
            highpass_cutoff_hz: 
                - High-pass filter cutoff frequency (Hz)
                - 이 주파수 이하를 제거 (저역 럼블, 바람 소리 등)
                - 피아노: 80Hz, 신디: 60~100Hz
        
        Compressor Parameters:
            comp_threshold_db: Compressor threshold (dB)
            comp_ratio: Compressor ratio - 높을수록 강한 압축
            comp_attack_ms: Compressor attack time (ms)
            comp_release_ms: Compressor release time (ms)
        
        EQ Parameters:
            eq_low_gain_db: Low frequency gain (200Hz 부근) - 풀바디감
            eq_mid_gain_db: Mid frequency gain (1.5kHz) - 음의 존재감
            eq_high_gain_db: High frequency gain (8kHz) - 밝기와 명료도
        
        Chorus Parameters:
            chorus_rate_hz: Chorus LFO rate (Hz) - 변조 속도
            chorus_depth: Chorus depth (0.0-1.0) - 변조 깊이
            chorus_centre_delay_ms: Chorus center delay (ms)
            chorus_feedback: Chorus feedback
            chorus_mix: Chorus dry/wet mix (0.0=dry, 1.0=wet)
        
        Reverb Parameters:
            reverb_room_size: Reverb room size (0.0-1.0)
            reverb_damping: Reverb damping - 고주파 감쇠
            reverb_wet_level: Reverb wet level
            reverb_dry_level: Reverb dry level
            reverb_width: Reverb stereo width
        
        Limiter Parameters:
            limiter_threshold_db: Limiter threshold (dB)
            limiter_release_ms: Limiter release time (ms)
        
        Examples:
            >>> # 기본 설정으로 체인 생성
            >>> chain = SynthEffectsChain()
            
            >>> # 피아노 전용 설정
            >>> piano_chain = SynthEffectsChain(
            ...     gate_threshold_db=-65.0,
            ...     gate_attack_ms=0.5,
            ...     gate_release_ms=150.0,
            ...     eq_mid_gain_db=3.0
            ... )
            
            >>> # 신디 리드 전용 설정 (타이트한 사운드)
            >>> lead_chain = SynthEffectsChain(
            ...     gate_threshold_db=-55.0,
            ...     gate_ratio=12.0,
            ...     gate_release_ms=50.0,
            ...     comp_ratio=4.0,
            ...     reverb_room_size=0.2
            ... )
            
            >>> # 신디 패드 전용 설정 (공간감 있는 사운드)
            >>> pad_chain = SynthEffectsChain(
            ...     gate_threshold_db=-70.0,
            ...     gate_attack_ms=10.0,
            ...     gate_release_ms=200.0,
            ...     chorus_mix=0.5,
            ...     reverb_room_size=0.6,
            ...     reverb_wet_level=0.4
            ... )
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
            # 1. Noise Gate (Compressor를 high ratio로 사용하여 구현)
            #    - threshold 이하의 신호를 10:1 비율로 감쇠
            #    - 분리 후 남은 노이즈와 아티팩트를 효과적으로 제거
            Compressor(
                threshold_db=gate_threshold_db,
                ratio=gate_ratio,
                attack_ms=gate_attack_ms,
                release_ms=gate_release_ms
            ),
            
            # 2. High-pass Filter (저역 럼블 제거)
            #    - 80Hz 이하의 불필요한 저음역 제거
            #    - 분리 과정에서 생긴 저역 아티팩트 감소
            HighpassFilter(cutoff_frequency_hz=highpass_cutoff_hz),
            
            # 3. Compressor (다이내믹 레인지 균일화)
            #    - 피아노/신디 음량을 일정하게 유지
            #    - 3:1 압축으로 자연스러운 다이내믹스 보존
            Compressor(
                threshold_db=comp_threshold_db,
                ratio=comp_ratio,
                attack_ms=comp_attack_ms,
                release_ms=comp_release_ms
            ),
            
            # 4. EQ - Low Shelf (200Hz 부근)
            #    - 저음역 풀바디감 조절
            LowShelfFilter(
                cutoff_frequency_hz=200.0,
                gain_db=eq_low_gain_db,
                q=0.707
            ),
            
            # 5. EQ - Mid Peak (1.5kHz - presence)
            #    - 음의 존재감(presence) 강조
            #    - 믹스에서 피아노/신디가 잘 들리도록
            PeakFilter(
                cutoff_frequency_hz=1500.0,
                gain_db=eq_mid_gain_db,
                q=1.0
            ),
            
            # 6. EQ - High Shelf (8kHz - brightness)
            #    - 밝기(brightness)와 명료도 향상
            HighShelfFilter(
                cutoff_frequency_hz=8000.0,
                gain_db=eq_high_gain_db,
                q=0.707
            ),
            
            # 7. Chorus (스테레오 이미지 확장)
            #    - 0.8Hz의 느린 LFO로 자연스러운 변조
            #    - 30% wet mix로 미묘한 두께감 추가
            Chorus(
                rate_hz=chorus_rate_hz,
                depth=chorus_depth,
                centre_delay_ms=chorus_centre_delay_ms,
                feedback=chorus_feedback,
                mix=chorus_mix
            ),
            
            # 8. Reverb (공간감)
            #    - 작은 룸 사이즈로 자연스러운 앰비언스
            #    - 피아노/신디에 공간감 부여
            Reverb(
                room_size=reverb_room_size,
                damping=reverb_damping,
                wet_level=reverb_wet_level,
                dry_level=reverb_dry_level,
                width=reverb_width
            ),
            
            # 9. Limiter (출력 레벨 제한)
            #    - -1dB에서 리미팅하여 클리핑 방지
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
        preset (str): 프리셋 이름 (\"default\", \"bright\", \"warm\", \"spacious\")
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
