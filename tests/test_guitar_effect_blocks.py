import unittest
import numpy as np

from pedalboard import Pedalboard
from hystemfx.guitar.effects import (
    FX_Compressor, FX_Distortion, FX_Chorus, FX_Delay, FX_Reverb,
    FX_Gain, FX_NoiseGate, FX_HighPass, FX_LowPass, FX_Limiter, FX_Phaser
)


def make_dummy_audio(sr=44100, duration=0.5, channels=2):
    """
    (C, T) 형식의 더미 테스트 오디오 생성.
    """
    T = int(sr * duration)
    t = np.linspace(0, duration, T, endpoint=False)

    left = 0.2 * np.sin(2 * np.pi * 440 * t)
    right = 0.2 * np.sin(2 * np.pi * 220 * t)

    audio = np.stack([left, right], axis=0).astype("float32")  # (2, T)
    return audio, sr


class TestGuitarEffectBlocks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.audio, cls.sr = make_dummy_audio()

    # -------------------------------------------------
    # 1) 각 FX 블록이 정상적으로 생성되는지
    # -------------------------------------------------
    def test_fx_init_all(self):
        _ = FX_Compressor()
        _ = FX_Distortion()
        _ = FX_Chorus()
        _ = FX_Delay()
        _ = FX_Reverb()
        _ = FX_Gain()
        _ = FX_NoiseGate()
        _ = FX_HighPass()
        _ = FX_LowPass()
        _ = FX_Limiter()
        _ = FX_Phaser()

        # 여기서 에러 안 나면 init은 통과

    # -------------------------------------------------
    # 2) 각 FX 블록이 (C, T) 입력을 받아 크래시 없이 (C, T)로 돌려주는지
    #    (EffectBlock에 process()가 있다면 그걸 사용)
    # -------------------------------------------------
    def _check_block_preserves_shape(self, block_cls):
        fx = block_cls()
        audio_in = self.audio
        # EffectBlock이 process(audio, sr)를 제공한다고 가정
        if hasattr(fx, "process"):
            out = fx.process(audio_in, self.sr)
        else:
            # 최소한 device 직접 호출
            out = fx.device(audio_in, self.sr)

        self.assertEqual(out.shape, audio_in.shape,
                         f"{block_cls.__name__} 출력 shape가 입력과 다릅니다: {out.shape} != {audio_in.shape}")
        self.assertTrue(np.isfinite(out).all(),
                        f"{block_cls.__name__} 출력에 NaN/inf가 포함되어 있습니다.")

    def test_each_block_preserves_shape(self):
        for block_cls in [
            FX_Compressor, FX_Distortion, FX_Chorus, FX_Delay, FX_Reverb,
            FX_Gain, FX_NoiseGate, FX_HighPass, FX_LowPass, FX_Limiter, FX_Phaser
        ]:
            with self.subTest(block=block_cls.__name__):
                self._check_block_preserves_shape(block_cls)

    # -------------------------------------------------
    # 3) 간이 Guitar FX 체인 (Pedalboard)도 한 번에 테스트
    # -------------------------------------------------
    def test_guitar_chain_end_to_end(self):
        # 실제 체인 예시 (게이트 → 컴프 → 드라이브 → 하이패스 → 리미터)
        effects = [
            FX_NoiseGate().device,
            FX_Compressor().device,
            FX_Distortion().device,
            FX_HighPass().device,
            FX_Limiter().device,
        ]
        board = Pedalboard(effects)

        out = board(self.audio, self.sr)

        self.assertEqual(
            out.shape, self.audio.shape,
            f"Guitar FX 체인 출력 shape가 입력과 다릅니다: {out.shape} != {self.audio.shape}"
        )
        self.assertTrue(np.isfinite(out).all(), "Guitar FX 체인 출력에 NaN/inf가 있습니다.")

    # -------------------------------------------------
    # 4) Deterministic 여부 (랜덤 없음 확인)
    # -------------------------------------------------
    def test_deterministic_single_block(self):
        fx = FX_Distortion()  # 아무 블럭이나
        audio_in = self.audio

        out1 = fx.device(audio_in, self.sr)
        out2 = fx.device(audio_in, self.sr)

        self.assertTrue(
            np.allclose(out1, out2, atol=1e-7),
            "같은 입력에 대한 FX 출력이 run마다 다릅니다. (비결정적 동작)"
        )


if __name__ == "__main__":
    unittest.main()
