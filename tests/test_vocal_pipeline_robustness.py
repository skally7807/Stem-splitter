import os
import unittest
import tempfile
from pathlib import Path

import numpy as np
import soundfile as sf

from hystemfx.vocal.pipeline import VocalPipeline


def make_dummy_wav(path: Path, sr=44100, duration=0.2, channels=2):
    """
    테스트용 더미 WAV 생성
    - (T, C) 형식으로 저장됨 (soundfile 기본)
    """
    T = max(1, int(sr * duration))  # duration이 매우 짧아도 최소 한 샘플

    t = np.linspace(0, duration, T, endpoint=False)
    left = 0.5 * np.sin(2 * np.pi * 440 * t)

    if channels == 1:
        audio = left.astype("float32")
    else:
        right = 0.5 * np.sin(2 * np.pi * 220 * t)
        audio = np.stack([left, right], axis=1).astype("float32")

    sf.write(str(path), audio, sr)


class TestVocalPipelineRobustness(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # CPU 고정 — unittest 환경에서 GPU 사용 비권장
        cls.pipe = VocalPipeline(device="cpu")

    # ---------------------------------------------------------
    # 1. 매우 짧은 mono 파일 (10ms)
    # ---------------------------------------------------------
    def test_very_short_mono(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            inp = td / "short_mono.wav"
            out = td / "short_mono_out.wav"

            make_dummy_wav(inp, sr=44100, duration=0.01, channels=1)

            self.pipe.process_file(str(inp), str(out))
            self.assertTrue(out.exists(), "very short mono 처리 실패")

    # ---------------------------------------------------------
    # 2. 짧은 stereo 파일
    # ---------------------------------------------------------
    def test_short_stereo(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            inp = td / "short_st.wav"
            out = td / "short_st_out.wav"

            make_dummy_wav(inp, sr=44100, duration=0.2, channels=2)

            self.pipe.process_file(str(inp), str(out))
            self.assertTrue(out.exists(), "short stereo 처리 실패")

    # ---------------------------------------------------------
    # 3. 48kHz 입력 → 44.1kHz로 자동 리샘플되는지 확인
    # ---------------------------------------------------------
    def test_resample_from_48k(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            inp = td / "48k.wav"
            out = td / "48k_out.wav"

            make_dummy_wav(inp, sr=48000, duration=0.2, channels=2)

            self.pipe.process_file(str(inp), str(out))

            self.assertTrue(out.exists(), "48kHz 파일 처리 실패")
            audio, sr = sf.read(out)
            self.assertEqual(sr, 44100, "리샘플링이 44.1kHz로 되지 않음")

    # ---------------------------------------------------------
    # 4. 22kHz 입력
    # ---------------------------------------------------------
    def test_resample_from_22k(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            inp = td / "22k.wav"
            out = td / "22k_out.wav"

            make_dummy_wav(inp, sr=22050, duration=0.2, channels=2)

            self.pipe.process_file(str(inp), str(out))

            audio, sr = sf.read(out)
            self.assertEqual(sr, 44100, "22.05kHz → 44.1kHz 리샘플 실패")

    # ---------------------------------------------------------
    # 5. 파일이 길어도(3~5초) crash 없이 처리되는지 확인 (성능 테스트 시)
    # ---------------------------------------------------------
    def test_long_file(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            inp = td / "long.wav"
            out = td / "long_out.wav"

            make_dummy_wav(inp, sr=44100, duration=3.0, channels=2)

            self.pipe.process_file(str(inp), str(out))

            self.assertTrue(out.exists(), "3초 파일 처리 실패")


if __name__ == "__main__":
    unittest.main()

