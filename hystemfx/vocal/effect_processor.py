"""
vocal.effect_processor

- 이미 분리된 보컬 오디오 + 이펙트 체인 → 처리된 보컬 오디오로 바꿔주는 모듈
- 내부적으로는:
    1) numpy 배열 형태의 보컬 waveform (vocal_waveform, sr)
    2) effect_chain에서 만들어준 pedalboard (혹은 이펙트 리스트)
   를 받아서,
    3) 체인을 순서대로 적용한 결과를 반환하는 역할만 담당할 예정.
"""