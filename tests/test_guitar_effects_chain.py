# tests/test_guitar_effects_chain.py

import unittest
import numpy as np

from hystemfx.guitar.effects import GuitarEffectsChain

class TestGuitarEffectsChain(unittest.TestCase):
    def setUp(self):
        # 1초짜리 stereo dummy 오디오 (C, T)
        self.sr = 44100
        self.audio = np.random.uniform(
            low=-0.5, high=0.5, size=(2, self.sr)
        ).astype(np.float32)

    # ---------------------------------------------------------
    # 1) 기본 preset 별로 에러 없이 처리되는지
    # ---------------------------------------------------------
    def test_clean_preset_processes_audio(self):
        chain = GuitarEffectsChain(preset="clean")
        out = chain.process(self.audio, self.sr)

        # shape 유지 확인
        self.assertIsInstance(out, np.ndarray)
        self.assertEqual(out.shape, self.audio.shape)

    def test_distortion_preset_processes_audio(self):
        chain = GuitarEffectsChain(preset="distortion")
        out = chain.process(self.audio, self.sr)

        self.assertIsInstance(out, np.ndarray)
        self.assertEqual(out.shape, self.audio.shape)

    def test_crunch_preset_processes_audio(self):
        chain = GuitarEffectsChain(preset="crunch")
        out = chain.process(self.audio, self.sr)

        self.assertIsInstance(out, np.ndarray)
        self.assertEqual(out.shape, self.audio.shape)

    # ---------------------------------------------------------
    # 2) (T,), (T, C) 형태도 잘 처리하는지
    # ---------------------------------------------------------
    def test_process_mono_1d_input(self):
        mono = np.random.uniform(-0.5, 0.5, size=(self.sr,)).astype(np.float32)
        chain = GuitarEffectsChain(preset="clean")

        out = chain.process(mono, self.sr)

        # 1D 입력 → 내부에서 (1, T)로 바꿔 처리 후 다시 (1, T) 또는 (T, 1)로 나옴
        self.assertIsInstance(out, np.ndarray)
        self.assertEqual(out.ndim, 2)

    def test_process_time_channel_input(self):
        # (T, C) 형태로 만들어보기
        tc_audio = self.audio.T  # (T, C)
        chain = GuitarEffectsChain(preset="clean")

        out = chain.process(tc_audio, self.sr)

        # 다시 (T, C) 형태로 나와야 함
        self.assertEqual(out.shape, tc_audio.shape)

    # ---------------------------------------------------------
    # 3) get_settings 동작 확인
    # ---------------------------------------------------------
    def test_get_settings_contains_preset_and_params(self):
        chain = GuitarEffectsChain(
            preset="distortion",
            drive_db=25.0,
            gate_threshold_db=-40.0,
        )
        settings = chain.get_settings()

        self.assertIn("preset", settings)
        self.assertEqual(settings["preset"], "distortion")
        self.assertIn("drive_db", settings)
        self.assertEqual(settings["drive_db"], 25.0)
        self.assertIn("gate_threshold_db", settings)
        self.assertEqual(settings["gate_threshold_db"], -40.0)

    # ---------------------------------------------------------
    # 4) 알 수 없는 preset → clean fallback 테스트
    # ---------------------------------------------------------
    def test_unknown_preset_fallback(self):
        # 잘못된 preset을 넣어도 에러 없이 동작해야 함
        chain = GuitarEffectsChain(preset="unknown_preset")
        out = chain.process(self.audio, self.sr)

        self.assertIsInstance(out, np.ndarray)
        self.assertEqual(out.shape, self.audio.shape)


if __name__ == "__main__":
    unittest.main()