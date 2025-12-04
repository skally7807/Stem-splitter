import os
import sys
import numpy as np
import soundfile as sf
from pathlib import Path

# Add project root to sys.path
current_file_path = os.path.abspath(__file__)
root_path = os.path.dirname(os.path.dirname(current_file_path))
if root_path not in sys.path:
    sys.path.append(root_path)

from hystemfx.pipeline import run_pipeline

def create_dummy_audio(path, duration=5.0, sr=44100):
    t = np.linspace(0, duration, int(sr * duration))
    # Create a simple mix of frequencies to simulate "instruments"
    # 440Hz (A4) - Vocals
    # 110Hz (A2) - Bass
    # 880Hz (A5) - Synth
    audio = 0.5 * np.sin(2 * np.pi * 440 * t) + \
            0.3 * np.sin(2 * np.pi * 110 * t) + \
            0.2 * np.sin(2 * np.pi * 880 * t)
    
    # Make it stereo
    audio_stereo = np.stack([audio, audio], axis=1)
    
    sf.write(path, audio_stereo, sr)
    print(f"Created dummy audio at {path}")

def test_pipeline():
    test_dir = Path("test_output")
    test_dir.mkdir(exist_ok=True)
    
    input_audio = Path("mixed.wav").resolve()
    if not input_audio.exists():
        # Fallback to checking parent dir if running from subfolder or similar, 
        # but user said "root mixed.wav". 
        # Let's assume script is in root or we look in root.
        # The script is in root/verify_pipeline.py based on file path.
        # So mixed.wav should be in the same dir.
        # Wait, user said "root mixed.wav".
        pass

    output_dir = test_dir / "pipeline_results"
    
    # create_dummy_audio(str(input_audio)) # User wants to use real mixed.wav
    
    print("\n--- Running Pipeline Test ---")
    try:
        # Use CPU for testing to avoid CUDA issues if not available/configured
        results = run_pipeline(
            str(input_audio), 
            output_dir=str(output_dir),
            device="cpu" 
        )
        
        print("\n--- Verification ---")
        expected_stems = ["vocals", "bass", "guitar", "piano"]
        
        all_passed = True
        
        # Check raw stems
        for stem in expected_stems:
            key = f"{stem}_raw"
            if key in results and os.path.exists(results[key]):
                print(f"[PASS] Raw stem found: {stem}")
            else:
                print(f"[FAIL] Raw stem missing: {stem}")
                all_passed = False
                
        # Check processed stems (vocals, piano, guitar)
        for stem in ["vocals", "piano", "guitar"]:
            key = f"{stem}_processed"
            if key in results and os.path.exists(results[key]):
                print(f"[PASS] Processed stem found: {stem}")
            else:
                print(f"[FAIL] Processed stem missing: {stem}")
                all_passed = False
                
        if all_passed:
            print("\n>>> TEST PASSED: All expected files were created.")
        else:
            print("\n>>> TEST FAILED: Some files are missing.")
            
    except Exception as e:
        print(f"\n>>> TEST FAILED with Exception: {e}")
        import traceback
        traceback.print_exc()

class Logger(object):
    def __init__(self):
        self.terminal = sys.stdout
        self.log = open("pipeline_log.txt", "w", encoding="utf-8")

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)

    def flush(self):
        self.terminal.flush()
        self.log.flush()

if __name__ == "__main__":
    sys.stdout = Logger()
    test_pipeline()
