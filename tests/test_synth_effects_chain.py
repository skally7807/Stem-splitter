import unittest
from pathlib import Path
import numpy as np

from hystemfx.synth.effects import (
    SynthEffectsChain,
    RandomizedSynthEffects,
    apply_synth_effects,
)


def make_dummy_audio(sr=44100, duration=0.5, channels=2):
    """
    간단한 더미 오디오 생성 (C, T)
    """
    T = int(sr * duration)
    t = np.linspace(0, duration, T, endpoint=False)

    left = 0.2 * np.sin(2 * np.pi * 440 * t)
    if channels == 1:
        audio = left.astype("float32")[np.newaxis, :]
    else:
        right = 0.2 * np.sin(2 * np.pi * 220 * t)
        audio = np.stack([left, right], axis=0).astype("float32")  # (2, T)
    return audio, sr


class TestSynthEffectsChainBasic(unittest.TestCase):
    def test_process_keeps_shape_stereo(self):
        audio, sr = make_dummy_audio(channels=2)
        chain = SynthEffectsChain()
        out = chain.process(audio, sr)

        self.assertEqual(
            out.shape, audio.shape,
            f"출력 shape가 입력과 다릅니다: {out.shape} != {audio.shape}",
        )
        self.assertTrue(np.isfinite(out).all(), "출력에 NaN/inf가 포함되어 있습니다.")

    def test_process_accepts_mono_1d(self):
        # (T,) mono 입력도 잘 처리되는지
        audio, sr = make_dummy_audio(channels=1)
        audio_1d = audio[0]  # (T,)
        chain = SynthEffectsChain()
        out = chain.process(audio_1d, sr)

        # 내부에서 (1, T)로 바꾸기 때문에 출력은 (1, T) 기대
        self.assertEqual(out.ndim, 2)
        self.assertEqual(out.shape[0], 1)
        self.assertTrue(np.isfinite(out).all())

    def test_process_accepts_TxC(self):
        # (T, C) 형식도 잘 처리하는지 (transpose 로직)
        audio, sr = make_dummy_audio(channels=2)  # (2, T)
        audio_TxC = audio.T  # (T, 2)
        chain = SynthEffectsChain()
        out = chain.process(audio_TxC, sr)

        # 결과는 pedalboard 내부 기준으로 (C, T)일 가능성이 높음
        self.assertEqual(out.ndim, 2)
        self.assertTrue(np.isfinite(out).all())


class TestSynthEffectsPresets(unittest.TestCase):
    def test_apply_synth_effects_all_presets(self):
        audio, sr = make_dummy_audio()

        presets = ["default", "bright", "warm", "spacious", "tight"]
        outputs = {}

        for p in presets:
            with self.subTest(preset=p):
                out = apply_synth_effects(audio, sr, preset=p)
                self.assertEqual(out.shape, audio.shape)
                self.assertTrue(np.isfinite(out).all())
                outputs[p] = out

        # preset 변경 시 출력이 모두 완전히 같은지 정도는 확인
        # (완전히 같으면 preset 의미가 약함)
        all_same = True
        ref = outputs["default"]
        for p, out in outputs.items():
            if not np.allclose(ref, out, atol=1e-6):
                all_same = False
                break

        self.assertFalse(
            all_same,
            "모든 preset 출력이 거의 동일합니다. preset 효과가 없는 것 같습니다.",
        )



if __name__ == "__main__":
    unittest.main()
