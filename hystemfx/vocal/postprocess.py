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
