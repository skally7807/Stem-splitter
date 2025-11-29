from pedalboard import (
    Compressor, Distortion, 
    Chorus, Delay, Reverb, Gain, NoiseGate
)
from core.effect_block import EffectBlock

class FX_Compressor(EffectBlock):
    name = "guitar_compressor"

    def __init__(self, threshold_db=-15, ratio=4.0):
        super().__init__()
        self.device = Compressor(
            threshold_db=threshold_db, 
            ratio=ratio,
            attack_ms=5.0,
            release_ms=50.0
        )

class FX_Distortion(EffectBlock):
    name = "guitar_distortion"

    def __init__(self, drive_db=25.0):
        super().__init__()
        self.device = Distortion(drive_db=drive_db)

class FX_Chorus(EffectBlock):
    name = "guitar_chorus"

    def __init__(self, rate_hz=1.0, depth=0.25, mix=0.3):
        super().__init__()
        self.device = Chorus(
            rate_hz=rate_hz, 
            depth=depth, 
            centre_delay_ms=7.0, 
            mix=mix
        )

class FX_Delay(EffectBlock):
    name = "guitar_delay"

    def __init__(self, delay_seconds=0.5, feedback=0.2, mix=0.3):
        super().__init__()
        self.device = Delay(
            delay_seconds=delay_seconds, 
            feedback=feedback, 
            mix=mix
        )

class FX_Reverb(EffectBlock):
    name = "guitar_reverb"

    def __init__(self, room_size=0.5, damping=0.5, wet_level=0.33, dry_level=0.4):
        super().__init__()
        self.device = Reverb(
            room_size=room_size, 
            damping=damping, 
            wet_level=wet_level, 
            dry_level=dry_level
        )

class FX_Gain(EffectBlock):
    name = "guitar_gain"

    def __init__(self, gain_db=0.0):
        super().__init__()
        self.device = Gain(gain_db=gain_db)

class FX_NoiseGate(EffectBlock):
    name = "guitar_noisegate"

    def __init__(self, threshold_db=-50, ratio=10, release_ms=100):
        super().__init__()
        self.device = NoiseGate(
            threshold_db=threshold_db, 
            ratio=ratio, 
            release_ms=release_ms
        )