"""
vocal.postprocess

- 이펙트까지 다 먹인 보컬 오디오에 대해, "출력 직전"에 공통으로 수행하는 후처리 단계 모듈.
- 예시:
    - peak normalization
    - limiter / soft clipper
    - 약간의 EQ 정리 (하이컷, 로우컷)
    - dither 또는 페이드 인/아웃 등
- 나중에 `apply_postprocess(vocal_waveform, sr)` 같은 함수로 정리할 예정.
"""

# TODO:
# - normalize_peak(vocal_waveform, target_db=-1.0)
# - apply_limiter(vocal_waveform, threshold_db=-1.0, release_ms=50)
# - optional: highpass(HPF) / lowpass(LPF) 로 극저역/초고역 정리
# - optional: de-esser 모듈 추가 
#
# 최종적으로는:
# def apply_vocal_postprocess(vocal_waveform: np.ndarray, sr: int) -> np.ndarray:
#     """
#     1) peak normalize
#     2) limiter
#     3) 필요한 간단한 EQ
#     를 순차적으로 적용해서, "바로 믹스로 던져도 되는" 보컬 레벨을 만들어준다.
#     """
#     raise NotImplementedError
