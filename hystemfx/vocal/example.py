import os
import sys

# =================================================================
# [경로 설정]
# =================================================================
current_file_path = os.path.abspath(__file__)
root_path = os.path.dirname(os.path.dirname(os.path.dirname(current_file_path)))
if root_path not in sys.path:
    sys.path.append(root_path)

from hystemfx.vocal.pipeline import VocalPipeline


def main():
    # 루트 기준 파일 경로 정의
    INPUT_FILE = "data/test.mp3"   # 너가 원하는 이름으로 바꿔
    OUTPUT_FILE = "vocal_result.wav"
    PRESET = "default"   # "bright", "air", "roomy" 등 바꿔도 됨
    SEED = None          # 랜덤 증강 쓰고 싶으면 아무 정수

    input_full_path = os.path.join(root_path, INPUT_FILE)
    output_full_path = os.path.join(root_path, OUTPUT_FILE)

    if not os.path.exists(input_full_path):
        print(f"[VocalExample] 파일을 찾을 수 없습니다: {input_full_path}")
        return

    try:
        print(f"[VocalExample] 시작 (Preset: {PRESET}, Seed: {SEED})")
        pipeline = VocalPipeline()

        pipeline.process_file(
            input_path=input_full_path,
            output_path=output_full_path,
            preset=PRESET,
            seed=SEED,
        )

        print(f"[VocalExample] 결과 파일: {output_full_path}")

    except Exception as e:
        print(f"[VocalExample] 에러 발생: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()

