import numpy as np
import random
from typing import Optional, Dict

from pedalboard import (
    Pedalboard,
    NoiseGate,
    HighpassFilter,
    Compressor,
    PeakFilter,
    Distortion,
    Reverb,
    Limiter,
)


class VocalRack:
    """
    Vocal Processing Rack

    보컬용 이펙트 체인 (README 명세 기반):

    1. Noise Gate        - 백그라운드 노이즈 제거
    2. High-pass Filter  - 저역 럼블 제거
    3. De-esser (EQ 컷)  - 5~7kHz 치찰음 제어
    4. Compressor        - 다이내믹 컨트롤
    5. Parametric EQ     - Presence / Air 부스트
    6. Saturation        - 약한 하모닉스 추가
    7. Reverb            - 공간감
    8. Limiter           - 피크 제어
    """

    # =================================================================
    # 기본 설정값 (README 테이블 기반)
    # =================================================================
    DEFAULT_CONFIG = {
        # 1. Noise Gate
        "noise_gate_threshold_db": -60.0,
        "noise_gate_ratio": 10.0,
        "noise_gate_attack_ms": 5.0,
        "noise_gate_release_ms": 50.0,
        # 2. High-pass Filter
        "highpass_cutoff_hz": 90.0,  # 80~100Hz 사이
        # 3. De-esser (EQ 컷으로 근사)
        "deesser_freq_hz": 6000.0,
        "deesser_cut_db": -4.0,
        "deesser_q": 3.0,
        # 4. Compressor
        "comp_threshold_db": -18.0,
        "comp_ratio": 3.5,
        "comp_attack_ms": 8.0,
        "comp_release_ms": 60.0,
        # 5. EQ (Presence & Air)
        "eq_presence_freq_hz": 3000.0,
        "eq_presence_gain_db": 12.0,
        "eq_presence_q": 1.0,
        "eq_air_freq_hz": 10000.0,
        "eq_air_gain_db": 12.0,
        "eq_air_q": 0.7,
        # 6. Saturation
        "saturation_drive_db": 4.5,
        "saturation_mix": 0.3,
        # 7. Reverb
        "reverb_room_size": 0.28,
        "reverb_damping": 0.5,
        "reverb_wet_level": 0.2,
        "reverb_dry_level": 0.8,
        "reverb_width": 1.0,
        "reverb_pre_delay_ms": 20.0,
        "reverb_freeze_mode": 0.0,
        # 8. Limiter
        "limiter_threshold_db": -1.0,
    }

    def __init__(self, preset: str = "default", verbose: bool = False):
        self.verbose = verbose
        if self.verbose:
            print(f"[VocalRack] Initializing with preset: '{preset}'")

        self.current_settings = self.DEFAULT_CONFIG.copy()
        self.board: Optional[Pedalboard] = None

        if preset != "default":
            self.load_preset(preset)
        else:
            self._build_board()

    # =================================================================
    # 보드 빌드
    # =================================================================
    def _build_board(self) -> None:
        s = self.current_settings
        effects_list = []

        # 1. Noise Gate
        effects_list.append(
            NoiseGate(
                threshold_db=s["noise_gate_threshold_db"],
                ratio=s["noise_gate_ratio"],
                attack_ms=s["noise_gate_attack_ms"],
                release_ms=s["noise_gate_release_ms"],
            )
        )

        # 2. High-pass Filter
        effects_list.append(
            HighpassFilter(
                cutoff_frequency_hz=s["highpass_cutoff_hz"],
            )
        )

        # 3. De-esser 역할: 6kHz 근처를 컷하는 PeakFilter
        effects_list.append(
            PeakFilter(
                cutoff_frequency_hz=s["deesser_freq_hz"],
                gain_db=s["deesser_cut_db"],  # 마이너스 → 치찰음 억제
                q=s["deesser_q"],
            )
        )

        # 4. Compressor
        effects_list.append(
            Compressor(
                threshold_db=s["comp_threshold_db"],
                ratio=s["comp_ratio"],
                attack_ms=s["comp_attack_ms"],
                release_ms=s["comp_release_ms"],
            )
        )

        # 5. Parametric EQ (Presence / Air)
        effects_list.append(
            PeakFilter(
                cutoff_frequency_hz=s["eq_presence_freq_hz"],
                gain_db=s["eq_presence_gain_db"],
                q=s["eq_presence_q"],
            )
        )
        effects_list.append(
            PeakFilter(
                cutoff_frequency_hz=s["eq_air_freq_hz"],
                gain_db=s["eq_air_gain_db"],
                q=s["eq_air_q"],
            )
        )

        # 6. Saturation (Distortion)
        effects_list.append(
            Distortion(
                drive_db=s["saturation_drive_db"],
               
            )
        )

        # 7. Reverb
        effects_list.append(
            Reverb(
                room_size=s["reverb_room_size"],
                damping=s["reverb_damping"],
                wet_level=s["reverb_wet_level"],
                dry_level=s["reverb_dry_level"],
                width=s["reverb_width"],
                freeze_mode=s["reverb_freeze_mode"],
            )
        )

        # 8. Limiter
        effects_list.append(
            Limiter(
                threshold_db=s["limiter_threshold_db"],
            )
        )

        self.board = Pedalboard(effects_list)

        if self.verbose:
            print("[VocalRack] Effect chain rebuilt successfully.")

    # =================================================================
    # 처리 메서드
    # =================================================================
    def process(self, audio: np.ndarray, sample_rate: int) -> np.ndarray:
        if self.board is None:
            self._build_board()

        input_audio = audio.copy()

        # (T,) -> (1, T)
        if input_audio.ndim == 1:
            input_audio = input_audio[np.newaxis, :]

        transposed = False
        # (C, T)가 아니라 (T, C)이면 transpose
        if input_audio.shape[0] > input_audio.shape[1]:
            input_audio = input_audio.T
            transposed = True

        processed_audio = self.board(input_audio, sample_rate)

        if transposed:
            processed_audio = processed_audio.T

        return processed_audio

    # =================================================================
    # Preset / Randomize
    # =================================================================
    def load_preset(self, preset_name: str) -> "VocalRack":
        updates = {}

        if preset_name == "default":
            self.current_settings = self.DEFAULT_CONFIG.copy()

        elif preset_name == "bright":
            # 고역/프레즌스 강조
            updates = {
                "eq_presence_gain_db": 10.0,
                "eq_air_gain_db": 14.0,
                "highpass_cutoff_hz": 100.0,
            }

        elif preset_name == "warm":
            # 고역을 줄이고 저역 약간 보강
            updates = {
                "eq_presence_gain_db": 6.0,
                "eq_air_gain_db": 6.0,
                "highpass_cutoff_hz": 70.0,
                "saturation_drive_db": 3.0,
            }

        elif preset_name == "roomy":
            # 리버브 양을 늘린 공간감 프리셋
            updates = {
                "reverb_room_size": 0.4,
                "reverb_wet_level": 0.28,
            }

        else:
            print(f"[VocalRack] Unknown preset '{preset_name}'. default 로 로드합니다.")
            self.current_settings = self.DEFAULT_CONFIG.copy()

        if updates:
            self.current_settings.update(updates)

        self._build_board()
        return self

    def randomize_parameters(self, seed: Optional[int] = None) -> "VocalRack":
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)

        ranges = {
            # README에 언급된 랜덤화 예시 반영
            "comp_threshold_db": (-24.0, -12.0),
            "reverb_room_size": (0.2, 0.5),
            "saturation_drive_db": (3.0, 6.0),
            "reverb_wet_level": (0.15, 0.3),
            "eq_presence_gain_db": (8.0, 14.0),
            "eq_air_gain_db": (8.0, 14.0),
        }

        random_updates = {}
        for key, (lo, hi) in ranges.items():
            random_updates[key] = random.uniform(lo, hi)

        self.current_settings.update(random_updates)
        self._build_board()
        return self

    def get_current_settings(self) -> Dict[str, float]:
        """현재 적용된 파라미터 값 반환 (로깅/저장용)"""
        return self.current_settings.copy()


# =============================================================================
# Helper Function
# =============================================================================
def apply_vocal_effects(
    audio: np.ndarray,
    sample_rate: int,
    preset: str = "default",
    seed: Optional[int] = None,
) -> np.ndarray:
    """
    외부에서 VocalRack 클래스를 직접 인스턴스화하지 않고
    함수 호출 한 번으로 이펙트를 적용할 수 있는 래퍼 함수.
    """
    rack = VocalRack(preset=preset)

    if seed is not None:
        rack.randomize_parameters(seed=seed)

    return rack.process(audio, sample_rate)
