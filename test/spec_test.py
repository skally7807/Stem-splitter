# test/test_day1.py

"""
1일차 검증 스크립트
- 오디오 파일 로드
- STFT 실행
- 스펙트로그램 생성
- 이미지 1장 저장
"""

import os
from src.preprocess import load_audio, compute_spectrogram
from src.export_images import save_spectrogram

AUDIO_PATH = "data/YUDABINBAND_-_(mp3.pm) [vocals].mp3"   # <-- 테스트용 오디오 (Git에 올리지 말 것)

# 0. 출력 폴더 생성
OUTPUT_DIR = "test_output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 출력 파일 경로
OUTPUT_PATH = os.path.join(OUTPUT_DIR, "spec_test.png")

# 1. 오디오 로드
y = load_audio(AUDIO_PATH)

print("파형 크기:", y.shape)

# 2. 스펙트로그램 계산
mag = compute_spectrogram(y)
print("스펙트로그램 크기 (Freq x Time):", mag.shape)

# 3. 이미지 저장
save_spectrogram(mag, OUTPUT_PATH)
print(f"스펙트로그램 이미지 저장 완료 → {OUTPUT_PATH}")
