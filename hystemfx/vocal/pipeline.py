import os
import sys
import soundfile as sf
import torch
import numpy as np

# =================================================================
# [경로 설정]
# =================================================================
current_file_path = os.path.abspath(__file__)
# .../Project/hystemfx/vocal/pipeline.py -> .../Project
root_path = os.path.dirname(os.path.dirname(os.path.dirname(current_file_path)))
if root_path not in sys.path:
    sys.path.append(root_path)

from hystemfx.core.separator import DemucsSeparator      # core 분리기
from hystemfx.vocal.effects import VocalRack             # 보컬 이펙트 체인


class VocalPipeline:
    """
    Vocal Stem 분리(Demucs) + 보컬 이펙트 체인(Pedalboard) 파이프라인
    """

    def __init__(self, device: str | None = None):
        # Demucs 실행 디바이스
        self.device = device if device else ("cuda" if torch.cuda.is_available() else "cpu")

        # Demucs Separator 초기화
        try:
            self.separator = DemucsSeparator(device=self.device)
            print(f"[VocalPipeline] DemucsSeparator 로드 성공 (device={self.device})")
        except Exception as e:
            print(f"[VocalPipeline] DemucsSeparator 초기화 실패: {e}")
            self.separator = None

        # Vocal FX Rack 초기화
        self.fx_rack = VocalRack()

    def process_file(
        self,
        input_path: str,
        output_path: str,
        preset: str = "default",
        seed: int | None = None,
    ) -> None:
        """
        1) 입력 파일에서 보컬 stem 추출 (Demucs)
        2) 보컬 이펙트 체인 적용
        3) 결과를 output_path 에 저장
        """
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"File not found: {input_path}")

        print(f"▶ Vocal Processing: {input_path} (Preset: {preset})")

        raw_vocal = None
        sr = 44100  # fallback 기본 sr

        # -------------------------------------------------
        # 1. Demucs로 보컬 stem 추출 시도
        # -------------------------------------------------
        if self.separator is not None:
            try:
        # core.load_audio 대신 soundfile로 직접 읽기
                audio, sr = sf.read(input_path)
        # audio shape 정리: (T,), (T, C), (C, T) 어떤 경우든 Demucs가 기대하는 (C, T)로 맞춤
                if audio.ndim == 1:
            # mono: (T,) -> (1, T)
                    audio = audio[np.newaxis, :]
                elif audio.ndim == 2 :
            # (T, C) -> (C, T)
                    audio = audio.T

                print("  → audio 로드 완료, Demucs stem 분리 시도...")


        # Demucs 메모리 분리기 사용
                stems = self.separator.separate_memory(audio, shifts=0)

                if isinstance(stems, dict) and "vocals" in stems:
                    raw_vocal = stems["vocals"]
                    sr = self.separator.sample_rate  # Demucs 모델 샘플레이트
                    print("  ✓ Vocal stem 추출 완료 (Demucs)")
                else:
                    print("  ✗ 'vocals' stem 을 찾을 수 없음. 원본 사용으로 fallback.")

            except Exception as e:
                print(f"  ✗ Demucs 분리 중 에러 발생: {e}")


        # -------------------------------------------------
        # 2. 분리 실패 시, 입력 파일 전체를 보컬로 간주 (fallback)
        # -------------------------------------------------
        if raw_vocal is None:
            print("  → fallback: 입력 파일을 그대로 보컬 소스로 사용합니다.")
            raw_vocal, sr = sf.read(input_path)

            # (T,) -> (1, T)
            if raw_vocal.ndim == 1:
                raw_vocal = raw_vocal[np.newaxis, :]

            # (T, C) 형태면 (C, T)로 변경
            if raw_vocal.ndim == 2 and raw_vocal.shape[0] < raw_vocal.shape[1]:
                raw_vocal = raw_vocal.T

        # -------------------------------------------------
        # 3. Vocal FX Rack 설정 (preset + randomize)
        # -------------------------------------------------
        self.fx_rack.load_preset(preset)

        if seed is not None:
            self.fx_rack.randomize_parameters(seed)

        # -------------------------------------------------
        # 4. 이펙트 체인 적용
        # -------------------------------------------------
        processed = self.fx_rack.process(raw_vocal, sr)

        # (C, T) → (T, C) 로 바꿔서 저장
        if processed.ndim == 2 and processed.shape[0] < processed.shape[1]:
            processed_to_write = processed.T
        else:
            processed_to_write = processed

        sf.write(output_path, processed_to_write, sr)
        print(f"  ✓ 결과 저장: {output_path}")


