# HystemFX 테스트 문서 (`test.md`)

본 문서는 HystemFX 프로젝트의 핵심 테스트 스위트 구조와 각 테스트 파일이 검증하는 **기능 계약(contracts)**을 정리한 문서입니다.  
테스트는 총 4개의 주요 분야를 다루며, 세션별 FX 체인·랜덤성 결정성·Core Separator 계약을 포함합니다.

---

# 1. `tests/test_synth_effects_chain.py`
> 출처: `test_synth_effects_chain.py`

## 목적
- Synth 세션의 이펙트 체인이 **입력·출력 shape 계약**을 준수하는지 검증  
- preset이 정상적으로 동작하며 preset 간 **출력 차이**가 존재하는지 확인  
- 다양한 입력 형식에 대한 견고함 검증

## 테스트 항목

### ✔ 1) Stereo 입력 shape 유지
- 입력: `(2, T)`  
- 출력: 반드시 `(2, T)`  
- NaN/Inf 없어야 함

### ✔ 2) Mono 1D 입력 처리
- 입력: `(T,)`  
- 내부적으로 `(1, T)`로 변환  
- 출력도 2D `(1, T)` 형태여야 함

### ✔ 3) (T, C) 형식 입력 처리
- 입력: `(T, 2)`  
- 처리 후 정상적인 2D 배열 반환

### ✔ 4) 모든 preset 동작 확인
preset 목록:"default", "bright", "warm", "spacious", "tight"

- 모든 preset 실행 가능  
- 출력 shape 동일  
- preset 간 결과가 **모두 동일하면 안 됨** → preset 유효성 검증

---

# 2. `tests/test_guitar_effects_chain.py`
> 출처: `test_guitar_effects_chain.py`

## 목적
- Guitar FX Chain의 preset 처리, 입력 형식 유연성, fallback 로직, 설정 반환 기능 테스트

## 테스트 항목

### ✔ 1) 기본 preset 정상 처리
테스트 preset:
"clean", "distortion", "crunch"
- preset별로 처리 에러 없어야 함  
- 출력 shape == 입력 shape

### ✔ 2) 다양한 입력 형식 테스트
- Mono `(T,)` → 출력 `(1, T)` 형태  
- `(T, C)` 입력 → 처리 후 `(T, C)` 유지

### ✔ 3) get_settings() 값 검증
- `preset`, `drive_db`, `gate_threshold_db` 등 key 존재  
- 설정 값 정확하게 일치해야 함

### ✔ 4) Unknown preset fallback
- 존재하지 않는 preset 입력 시 clean preset으로 fallback  
- 에러 없이 shape 유지

---

# 3. `tests/test_fx_determinism.py`
> 출처: `test_fx_determinism.py`

## 목적
- VocalRack / BassRack의 파라미터 랜덤화(randomize_parameters)가  
  **동일 seed → 동일 출력**, **다른 seed → 다른 출력**임을 보장  
- 모델 reproducibility 보장

## 테스트 항목

### ✔ 1) VocalRack 동일 seed → 동일 출력
- seed=0  
- `np.allclose()`로 거의 완전 동일 비교

### ✔ 2) VocalRack 다른 seed → 다른 출력
- seed=0 vs seed=1  
- 동일하면 안 됨

### ✔ 3) BassRack 동일 seed → 동일 출력
- seed=123  
- 출력이 완전히 동일해야 함

### ✔ 4) Synth/Guitar도 확장 가능
- 동일 구조로 deterministic test 추가 가능

---

# 4. `tests/test_core_separator_contract.py`
> 출처: `test_core_separator_contract.py`

## 목적
Core 모듈의 `DemucsSeparator`가 **프로젝트의 공식 Contract**를 준수하는지 검증한다.  
이 테스트는 전체 파이프라인 안정성의 핵심이다.

## 테스트 항목

### ✔ 1) Dummy wav 생성 후 separate_file() 정상 작동
- 0.5초 스테레오 wav 생성 → 분리 실행  
- 파일 기반 API 검증

### ✔ 2) 반환 타입 검증
- `separate_file()` → 반드시 `dict` 반환

### ✔ 3) 필수 stem key 존재
필수 키:"vocals", "guitar", "bass", "piano"

- 누락 시 contract 위반

### ✔ 4) 각 stem shape = (C, T)
요구 조건:
- ndarray  
- 2차원  
- C ≥ 1  
- T > 0  
- T > C  (T는 sample 길이, C는 channel 수)

### ✔ 5) sample_rate 계약
- `self.separator.sample_rate == 44100` 여야 함  
- 프로젝트 표준 SR 유지 규칙 반영

---

# 📌 전체 테스트 요약

| 테스트 파일 | 보장 기능 |
|------------|-----------|
| `test_synth_effects_chain.py` | Synth FX 체인의 shape 안정성 & preset 유효성 |
| `test_guitar_effects_chain.py` | Guitar FX preset / shape / fallback / 설정 구조 |
| `test_fx_determinism.py` | Vocal/Bass random-parameter 결정성 보장 |
| `test_core_separator_contract.py` | Separator API의 공식 계약(shape, key, SR) 보장 |

---

# 📘 활용
- 팀 PR 리뷰 기준  
- 세션 확장 시 테스트 scaffold  
- CI(GitHub Actions) 테스트 기준  
- Contract 기반 개발을 통한 안정성 강화

