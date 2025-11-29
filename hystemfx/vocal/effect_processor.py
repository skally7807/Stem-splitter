"""
vocal.effect_processor

- 이미 분리된 보컬 오디오 + 이펙트 체인 → 처리된 보컬 오디오로 바꿔주는 모듈
- 내부적으로는:
    1) numpy 배열 형태의 보컬 waveform (vocal_waveform, sr)
    2) effect_chain에서 만들어준 pedalboard (혹은 이펙트 리스트)
   를 받아서,
    3) 체인을 순서대로 적용한 결과를 반환하는 역할만 담당할 예정.
"""


# 예상 함수 형태 
# def apply_vocal_chain(vocal_waveform: np.ndarray, sr: int, chain) -> np.ndarray:
#     """
#     Args:
#         vocal_waveform: 분리된 보컬 오디오 (mono 또는 stereo)
#         sr: sample rate
#         chain: effect_chain.build_vocal_chain(...) 에서 넘어온 이펙트 체인 객체
#
#     Returns:
#         processed_vocal: 이펙트가 모두 적용된 보컬 오디오
#
#     내부 로직 (나중에 구현):
#         - chain 객체를 순차적으로 적용
#         - pedalboard.Board 를 쓰면 board(vocal_waveform, sr) 형태로 호출
#         - 에러/클리핑 방지를 위한 레벨 체크는 postprocess에서 처리
#     """
#     raise NotImplementedError
