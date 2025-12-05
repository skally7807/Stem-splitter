import unittest
import numpy as np

from hystemfx.vocal.effects import VocalRack
from hystemfx.bass.effects import BassRack
# synth/guitar 쪽도 FX 클래스가 있으면 여기에 import 추가


def make_dummy_audio(sr=44100, duration=0.5, channels=2):
    """
    간단한 테스트용 더미 오디오 생성.
    shape: (C, T)  (2채널 사인파)
    """
    T = int(sr * duration)
    t = np.linspace(0, duration, T, endpoint=False)

    left = 0.2 * np.sin(2 * np.pi * 440 * t)
    right = 0.2 * np.sin(2 * np.pi * 220 * t)

    audio = np.stack([left, right], axis=0).astype("float32")  # (2, T)
    return audio, sr


class TestDeterminismVocal(unittest.TestCase):
    def test_vocal_same_seed_gives_same_output(self):
        audio, sr = make_dummy_audio()

        rack1 = VocalRack(preset="default", verbose=False)
        rack2 = VocalRack(preset="default", verbose=False)

        # 같은 seed로 랜덤 파라미터 설정
        rack1.randomize_parameters(seed=0)
        rack2.randomize_parameters(seed=0)

        out1 = rack1.process(audio, sr)
        out2 = rack2.process(audio, sr)

        self.assertTrue(
            np.allclose(out1, out2, atol=1e-6),
            "같은 seed인데 VocalRack 출력이 다릅니다."
        )

    def test_vocal_different_seed_gives_different_output(self):
        audio, sr = make_dummy_audio()

        rack1 = VocalRack(preset="default", verbose=False)
        rack2 = VocalRack(preset="default", verbose=False)

        rack1.randomize_parameters(seed=0)
        rack2.randomize_parameters(seed=1)

        out1 = rack1.process(audio, sr)
        out2 = rack2.process(audio, sr)

        # 완전히 같지는 않아야 함 (완전 동일하면 이상)
        self.assertFalse(
            np.allclose(out1, out2, atol=1e-6),
            "다른 seed인데 VocalRack 출력이 지나치게 동일합니다."
        )


class TestDeterminismBass(unittest.TestCase):
    def test_bass_same_seed_gives_same_output(self):
        audio, sr = make_dummy_audio()

        rack1 = BassRack(preset="default", verbose=False)
        rack2 = BassRack(preset="default", verbose=False)

        rack1.randomize_parameters(seed=123)
        rack2.randomize_parameters(seed=123)

        out1 = rack1.process(audio, sr)
        out2 = rack2.process(audio, sr)

        self.assertTrue(
            np.allclose(out1, out2, atol=1e-6),
            "같은 seed인데 BassRack 출력이 다릅니다."
        )


        # 필요하면 여기서도 다른 seed → 다른 출력 테스트 추가 가능


# Synth / Guitar FX도 비슷한 패턴으로 테스트 클래스 추가하면 됨.
# class TestDeterminismSynth(unittest.TestCase):
#     ...


if __name__ == "__main__":
    unittest.main()
