from pedalboard import (
    Compressor, Distortion, 
    Chorus, Delay, Reverb, Gain, NoiseGate,
    LowpassFilter, HighpassFilter,
    Limiter, Phaser, Pedalboard
)
from hystemfx.core.effect_block import EffectBlock
import numpy as np

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
        
class FX_HighPass(EffectBlock):
    name = "high_pass_filter"
    
    def __init__(self, cutoff_hz=100.0):
        super().__init__()
        """
        특정 주파수 아래 깎아냄
        :param cutoff_hz: threshold 주파수
        """
        self.device = HighpassFilter(cutoff_frequency_hz=cutoff_hz)
        
class FX_LowPass(EffectBlock):
    name = "low_pass_filter"
    
    def __init__(self, cutoff_hz=10000.0):
        super().__init__()
        """
        특정 주파수 위 깎아냄.
        :param cutoff_hz: threshold 주파수
        """
        self.device = LowpassFilter(cutoff_frequency_hz=cutoff_hz)
        
class FX_Limiter(EffectBlock):
    name = "guitar_limiter"

    def __init__(self, threshold_db=-1.0, release_ms=100.0):
        """
        지정된 볼륨(threshold_db)을 넘지 않게 눌러줌.

        :param threshold_db: 제한할 데시벨 기준값 (예: -1.0)
        :param release_ms: 신호가 줄어들 때 리미터가 풀리는 시간 (ms)
        """
        super().__init__()
        self.device = Limiter(threshold_db=threshold_db, release_ms=release_ms)

class FX_Phaser(EffectBlock):
    name = "guitar_phaser"

    def __init__(self, rate_hz=1.0, depth=0.5, feedback=0.5, mix=0.5):
        """
        Phaser임
        
        :param rate_hz: 변조 속도 (Hz)
        :param depth: 변조 깊이 (0.0 ~ 1.0)
        :param feedback: 피드백 양 (0.0 ~ 1.0)
        :param mix: 원음과 효과음의 혼합 비율 (0.0 ~ 1.0)
        """
        super().__init__()
        self.device = Phaser(
            rate_hz=rate_hz, 
            depth=depth, 
            feedback=feedback, 
            mix=mix,
            centre_frequency_hz=1300
        )

class GuitarEffectsChain:
    """
    Guitar Effects Chain
    
    Presets:
    - clean: Compressor -> Chorus -> Reverb
    - distortion: NoiseGate -> Distortion -> Reverb
    - crunch: Compressor -> Mild Distortion -> Reverb
    """
    def __init__(self, preset="clean", custom_board=None, **kwargs):
        self.preset = preset
        self.params = kwargs
        self.board = custom_board
        
        if self.board is None:
            self._build_board()

    def _build_board(self):
        effects = []
        
        if self.preset == "clean":
            # Clean: Compressor -> Chorus -> Reverb
            comp_thresh = self.params.get("comp_threshold_db", -15.0)
            chorus_rate = self.params.get("chorus_rate_hz", 1.0)
            reverb_size = self.params.get("reverb_room_size", 0.4)
            
            effects.append(FX_Compressor(threshold_db=comp_thresh).device)
            effects.append(FX_Chorus(rate_hz=chorus_rate).device)
            effects.append(FX_Reverb(room_size=reverb_size).device)
            
        elif self.preset == "distortion":
            # Distortion: NoiseGate -> Distortion -> Reverb
            gate_thresh = self.params.get("gate_threshold_db", -50.0)
            drive = self.params.get("drive_db", 30.0)
            reverb_size = self.params.get("reverb_room_size", 0.3)
            
            effects.append(FX_NoiseGate(threshold_db=gate_thresh).device)
            effects.append(FX_Distortion(drive_db=drive).device)
            effects.append(FX_Reverb(room_size=reverb_size).device)
            
        elif self.preset == "crunch":
            # Crunch: Compressor -> Mild Distortion -> Reverb
            comp_thresh = self.params.get("comp_threshold_db", -20.0)
            drive = self.params.get("drive_db", 15.0)
            reverb_size = self.params.get("reverb_room_size", 0.3)
            
            effects.append(FX_Compressor(threshold_db=comp_thresh).device)
            effects.append(FX_Distortion(drive_db=drive).device)
            effects.append(FX_Reverb(room_size=reverb_size).device)
            
        else:
            # Default to clean if unknown
            print(f"[GuitarEffectsChain] Unknown preset '{self.preset}'. Using clean.")
            effects.append(FX_Compressor().device)
            effects.append(FX_Reverb().device)

        self.board = Pedalboard(effects)

    def process(self, audio: np.ndarray, sample_rate: int) -> np.ndarray:
        if self.board is None:
            self._build_board()
            
        input_audio = audio.copy()
        
        # Ensure (C, T) -> (C, T) for Pedalboard (it handles channels well usually, 
        # but let's stick to standard checks if needed. Pedalboard expects (C, T) or (T, C) depending on version/usage.
        # Our other classes handle transpose. Let's do similar safety.
        
        # If input is (T,), make it (1, T)
        if input_audio.ndim == 1:
            input_audio = input_audio[np.newaxis, :]
            
        # Check shape. If (T, C) where T > C, transpose to (C, T) for consistency with other modules if they prefer that,
        # OR just pass to pedalboard. Pedalboard.__call__ takes (channels, samples).
        # So if we have (samples, channels), we must transpose.
        transposed = False
        if input_audio.shape[0] > input_audio.shape[1]: 
             input_audio = input_audio.T
             transposed = True
             
        processed = self.board(input_audio, sample_rate)
        
        if transposed:
            processed = processed.T
            
        return processed

    def get_settings(self):
        return {
            "preset": self.preset if self.preset else "custom",
            **self.params
        }