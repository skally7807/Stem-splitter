"""
vocal.pipeline

- 보컬 이펙트 전체 파이프라인의 "오케스트레이션(흐름 제어)"을 담당하는 모듈.
- 이 파일 한 곳에서:
    1) input: 믹스된 오디오 파일 경로 (또는 이미 분리된 보컬 트랙)
    2) core/separator (Demucs 등) 를 이용해 보컬 stem 분리 (필요할 경우)
    3) vocal.effect_chain.build_vocal_chain(...) 으로 이펙트 체인 생성
    4) vocal.effect_processor 를 사용해 체인 적용
    5) vocal.postprocess 로 최종 정리
    6) output: 처리된 보컬 wav를 파일로 저장하거나, numpy 배열로 반환

- 요약: "보컬 이펙트 전용 end-to-end 파이프라인의 진입점(entry point)" 역할.
"""

# 예상 주요 함수 설계:
#
# def process_vocal_pipeline(
#     input_path: str,
#     output_path: str,
#     separator_model: str = "htdemucs_6s",
#     chain_config: Optional[Dict[str, Any]] = None,
# ) -> str:
#     """
#     High-level pipeline:
#         1) input_path 의 믹스된 오디오를 core/separator 모듈로 보컬 stem만 분리
#         2) vocal.effect_chain.build_vocal_chain(chain_config) 로 이펙트 체인 생성
#         3) vocal.effect_processor.apply_vocal_chain(...) 으로 이펙트 적용
#         4) vocal.postprocess.apply_vocal_postprocess(...) 로 레벨/리미터 정리
#         5) 결과를 output_path 에 저장하고, 그 경로를 반환
#
#     나중에:
#         - dry/wet 비율 옵션
#         - 원래 믹스에 다시 합쳐서 "보컬만 이펙팅된 전체 곡" 도 같이 출력하는 기능 추가 가능
#     """
#     raise NotImplementedError
