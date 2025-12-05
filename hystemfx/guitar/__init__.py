from .effects import GuitarEffectsChain
from .separator import GuitarSeparator, separate_guitar
from .pipeline import GuitarPipeline, process_guitar_from_mix
from pedalboard import Pedalboard, NoiseGate, Compressor, Distortion, Reverb, Gain, Limiter

__all__ = [
    "GuitarEffectsChain",
    "get_default_chain",
    "GuitarSeparator",
    "separate_guitar",
    "GuitarPipeline",
    "process_guitar_from_mix"
]

def get_default_chain():
    """
    Guitar 세션용 기본 이펙트 체인 반환
    """
    return Pedalboard([
        NoiseGate(threshold_db=-60),
        Compressor(threshold_db=-10, ratio=3.0),
        Distortion(drive_db=10.0),
        Reverb(room_size=0.3, wet_level=0.2),
        Gain(gain_db=0.0),
        Limiter(threshold_db=-1.0)
    ])