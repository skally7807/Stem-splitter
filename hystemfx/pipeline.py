import os
import sys
import torch
import numpy as np
from pathlib import Path
from typing import Dict, Optional, Union

# Add project root to sys.path if needed
current_file_path = os.path.abspath(__file__)
root_path = os.path.dirname(os.path.dirname(current_file_path))
if root_path not in sys.path:
    sys.path.append(root_path)

from hystemfx.core.separator import DemucsSeparator
from hystemfx.core.io import load_audio, save_audio
from hystemfx.vocal.effects import VocalRack
from hystemfx.synth.effects import SynthEffectsChain
from hystemfx.guitar.effects import GuitarEffectsChain
from hystemfx.bass.effects import BassRack

def process_stem(
    input_path: str,
    output_path: str,
    session_type: str,
    preset: Union[str, object] = "default",
    sr: int = 44100
) -> None:
    """
    Process a single stem file with effects.
    
    Args:
        input_path (str): Path to input stem file
        output_path (str): Path to save processed file
        session_type (str): 'vocals', 'guitar', 'piano', etc.
        preset (str or object): Preset name or custom effect object
        sr (int): Sample rate
    """
    print(f"- Processing stem: {session_type} ({input_path})")
    
    # Load audio
    try:
        audio, _ = load_audio(input_path, sr=sr)
    except Exception as e:
        print(f"X Failed to load stem: {e}")
        return

    # Apply Effects
    processed_audio = None
    
    try:
        if session_type == "vocals":
            rack = VocalRack(preset=preset)
            processed_audio = rack.process(audio, sr)
            
        elif session_type == "piano":
            # Handle synth preset logic
            chain_params = {}
            if isinstance(preset, str):
                if preset == "bright":
                    chain_params = {"eq_mid_gain_db": 3.0, "eq_high_gain_db": 2.5, "chorus_mix": 0.4}
                elif preset == "warm":
                    chain_params = {"eq_low_gain_db": 1.5, "eq_mid_gain_db": 1.0, "eq_high_gain_db": -1.0}
                chain = SynthEffectsChain(**chain_params)
            else:
                # Assume custom object if supported, or just default
                chain = SynthEffectsChain()
                
            processed_audio = chain.process(audio, sr)
            
        elif session_type == "guitar":
            if isinstance(preset, str):
                chain = GuitarEffectsChain(preset=preset)
            else:
                chain = GuitarEffectsChain(custom_board=preset)
            processed_audio = chain.process(audio, sr)
            
        # Add other sessions if needed
        
    except Exception as e:
        print(f"X Processing failed for {session_type}: {e}")
        return

    # Save
    if processed_audio is not None:
        # Transpose if needed (C, T) -> (T, C) for saving
        if processed_audio.ndim == 2 and processed_audio.shape[0] < processed_audio.shape[1]:
             processed_audio = processed_audio.T
             
        save_audio(processed_audio, output_path, sr=sr)
        print(f"V Saved processed stem to {output_path}")


def run_pipeline(
    input_path: str,
    device: Optional[str] = None,
    output_dir: str = "output",
    vocal_preset: str = "default",
    synth_preset: str = "default",
    guitar_preset: Union[str, object] = "clean",
    bass_preset: str = "default"
) -> Dict[str, str]:
    """
    Run the full audio processing pipeline:
    1. Separate audio into stems.
    2. Save raw stems.
    3. Apply effects to specific stems in memory.
    4. Save processed stems.
    
    Args:
        input_path (str): Path to the input audio file.
        device (str, optional): 'cuda' or 'cpu'. Defaults to auto-detect.
        output_dir (str): Directory to save output files.
        vocal_preset (str): Preset name for vocal effects.
        synth_preset (str): Preset name for synth/piano effects.
        guitar_preset (str): Preset name for guitar effects.
        bass_preset (str): Preset name for bass effects.
    
    Returns:
        Dict[str, str]: Map of saved file paths.
    """
    input_path = Path(input_path)
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    output_dir = Path(output_dir)
    separated_dir = output_dir / "separated"
    processed_dir = output_dir / "processed"
    
    # Directories are created by save_audio if needed, but good to have base
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"> Starting Pipeline for: {input_path.name}")

    # 1. Initialize
    device = device or ("cuda" if torch.cuda.is_available() else "cpu")
    print(f"- Device: {device}")

    try:
        separator = DemucsSeparator(device=device)
    except Exception as e:
        raise RuntimeError(f"Failed to initialize DemucsSeparator: {e}")

    # 2. Load Audio (using core.io)
    print("- Loading audio...")
    # DemucsSeparator handles loading internally via separate_file, 
    # OR we load here and pass to separate_memory.
    # Let's load here to control I/O explicitly as requested.
    try:
        audio, sr = load_audio(input_path, sr=separator.sample_rate)
    except Exception as e:
        raise RuntimeError(f"Failed to load audio: {e}")

    # 3. Separation
    print("- Separating stems...")
    try:
        # separate_memory returns: {'vocals': array, 'drums': array, ...}
        # Arrays are (C, T)
        stems = separator.separate_memory(audio, shifts=0)
    except Exception as e:
        raise RuntimeError(f"Separation failed: {e}")

    # Filter stems
    allowed_stems = {"vocals", "guitar", "bass", "piano"}
    stems = {k: v for k, v in stems.items() if k in allowed_stems}

    saved_files = {}

    # 4. Processing & Saving
    print("- Processing and saving stems...")

    for stem_name, stem_audio in stems.items():
        # A. Save Raw Stem
        raw_save_path = separated_dir / f"{stem_name}.wav"
        
        # Prepare for saving: (C, T) -> (T, C)
        stem_to_save = stem_audio
        if stem_to_save.ndim == 2:
            stem_to_save = stem_to_save.T
            
        save_audio(stem_to_save, raw_save_path, sr=sr)
        saved_files[f"{stem_name}_raw"] = str(raw_save_path)
        print(f"V Saved raw {stem_name}")

        # B. Apply Effects (In-Memory)
        processed_audio = None
        
        # Pass (C, T) to effects, they handle it.
        # Note: Our effects classes expect (C, T) usually, or handle transpose.
        
        if stem_name == "vocals":
            print(f"> Applying Vocal Effects (Preset: {vocal_preset})...")
            try:
                rack = VocalRack(preset=vocal_preset)
                processed_audio = rack.process(stem_audio, sr)
            except Exception as e:
                print(f"X Vocal processing failed: {e}")

        elif stem_name == "piano":
            print(f">Applying Synth/Piano Effects (Preset: {synth_preset})...")
            try:
                chain_params = {}
                if synth_preset == "bright":
                    chain_params = {"eq_mid_gain_db": 3.0, "eq_high_gain_db": 2.5, "chorus_mix": 0.4}
                elif synth_preset == "warm":
                    chain_params = {"eq_low_gain_db": 1.5, "eq_mid_gain_db": 1.0, "eq_high_gain_db": -1.0}
                
                chain = SynthEffectsChain(**chain_params)
                processed_audio = chain.process(stem_audio, sr)
            except Exception as e:
                print(f"X Synth processing failed: {e}")

        elif stem_name == "guitar":
            print(f">Applying Guitar Effects (Preset: {guitar_preset if isinstance(guitar_preset, str) else 'Custom'})...")
            try:
                if isinstance(guitar_preset, str):
                    chain = GuitarEffectsChain(preset=guitar_preset)
                else:
                    chain = GuitarEffectsChain(custom_board=guitar_preset)
                processed_audio = chain.process(stem_audio, sr)
            except Exception as e:
                print(f"X Guitar processing failed: {e}")
        
        # Bass is allowed but no effects logic defined in original pipeline, 
        # so we just skip processing for bass unless added.
        # (User didn't explicitly ask to add bass effects logic here, just "processing")
        # But we should probably save it as processed if we had effects. 
        # For now, if no effects, we don't save a "processed" version or just copy raw?
        # Requirement: "8 outputs (4 raw + 4 processed)". 
        # So we MUST produce a processed file for bass too, even if it's just raw or default effects.
        
        elif stem_name == "bass":
            print(f">Applying Bass Effects (Preset: {bass_preset})...")
            try:
                rack = BassRack(preset=bass_preset)
                processed_audio = rack.process(stem_audio, sr)
                
                # Log Bass Effects Settings
                settings = rack.get_current_settings()
                print(f"      [Bass Effects Settings]")
                for k, v in settings.items():
                    print(f"        - {k}: {v}")
                    
            except Exception as e:
                print(f"    ✗ Bass processing failed: {e}")

        # C. Save Processed Stem
        if processed_audio is not None:
            proc_save_path = processed_dir / f"{stem_name}_processed.wav"
            
            # Prepare for saving: (C, T) -> (T, C)
            proc_to_save = processed_audio
            if proc_to_save.ndim == 2 and proc_to_save.shape[0] < proc_to_save.shape[1]:
                 proc_to_save = proc_to_save.T
            
            save_audio(proc_to_save, proc_save_path, sr=sr)
            saved_files[f"{stem_name}_processed"] = str(proc_save_path)
            print(f"Saved processed {stem_name}")
        else:
             # If 8 files are strictly required, we might want to save raw as processed if no effect applied?
             # But "processed" implies processing. If failed or no effect, maybe skip.
             # User said "separation from effecting to save 8 files". 
             # I'll assume if bass has effects (which I added), we get 8.
             pass

    print("Pipeline Completed.")
    return saved_files

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python pipeline.py <input_audio_path> [output_dir]")
        sys.exit(1)

    in_path = sys.argv[1]
    out_dir = sys.argv[2] if len(sys.argv) > 2 else "output"
    
    try:
        run_pipeline(in_path, output_dir=out_dir)
    except Exception as e:
        print(f"Error: {e}")
