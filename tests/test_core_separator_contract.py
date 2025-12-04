import os
import unittest
import tempfile
from pathlib import Path

import numpy as np
import soundfile as sf

from hystemfx.core.separator import DemucsSeparator


def create_short_dummy_wav(path: str, sr: int = 44100, duration_sec: float = 0.5):
    """
    테스트용 짧은 스테레오 WAV 생성 (약 0.5초)
    shape: (T, 2)
    """
    t = np.linspace(0, duration_sec, int(sr * duration_sec), endpoint=False)
    left = 0.5 * np.sin(2 * np.pi * 440 * t)   # 440 Hz
    right = 0.5 * np.sin(2 * np.pi * 330 * t)  # 330 Hz
    audio = np.stack([left, right], axis=1)    # (T, 2)
    sf.write(path, audio, sr)


class TestCoreSeparatorContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # 테스트 전체에서 Demucs 한 번만 로드 (느려서)
        cls.separator = DemucsSeparator(device="cpu")

    def test_separate_file_core_api_contract(self):
        # ---------------------------
        # 1. 짧은 테스트 파일 생성
        # ---------------------------
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            wav_path = tmpdir / "dummy_mix.wav"
            create_short_dummy_wav(str(wav_path), sr=44100, duration_sec=0.5)

            # ---------------------------
            # 2. core API 호출
            # ---------------------------
            stems = self.separator.separate_file(str(wav_path))

        # ---------------------------
        # 3. dict & key 계약 테스트
        # ---------------------------
        self.assertIsInstance(stems, dict, "separate_file는 dict를 반환해야 합니다.")

        required_keys = {"vocals", "guitar", "bass", "piano"}
        missing = required_keys - stems.keys()
        self.assertFalse(
            missing,
            f"stem dict에 필요한 키가 없습니다: {missing}",
        )

        # ---------------------------
        # 4. 각 stem shape == (C, T) 확인
        # ---------------------------
        for name in required_keys:
            audio = stems[name]

            self.assertIsInstance(
                audio, np.ndarray, f"{name} stem은 np.ndarray 여야 합니다."
            )
            self.assertEqual(
                audio.ndim, 2, f"{name} stem은 2D (C, T)여야 합니다. 현재: {audio.shape}"
            )

            C, T = audio.shape
            # 채널 수는 1 이상, 길이는 0보다 커야 함
            self.assertGreaterEqual(C, 1, f"{name} stem 채널 수가 1 미만입니다: C={C}")
            self.assertGreater(T, 0, f"{name} stem 길이가 0입니다.")

            # (C, T) 계약이므로 보통 T가 C보다 훨씬 커야 함
            self.assertGreater(
                T, C,
                f"{name} stem에서 T(샘플 수)가 C(채널 수)보다 작거나 같음: shape={audio.shape}",
            )

        # ---------------------------
        # 5. 샘플레이트 계약 테스트 (44100)
        # ---------------------------
        self.assertEqual(
            self.separator.sample_rate,
            44100,
            f"DemucsSeparator.sample_rate는 44100이어야 합니다. 현재: {self.separator.sample_rate}",
        )


if __name__ == "__main__":
    unittest.main()
