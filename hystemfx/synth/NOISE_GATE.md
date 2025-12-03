# Noise Gate Implementation for Synth/Piano/Keyboard

## 개요

신디사이저/피아노/키보드 분리 후 남은 노이즈와 아티팩트를 제거하기 위한 Noise Gate 이펙터 구현 문서입니다.

## 현재 구현

현재 `SynthEffectsChain`에서는 **Compressor를 high ratio로 설정**하여 Noise Gate로 활용하고 있습니다.

```python
Compressor(
    threshold_db=gate_threshold_db,  # 기본값: -60dB
    ratio=gate_ratio,                 # 기본값: 10.0
    attack_ms=gate_attack_ms,         # 기본값: 1.0ms
    release_ms=gate_release_ms        # 기본값: 100.0ms
)
```

### 왜 Compressor를 사용하는가?

1. **Pedalboard의 제한**: 일부 버전의 Pedalboard에는 전용 `NoiseGate` 플러그인이 없을 수 있습니다.
2. **효과적인 대안**: High ratio (10:1)의 Compressor는 threshold 이하의 신호를 효과적으로 감쇠시켜 Noise Gate와 동일한 효과를 냅니다.
3. **안정성**: Compressor는 모든 Pedalboard 버전에서 안정적으로 작동합니다.

## Noise Gate 작동 원리

### Threshold (임계값)
- `-60dB` 이하의 신호를 노이즈로 간주
- **낮은 값** (-70dB ~ -80dB): 더 많은 신호 통과 (미세한 노이즈까지 보존)
- **높은 값** (-50dB ~ -40dB): 더 적극적인 노이즈 제거 (일부 유용한 신호도 제거될 수 있음)

### Ratio (압축 비율)
- `10:1` - threshold 이하 신호를 1/10로 감쇠
- **높은 ratio** (10:1 이상): 강력한 게이팅 효과
- **낮은 ratio** (3:1 ~ 5:1): 부드러운 게이팅 효과

### Attack Time (어택 타임)
- `1.0ms` - 신호가 threshold를 넘으면 1ms 안에 게이트 열림
- **빠른 attack** (0.1 ~ 2ms): 트랜지언트 보존 (피아노 음의 공격음)
- **느린 attack** (5 ~ 10ms): 부드러운 페이드인

### Release Time (릴리즈 타임)
- `100ms` - 신호가 threshold 아래로 내려가면 100ms에 걸쳐 게이트 닫힘
- **빠른 release** (10 ~ 50ms): 짧은 음에 적합, 노이즈가 끝날 수 있음
- **느린 release** (100 ~ 300ms): 자연스러운 감쇠, 노이즈 꼬리 제거

## 파라미터 튜닝 가이드

### 문제별 해결 방법

#### 1. 노이즈가 여전히 들린다
```python
chain = SynthEffectsChain(
    gate_threshold_db=-50.0,  # threshold 상향 (더 적극적)
    gate_ratio=15.0            # ratio 상향 (더 강력하게)
)
```

#### 2. 피아노 음이 잘린다 (너무 aggressive)
```python
chain = SynthEffectsChain(
    gate_threshold_db=-70.0,  # threshold 하향 (더 많은 신호 통과)
    gate_ratio=5.0,            # ratio 하향 (덜 aggressive)
    gate_release_ms=200.0      # release 길게 (자연스러운 감쇠)
)
```

#### 3. 피아노 음의 attack이 부자연스럽다
```python
chain = SynthEffectsChain(
    gate_attack_ms=0.5,        # attack 빠르게 (즉시 열림)
)
```

#### 4. 음이 끊기는 느낌
```python
chain = SynthEffectsChain(
    gate_release_ms=300.0,     # release 길게
)
```

## 악기별 권장 설정

### 피아노
```python
SynthEffectsChain(
    gate_threshold_db=-60.0,
    gate_ratio=10.0,
    gate_attack_ms=0.5,      # 빠른 attack으로 명확한 음 시작
    gate_release_ms=150.0    # 자연스러운 페달 효과
)
```

### 신디사이저 (Pad)
```python
SynthEffectsChain(
    gate_threshold_db=-65.0,  # 부드러운 게이팅
    gate_ratio=8.0,
    gate_attack_ms=5.0,       # 천천히 페이드인
    gate_release_ms=200.0     # 긴 꼬리 보존
)
```

### 신디사이저 (Lead/Pluck)
```python
SynthEffectsChain(
    gate_threshold_db=-55.0,  # 적극적인 게이팅
    gate_ratio=12.0,
    gate_attack_ms=0.3,       # 매우 빠른 attack
    gate_release_ms=50.0      # 짧은 release
)
```

## 고급 기능: 전용 NoiseGate 사용 (선택사항)

Pedalboard가 `NoiseGate`를 지원하는 경우:

```python
from pedalboard import NoiseGate

# effects.py의 import 수정
from pedalboard import (
    Pedalboard, Compressor, Gain, Chorus, Reverb, 
    Limiter, HighpassFilter, LowShelfFilter, 
    HighShelfFilter, PeakFilter, NoiseGate
)

# Pedalboard 구성에서 변경
self.board = Pedalboard([
    # 1. 전용 Noise Gate
    NoiseGate(
        threshold_db=gate_threshold_db,
        ratio=gate_ratio,
        attack_ms=gate_attack_ms,
        release_ms=gate_release_ms
    ),
    # ... 나머지 이펙터들
])
```

## 테스트 및 검증

### 테스트 스크립트

```python
from hystemfx.synth.effects import SynthEffectsChain
from hystemfx.core.io import load_audio, save_audio

# 오디오 로드
audio, sr = load_audio("input.wav")

# 다양한 설정 테스트
for threshold in [-70, -60, -50, -40]:
    chain = SynthEffectsChain(gate_threshold_db=threshold)
    processed = chain.process(audio, sr)
    save_audio(processed, sr, f"output_gate_{threshold}db.wav")
    print(f"Processed with threshold: {threshold}dB")
```

### 청취 평가 체크리스트

- [ ] 노이즈가 효과적으로 제거되었는가?
- [ ] 음의 attack이 자연스러운가?
- [ ] 음의 sustain이 유지되는가?
- [ ] 음의 release/decay가 자연스러운가?
- [ ] 게이팅 아티팩트(펌핑, 클릭 노이즈)가 없는가?

## 참고 사항

- Noise Gate는 **이펙트 체인의 첫 번째**에 위치하여, 후속 이펙터에 노이즈가 전달되지 않도록 합니다.
- High-pass Filter와 함께 사용하면 저역 럼블과 노이즈를 동시에 제거할 수 있습니다.
- 과도한 게이팅은 소리를 부자연스럽게 만들 수 있으므로, 최소한의 설정으로 시작하는 것이 좋습니다.

## 문의 및 피드백

이 구현에 대한 개선 제안이나 문제 발견 시 Issue를 남겨주세요!
