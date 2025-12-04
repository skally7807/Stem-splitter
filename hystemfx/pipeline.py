import os
import sys
import torch
import numpy as np
import soundfile as sf
from pathlib import Path
from typing import Dict, Optional, Union



# Add project root to sys.path if needed
current_file_path = os.path.abspath(__file__)
root_path = os.path.dirname(os.path.dirname(current_file_path))
if root_path not in sys.path:
    sys.path.append(root_path)

from hystemfx.core.separator import DemucsSeparator
from hystemfx.vocal.effects import VocalRack
from hystemfx.synth.effects import SynthEffectsChain
from hystemfx.guitar.effects import GuitarEffectsChain

def run_pipeline(
    input_path: str,
    device: Optional[str] = None,
    output_dir: str = "output",
    vocal_preset: str = "default",
    synth_preset: str = "default",
    guitar_preset: Union[str, object] = "clean"
) -> Dict[str, str]:
    """
    Run the full audio processing pipeline:
    1. Separate audio into stems (vocals, drums, bass, guitar, piano, other).
    2. Apply effects to specific stems (vocals, piano, guitar).
    3. Save all results to disk.

    Args:
        input_path (str): Path to the input audio file.
        device (str, optional): 'cuda' or 'cpu'. Defaults to auto-detect.
        output_dir (str): Directory to save output files.
        vocal_preset (str): Preset name for vocal effects.
        synth_preset (str): Preset name for synth/piano effects.
        guitar_preset (str): Preset name for guitar effects.

    Returns:
        Dict[str, str]: Dictionary mapping stem names to their saved file paths.
    """
    input_path = Path(input_path)
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    output_dir = Path(output_dir)
    separated_dir = output_dir / "separated"
    processed_dir = output_dir / "processed"
    
    separated_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)

    print(f"▶ Starting Pipeline for: {input_path.name}")

    # -------------------------------------------------------------------------
    # 1. Initialize Components
    # -------------------------------------------------------------------------
    device = device or ("cuda" if torch.cuda.is_available() else "cpu")
    print(f"  • Device: {device}")

    try:
        separator = DemucsSeparator(device=device)
    except Exception as e:
        raise RuntimeError(f"Failed to initialize DemucsSeparator: {e}")

    # -------------------------------------------------------------------------
    # 2. Load Audio
    # -------------------------------------------------------------------------
    print("  • Loading audio...")
    try:
        audio, sr = sf.read(str(input_path))
        # Ensure (C, T) shape for Demucs
        if audio.ndim == 1:
            audio = audio[np.newaxis, :]
        elif audio.ndim == 2:
            # If shape is (T, C), transpose to (C, T)
            if audio.shape[0] > audio.shape[1]: 
                audio = audio.T
    except Exception as e:
        raise RuntimeError(f"Failed to load audio: {e}")

    # -------------------------------------------------------------------------
    # 3. Separation
    # -------------------------------------------------------------------------
    print("  • Separating stems...")
    try:
        # separate_memory returns: {'vocals': array, 'drums': array, ...}
        # Arrays are (C, T)
        stems = separator.separate_memory(audio, shifts=0)
    except Exception as e:
        raise RuntimeError(f"Separation failed: {e}")

    # Filter stems to only keep: vocals, guitar, bass, piano
    allowed_stems = {"vocals", "guitar", "bass", "piano"}
    stems = {k: v for k, v in stems.items() if k in allowed_stems}

    saved_files = {}

    # -------------------------------------------------------------------------
    # 4. Processing & Saving
    # -------------------------------------------------------------------------
    print("  • Processing and saving stems...")

    for stem_name, stem_audio in stems.items():
        # Save raw separated stem
        raw_save_path = separated_dir / f"{stem_name}.wav"
        
        # Prepare for saving: (C, T) -> (T, C)
        stem_to_save = stem_audio
        if stem_to_save.ndim == 2:
            stem_to_save = stem_to_save.T
            
        sf.write(str(raw_save_path), stem_to_save, separator.sample_rate)
        saved_files[f"{stem_name}_raw"] = str(raw_save_path)
        print(f"    ✓ Saved raw {stem_name}")

        # Apply Effects if applicable
        processed_audio = None
        
        if stem_name == "vocals":
            print(f"    → Applying Vocal Effects (Preset: {vocal_preset})...")
            try:
                rack = VocalRack(preset=vocal_preset)
                
                # Log Vocal Effects Settings
                settings = rack.get_current_settings()
                print(f"      [Vocal Effects Settings]")
                for k, v in settings.items():
                    print(f"        - {k}: {v}")

                # VocalRack expects (C, T) or (T, C), handles internally but let's pass (C, T)
                # It returns (C, T) usually, check implementation
                processed_audio = rack.process(stem_audio, separator.sample_rate)
            except Exception as e:
                print(f"    ✗ Vocal processing failed: {e}")

        elif stem_name == "piano":
            print(f"    → Applying Synth/Piano Effects (Preset: {synth_preset})...")
            try:
                # SynthEffectsChain params need to be unpacked if using presets logic manually, 
                # or just use default/custom init. 
                # Let's use the convenience function logic or direct class init.
                # SynthEffectsChain doesn't have a 'load_preset' method like VocalRack, 
                # but 'apply_synth_effects' helper does. Let's use the helper logic or just default for now.
                # To keep it simple and consistent with the plan, we'll instantiate the chain.
                # Note: SynthEffectsChain takes kwargs for params.
                
                # Simple preset mapping (simplified from synth/effects.py)
                chain_params = {}
                if synth_preset == "bright":
                    chain_params = {"eq_mid_gain_db": 3.0, "eq_high_gain_db": 2.5, "chorus_mix": 0.4}
                elif synth_preset == "warm":
                    chain_params = {"eq_low_gain_db": 1.5, "eq_mid_gain_db": 1.0, "eq_high_gain_db": -1.0}
                
                chain = SynthEffectsChain(**chain_params)
                
                # Log Synth Effects Settings
                params = chain.get_params()
                print(f"      [Synth/Piano Effects Settings]")
                for k, v in params.items():
                    print(f"        - {k}: {v}")

                processed_audio = chain.process(stem_audio, separator.sample_rate)
            except Exception as e:
                print(f"    ✗ Synth processing failed: {e}")

        elif stem_name == "guitar":
            print(f"    → Applying Guitar Effects (Preset: {guitar_preset if isinstance(guitar_preset, str) else 'Custom'})...")
            try:
                if isinstance(guitar_preset, str):
                    chain = GuitarEffectsChain(preset=guitar_preset)
                else:
                    # Assume it's a Pedalboard object or compatible
                    chain = GuitarEffectsChain(custom_board=guitar_preset)
                
                # Log Guitar Effects Settings
                settings = chain.get_settings()
                print(f"      [Guitar Effects Settings]")
                for k, v in settings.items():
                    print(f"        - {k}: {v}")
                
                processed_audio = chain.process(stem_audio, separator.sample_rate)
            except Exception as e:
                print(f"    ✗ Guitar processing failed: {e}")

        # Save processed stem if it exists
        if processed_audio is not None:
            proc_save_path = processed_dir / f"{stem_name}_processed.wav"
            
            # Prepare for saving: (C, T) -> (T, C)
            proc_to_save = processed_audio
            if proc_to_save.ndim == 2 and proc_to_save.shape[0] < proc_to_save.shape[1]:
                 proc_to_save = proc_to_save.T
            
            sf.write(str(proc_save_path), proc_to_save, separator.sample_rate)
            saved_files[f"{stem_name}_processed"] = str(proc_save_path)
            print(f"    ✓ Saved processed {stem_name}")

    print("▶ Pipeline Completed.")
    return saved_files

if __name__ == "__main__":
    # Simple CLI for testing
    if len(sys.argv) < 2:
        print("Usage: python pipeline.py <input_audio_path> [output_dir]")
        sys.exit(1)

    in_path = sys.argv[1]
    out_dir = sys.argv[2] if len(sys.argv) > 2 else "output"
    
    try:
        run_pipeline(in_path, output_dir=out_dir)
    except Exception as e:
        print(f"Error: {e}")
