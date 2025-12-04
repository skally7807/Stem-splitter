from pedalboard import (
    Compressor, Distortion, 
    Chorus, Delay, Reverb, Gain, NoiseGate,
    LowpassFilter, HighpassFilter,
    Limiter, Phaser, Pedalboard
)
import numpy as np
from typing import Dict, Optional

class GuitarEffectsChain:
    """
    Guitar Effects Chain
    
    Presets:
    - clean: Compressor -> Chorus -> Reverb
    - distortion: NoiseGate -> Distortion -> Reverb
    - crunch: Compressor -> Mild Distortion -> Reverb
    """
    
    DEFAULT_CONFIG = {
        # Clean Preset Defaults
        "clean_comp_threshold": -15.0,
        "clean_chorus_rate": 1.0,
        "clean_reverb_size": 0.4,
        
        # Distortion Preset Defaults
        "dist_gate_threshold": -50.0,
        "dist_drive": 30.0,
        "dist_reverb_size": 0.3,
        
        # Crunch Preset Defaults
        "crunch_comp_threshold": -20.0,
        "crunch_drive": 15.0,
        "crunch_reverb_size": 0.3
    }

    def __init__(self, preset="clean", custom_board=None, **kwargs):
        self.preset = preset
        self.params = kwargs
        self.board = custom_board
        
        # Merge defaults with provided params if needed, 
        # but here we just use kwargs directly or fallback to defaults in _build_board
        
        if self.board is None:
            self._build_board()

    def _build_board(self):
        effects = []
        
        if self.preset == "clean":
            # Clean: Compressor -> Chorus -> Reverb
            comp_thresh = self.params.get("comp_threshold_db", -15.0)
            chorus_rate = self.params.get("chorus_rate_hz", 1.0)
            reverb_size = self.params.get("reverb_room_size", 0.4)
            
            effects.append(Compressor(threshold_db=comp_thresh, ratio=4.0, attack_ms=5.0, release_ms=50.0))
            effects.append(Chorus(rate_hz=chorus_rate, depth=0.25, centre_delay_ms=7.0, mix=0.3))
            effects.append(Reverb(room_size=reverb_size, damping=0.5, wet_level=0.33, dry_level=0.4))
            
        elif self.preset == "distortion":
            # Distortion: NoiseGate -> Distortion -> Reverb
            gate_thresh = self.params.get("gate_threshold_db", -50.0)
            drive = self.params.get("drive_db", 30.0)
            reverb_size = self.params.get("reverb_room_size", 0.3)
            
            effects.append(NoiseGate(threshold_db=gate_thresh, ratio=10, release_ms=100))
            effects.append(Distortion(drive_db=drive))
            effects.append(Reverb(room_size=reverb_size, damping=0.5, wet_level=0.33, dry_level=0.4))
            
        elif self.preset == "crunch":
            # Crunch: Compressor -> Mild Distortion -> Reverb
            comp_thresh = self.params.get("comp_threshold_db", -20.0)
            drive = self.params.get("drive_db", 15.0)
            reverb_size = self.params.get("reverb_room_size", 0.3)
            
            effects.append(Compressor(threshold_db=comp_thresh, ratio=4.0))
            effects.append(Distortion(drive_db=drive))
            effects.append(Reverb(room_size=reverb_size, damping=0.5, wet_level=0.33, dry_level=0.4))
            
        else:
            # Default to clean if unknown
            print(f"[GuitarEffectsChain] Unknown preset '{self.preset}'. Using clean.")
            effects.append(Compressor())
            effects.append(Reverb())

        self.board = Pedalboard(effects)

    def process(self, audio: np.ndarray, sample_rate: int) -> np.ndarray:
        if self.board is None:
            self._build_board()
            
        input_audio = audio.copy()
        
        # If input is (T,), make it (1, T)
        if input_audio.ndim == 1:
            input_audio = input_audio[np.newaxis, :]
            
        # Check shape. If (T, C) where T > C, transpose to (C, T)
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