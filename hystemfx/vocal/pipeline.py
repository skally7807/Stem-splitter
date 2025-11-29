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
