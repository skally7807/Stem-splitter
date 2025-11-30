import os
import sys

current_file_path = os.path.abspath(__file__)

root_path = os.path.dirname(os.path.dirname(os.path.dirname(current_file_path)))

sys.path.append(root_path)
# =================================================================
from hystemfx.bass.pipeline import BassPipeline

def main():
    INPUT_FILE = "test_input.mp3"
    OUTPUT_FILE = "bass_result.wav"
    PRESET = "modern"

    input_full_path = os.path.join(root_path, INPUT_FILE)
    output_full_path = os.path.join(root_path, OUTPUT_FILE)

    if not os.path.exists(input_full_path):
        print(f"파일을 찾을 수 없습니다: {input_full_path}")
        return

    try:
        print(f" 시작 (Preset: {PRESET})")
        pipeline = BassPipeline()
        
        pipeline.process_file(
            input_path=input_full_path,
            output_path=output_full_path,
            preset=PRESET
        )
        
        print(f" 결과 파일: {output_full_path}")

    except Exception as e:
        print(f"에러 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()