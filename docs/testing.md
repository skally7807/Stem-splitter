HystemFX 테스트 문서 (Test Suite Documentation)
개요 (Overview)

HystemFX 프로젝트는 고품질 오디오 분리와 이펙트 체인을 안정적으로 제공하기 위해
표준화된 유닛 테스트 구조를 도입했습니다.

tests/ 디렉토리 내 테스트들은 다음을 보장합니다:

Core Separator API 일관성

이펙트 체인의 재현성(Reproducibility)

Robustness(입력 변형에 대한 견고성)

세션별(Guitar / Synth / Vocal) 모듈 안정성

테스트 파일 구조:

tests/
├── test_core_separator_contract.py
├── test_fx_determinism.py
├── test_guitar_effect_blocks.py
├── test_synth_effects_chain.py
└── test_vocal_pipeline_robustness.py

### 1. test_core_separator_contract.py

(Core API 규약 테스트)

목적

프로젝트 전체가 공유하는 Core Separator Contract(계약) 을 검증합니다.

검증 항목

DemucsSeparator.separate_file()의 반환 타입이 dict인지

필수 stem 키 존재

{ "vocals", "guitar", "bass", "piano" }

각 stem shape = (C, T)

dtype = float32

값 범위가 [-1.0, 1.0] 내에 있는지

Sample rate = 44,100 Hz 고정인지

왜 중요한가?

팀원들이 서로 다른 세션 모듈을 개발해도
최종 Mixer에서 반드시 조합 가능하도록 API 형식이 통일되어 있어야 합니다.

이 테스트가 팀 전체의 기반(Contract)을 강제합니다.

### 2. test_fx_determinism.py

(이펙트 재현성 테스트)

목적

seed를 동일하게 설정하면
Vocal/Bass FX 출력이 항상 동일한지 확인합니다.

검증 항목
out1 = rack.process(audio, sr, seed=0)
out2 = rack.process(audio, sr, seed=0)


두 출력이 완전히 동일해야 한다

파라미터 랜덤화(randomize)가 seed 기반으로 고정되는지 확인

의미

논문 실험, R&D, 비교 실험에서 반복 가능한 결과 확보

오디오 ML에서 매우 중요한 reproducibility 보장

### 3. test_guitar_effect_blocks.py

(기타 이펙트 블록 단위 테스트)

목적

각 Guitar 이펙트(FX) 클래스가 단독으로 정상 동작하는지 검사합니다.

검증 항목

FX 인스턴스 생성 가능 여부

process(dummy_audio) 입력 시 crash 없는지

출력 shape 유지되는지

의미

세션별 이펙트 코드 작성 시 발생할 수 있는:

파라미터 오타

Pedalboard 객체 생성 오류

shape mismatch
를 조기에 잡아주는 단위 테스트입니다.

### 4. test_synth_effects_chain.py

(신디/피아노/키보드 이펙트 체인 테스트)

목적

SynthEffectsChain 및 RandomizedSynthEffects가
안정적으로 입력을 처리하는지 검증합니다.

검증 항목

SynthEffectsChain이 dummy 오디오 처리 가능

출력 shape, 값 범위 확인

RandomizedSynthEffects가 설정된 range 안에서 파라미터를 생성하는지

주의

Synth의 랜덤 이펙트는 일부러 재현성을 강제하지 않음
(데이터 증강 목적)

의미

신디 계열 FX 체인이 batch 처리 또는 augment 상황에서도
안정적으로 동작하는지 확인

### 5. test_vocal_pipeline_robustness.py

(Vocal Pipeline 견고성 테스트)

목적

현실적인 “문제 있는 입력(audio edge cases)”을 넣었을 때도
파이프라인이 절대 crash하지 않고,
Demucs 실패 시 fallback 로직이 정상 작동하는지 검증합니다.

검증하는 입력 케이스
입력 종류	설명
매우 짧은 오디오	0.1초 미만
긴 오디오	메모리 처리 확인
22kHz	자동 리샘플링 확인
48kHz	자동 리샘플링 확인
Mono (1채널)	Demucs 에러 발생 → fallback 확인
Stereo	정상 처리
의미

사용자는 어떤 형태의 오디오를 넣어도 이상한 입력으로 인해 프로그램이 터지면 안 됨.
실제 서비스 품질과 직결되는 테스트.

### 6. 테스트 실행 방법
전체 테스트 실행
python -m unittest discover tests

특정 테스트 파일만 실행
python -m unittest tests/test_core_separator_contract.py

### 7. 테스트 설계 철학 (Design Philosophy)
✔ Dummy 오디오 기반

모든 테스트는 실제 음악 파일 대신:

임펄스 신호

노이즈

사인파

zero wave

등의 dummy 오디오로 진행됩니다.

→ 빠르고, reproducible하고, 저장 용량도 없음.

✔ 목적별 파일 분리

각 테스트 파일은 하나의 책임만 담당하도록 설계되었음.
덕분에:

디버깅 쉬움

PR 리뷰 용이

과제/프로젝트 설명 시 명확함

✔ Robustness 우선

Vocal pipeline은 특히 다양한 예외 상황을 커버하도록 테스트됨.

✔ Contract 기반 개발

Core separator 규약을 테스트로 강제함으로써
팀 전체가 동일한 API를 사용.

### 8. Dummy Audio 생성 예시
import numpy as np

def make_dummy_audio(seconds=1.0, sr=44100, channels=2):
    t = int(seconds * sr)
    audio = np.random.uniform(-0.5, 0.5, size=(channels, t)).astype(np.float32)
    return audio, sr


테스트 전용으로 reproducible한 입력을 생성.

### 요약

HystemFX 테스트 스위트는 다음을 보장합니다:

API 일관성

이펙트 재현성

입력 형태 변화에 대한 안정성

모듈 단위 안전성

오디오 파이프라인 전체의 신뢰성 확보

이 테스트들은 프로젝트의 유지보수성, 협업 구조, 품질 보장에 중요한 역할을 합니다.


