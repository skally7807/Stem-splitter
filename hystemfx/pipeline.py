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
    단일 스템 파일에 이펙트를 적용하여 저장함.
    
    이미 분리된 오디오 파일(Stem)을 입력으로 받아, 해당 세션 타입에 맞는 이펙트 체인을 적용함.
    
    :param input_path: 입력 스템 파일 경로
    :param output_path: 처리된 파일을 저장할 경로
    :param session_type: 세션 타입 ('vocals', 'guitar', 'piano', 'bass')
    :param preset: 이펙트 프리셋 이름 또는 커스텀 이펙트 객체
    :param sr: 샘플 레이트 (기본값: 44100)
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
    전체 오디오 처리 파이프라인을 실행함 (Master Pipeline).
    
    1. 입력 오디오를 로드하고 Demucs를 사용하여 각 악기(Stem)로 분리함.
    2. 분리된 원본 스템(Raw Stems)을 저장함.
    3. 각 스템에 대해 설정된 프리셋을 사용하여 이펙트를 적용함 (In-Memory).
    4. 이펙트가 적용된 스템(Processed Stems)을 저장함.
    
    :param input_path: 입력 오디오 파일 경로 (믹스 파일)
    :param device: 연산 장치 ('cuda' 또는 'cpu'). None일 경우 자동 감지.
    :param output_dir: 결과 파일을 저장할 디렉토리 경로
    :param vocal_preset: 보컬 이펙트 프리셋 이름
    :param synth_preset: 신디사이저/피아노 이펙트 프리셋 이름
    :param guitar_preset: 기타 이펙트 프리셋 이름
    :param bass_preset: 베이스 이펙트 프리셋 이름
    
    :return: 저장된 파일 경로들의 딕셔너리 (Key: 식별자, Value: 파일 경로)
    :raises FileNotFoundError: 입력 파일이 없을 경우
    :raises RuntimeError: 오디오 로드, 분리, 또는 처리 중 오류 발생 시
    """
    input_path = Path(input_path)
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    output_dir = Path(output_dir)
    separated_dir = output_dir / "separated"
    processed_dir = output_dir / "processed"
    
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"> Starting Pipeline for: {input_path.name}")

    # 1. Initialize
    device = device or ("cuda" if torch.cuda.is_available() else "cpu")
    print(f"- Device: {device}")

    try:
        separator = DemucsSeparator(device=device)
    except Exception as e:
        raise RuntimeError(f"Failed to initialize DemucsSeparator: {e}")

    # 2. Load Audio
    print("- Loading audio...")
    try:
        audio, sr = load_audio(input_path, sr=separator.sample_rate)
    except Exception as e:
        raise RuntimeError(f"Failed to load audio: {e}")

    # 3. Separation
    print("- Separating stems...")
    try:
        stems = separator.separate_memory(audio, shifts=0)
    except Exception as e:
        raise RuntimeError(f"Separation failed: {e}")

    # Filter stems
    allowed_stems = {"vocals", "guitar", "bass", "piano"}
    stems = {k: v for k, v in stems.items() if k in allowed_stems}

    saved_files = {}

    # 4. Processing & Saving
    print("- Processing and saving stems...")

    # Initialize Session Pipelines (for effect processing only)
    # We use the pipelines just for their effect chains if possible, 
    # or we can use the effect classes directly. 
    # Using effect classes directly is more efficient here since we already have the separated stems.
    
    from hystemfx.vocal.effects import VocalRack
    from hystemfx.synth.effects import SynthEffectsChain
    from hystemfx.guitar.effects import GuitarEffectsChain
    from hystemfx.bass.effects import BassRack

    for stem_name, stem_audio in stems.items():
        # A. Save Raw Stem
        raw_save_path = separated_dir / f"{stem_name}.wav"
        
        stem_to_save = stem_audio
        if stem_to_save.ndim == 2:
            stem_to_save = stem_to_save.T
            
        save_audio(stem_to_save, raw_save_path, sr=sr)
        saved_files[f"{stem_name}_raw"] = str(raw_save_path)
        print(f"  ✓ Saved raw {stem_name}")

        # B. Apply Effects (In-Memory)
        processed_audio = None
        
        try:
            if stem_name == "vocals":
                print(f"  > Processing Vocals (Preset: {vocal_preset})...")
                rack = VocalRack(preset=vocal_preset)
                processed_audio = rack.process(stem_audio, sr)

            elif stem_name == "piano":
                print(f"  > Processing Synth/Piano (Preset: {synth_preset})...")
                # Synth logic matching pipeline
                chain_params = {}
                if synth_preset == "bright":
                    chain_params = {"eq_mid_gain_db": 3.0, "eq_high_gain_db": 2.5, "chorus_mix": 0.4}
                elif synth_preset == "warm":
                    chain_params = {"eq_low_gain_db": 1.5, "eq_mid_gain_db": 1.0, "eq_high_gain_db": -1.0}
                
                chain = SynthEffectsChain(**chain_params)
                processed_audio = chain.process(stem_audio, sr)

            elif stem_name == "guitar":
                print(f"  > Processing Guitar (Preset: {guitar_preset if isinstance(guitar_preset, str) else 'Custom'})...")
                if isinstance(guitar_preset, str):
                    chain = GuitarEffectsChain(preset=guitar_preset)
                else:
                    chain = GuitarEffectsChain(custom_board=guitar_preset)
                processed_audio = chain.process(stem_audio, sr)
            
            elif stem_name == "bass":
                print(f"  > Processing Bass (Preset: {bass_preset})...")
                rack = BassRack(preset=bass_preset)
                processed_audio = rack.process(stem_audio, sr)
                
        except Exception as e:
            print(f"  ✗ Processing failed for {stem_name}: {e}")

        # C. Save Processed Stem
        if processed_audio is not None:
            proc_save_path = processed_dir / f"{stem_name}_processed.wav"
            
            proc_to_save = processed_audio
            if proc_to_save.ndim == 2 and proc_to_save.shape[0] < proc_to_save.shape[1]:
                 proc_to_save = proc_to_save.T
            
            save_audio(proc_to_save, proc_save_path, sr=sr)
            saved_files[f"{stem_name}_processed"] = str(proc_save_path)
            print(f"  ✓ Saved processed {stem_name}")

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
