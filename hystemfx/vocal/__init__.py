"""
Vocal Module
보컬 전용 이펙트 모듈
"""

from .effects import VocalRack, apply_vocal_effects
from .separator import VocalSeparator, separate_vocal
from .pipeline import VocalPipeline, process_vocal_from_mix

__all__ = [
    "VocalRack",
    "apply_vocal_effects",
    "VocalSeparator",
    "separate_vocal",
    "VocalPipeline",
    "process_vocal_from_mix"
]
