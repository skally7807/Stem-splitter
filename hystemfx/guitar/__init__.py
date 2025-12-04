# guitar/__init__.py

'''
from guitar import FX_Distortion, FX_Reverb
이렇게 import 할 수 있음
'''
from .effects import (
    FX_Compressor,
    FX_Distortion,
    FX_Chorus,
    FX_Delay,
    FX_Reverb,
    FX_Gain,
    FX_NoiseGate,
    FX_HighPass,
    FX_LowPass,
    FX_Limiter,
    FX_Phaser,
    GuitarEffectsChain
)
from pedalboard import Pedalboard

__all__ = [
    "FX_Compressor",
    "FX_Distortion",
    "FX_Chorus",
    "FX_Delay",
    "FX_Reverb",
    "FX_Gain",
    "FX_NoiseGate",
    "FX_HighPass",
    "FX_LowPass",
    "FX_Limiter",
    "FX_Phaser",
    "GuitarEffectsChain",
    "get_default_chain"
]

def get_default_chain():
    """
    Guitar 세션용 기본 이펙트 체인 반환
    """
    chain = [
        FX_NoiseGate(threshold_db=-60),
        FX_Compressor(threshold_db=-10, ratio=3.0),
        FX_Distortion(drive_db=10.0),
        FX_Reverb(room_size=0.3, wet_level=0.2),
        FX_Gain(gain_db=0.0),
        FX_Limiter(threshold_db=-1.0)
    ]
    
    # Wrapper에서 실제 device 객체만 추출하여 Pedalboard 구성
    return Pedalboard([fx.get_device() for fx in chain])