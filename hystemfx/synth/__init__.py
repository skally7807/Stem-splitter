"""
Synth/Piano/Keyboard Module
신디사이저, 피아노, 키보드 분리 및 이펙트 처리 모듈

이 모듈은 Spotify의 Pedalboard와 Meta의 Demucs를 활용하여
대중가요에서 신디사이저, 피아노, 키보드 성분을 분리하고
전문적인 이펙트 체인을 적용합니다.
"""

from .separator import SynthSeparator, separate_synth
from .effects import (
    SynthEffectsChain,
    RandomizedSynthEffects,
    apply_synth_effects
)
from .pipeline import SynthPipeline, process_synth_from_mix

__all__ = [
    # Separator
    'SynthSeparator',
    'separate_synth',
    
    # Effects
    'SynthEffectsChain',
    'RandomizedSynthEffects',
    'apply_synth_effects',
    
    # Pipeline
    'SynthPipeline',
    'process_synth_from_mix',
]
