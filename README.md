# Stem Splitting & FX Preprocessing

본 프로젝트는 **혼합된 밴드 오디오**를 입력으로 받아,
이를 악기별 Stem(보컬 / 기타 / 베이스 / 키보드)로 분리하고,
이후 각 Stem에 대하여 **세션 전용 이펙터 체인(FX Chain)·보정·전처리를 수행하는 파이프라인을 제공하는 것을 목표로 한다.

## 프로젝트 개요

본 라이브러리는 다음 두 가지 핵심 단계로 구성된다:

1. Stem Splitting (세션별 분리)
작성예정

2. FX Preprocessing (세션별 전처리 / 이펙터 체인 적용)
작성 예정

## 사용 기술 및 라이선스 (Built With & Licenses)

본 프로젝트는 고성능 음원 분리와 오디오 신호 처리를 위해 다음의 오픈 소스 라이브러리를 활용하였다.

| Component | Library | Model / Version | License | Note |
| :--- | :--- | :--- | :--- | :--- |
| **Source Separation** | [Demucs](https://github.com/facebookresearch/demucs) (Meta Research) | `htdemucs_6s` | MIT License | 6-stem 분리(Guitar 포함) 사용 |
| **Audio Effects** | [Pedalboard](https://github.com/spotify/pedalboard) (Spotify) | Latest | **GPL-3.0** | VST/AU 플러그인 기반 이펙트 처리 |
| **Audio I/O** | Librosa / SoundFile | - | ISC / BSD | 오디오 입출력 및 전처리 |

> **License Notice**: 본 프로젝트는 **GPL-3.0** 라이선스를 따르는 `spotify/pedalboard`를 포함하고 있으므로, 전체 프로젝트 또한 GPL-3.0 라이선스 정책을 준수함.

## 세션별 전처리 모듈

각 섹션에서는 세션의 고유한 음향적 특성을 기반으로 어떤 preprocessing filter를 설계했는지를 설명한다.

## 보컬 (담당자: 이현우)
### 처리 개요 (Processing Overview)

전체 파이프라인은 **[Source Separation] -> [Vocal FX Chain] -> [Post-processing]** 의 단계를 거친다.

1. **[공통과정] 전처리 (Pre-processing)**:  
   `seperator.py`를 통해 `htdemucs_6s` 모델이 원본 오디오를 각 세션에 맞는 Stem으로 분리하며,  
   본 모듈은 그중 `vocal` 트랙을 입력으로 사용한다.  
   필요 시 이미 분리된 보컬 트랙을 직접 입력으로 받을 수 있음.

2. **이펙팅 (Effecting)**:  
   `pedalboard` 라이브러리를 사용하여, 보컬 전용 이펙트 체인을 구성하고 직렬(Series)로 신호를 처리한다.

3. **후처리 (Post-processing)**:  
   레벨 정리, 리미터, 간단한 EQ 등을 적용해 믹스로 바로 사용할 수 있는 최종 보컬 레벨을 확보한다.

---

### 이펙트 체인 구성 (Effect Chain Specification)

본 세션에서 설계한 보컬용 페달보드 구성은 다음과 같다.  
아래 표에 명시된 값은 **기본 설정값(Default)**이며, 사용 목적에 따라 수정 및 랜덤화가 가능하다.

| 순서 | 이펙터 (Effect Unit) | 주요 설정 (Key Parameters) | 음향적 의도 (Tonal Function) |
| :--- | :--- | :--- | :--- |
| **1** | **Noise Gate** | `threshold_db`: -60dB, `ratio`: 10:1 | 분리 과정에서 발생할 수 있는 백그라운드 노이즈 및 브리딩 노이즈 제거 |
| **2** | **High-pass Filter** | `cutoff_hz`: 80–100Hz | 불필요한 저역 제거 및 마이크 럼블 억제 |
| **3** | **De-esser** | `center_freq`: 5–7kHz, `ratio`: 3:1 | 치찰음(Sibilance) 제어 |
| **4** | **Compressor** | `threshold`: -18dB, `ratio`: 3–4:1, `attack`: 5–10ms, `release`: 40–80ms | 발성 강도 차이를 줄이고 안정적 다이내믹 확보 |
| **5** | **Parametric EQ** | Presence +~10–12dB @3kHz, Air +~10–12dB @10kHz *(기본값, 곡에 따라 1–2dB로 조정 권장)* | 명료도 및 존재감(Presence) 보강 |
| **6** | **Saturation** | `drive_db`: 3–6dB, `mix`: 0.3 | 약한 하모닉스 추가로 밀도감 및 전면감 강화 |
| **7** | **Reverb** | `room_size`: 0.2–0.35, `pre_delay_ms`: 20ms, `wet_level`: 0.15–0.25 | 자연스러운 공간감 부여 |
| **8** | **Limiter** | `threshold_db`: -1.0dB | 최종 피크 제어 및 클리핑 방지 |

---

### 파라미터 커스터마이징 및 랜덤화 (Configuration & Randomization)

본 모듈은 **데이터 증강(Data Augmentation)** 및 **사용자 정의(User Customization)**를 모두 지원한다.

1. **사용자 정의 (User Customization)**  
   - 컴프레서 세기, EQ 게인, 리버브 양 등 모든 파라미터는  
     함수 호출 시 인자를 통해 자유롭게 수정 가능함.

2. **랜덤화 및 노이즈 주입 (Randomization & Noise Injection)**  
   - 모델 일반화 성능을 높이기 위해 주요 파라미터를 랜덤화할 수 있음.  
   - 예시 범위:  
     - `threshold ∈ [-24, -12] dB`  
     - `room_size ∈ [0.2, 0.5]`  
   - 필요 시 Gaussian noise, tape hiss, 미세한 EQ 변형 등 환경 기반 변형도 주입 가능함.

3. **재현성(Determinism)**  
   - 랜덤 체인 생성 시 `seed` 값을 지정할 수 있으며,  
     같은 seed 입력 시 항상 동일한 랜덤 이펙트 체인이 생성됨.

부드러운 배음(Harmonic Overtones):
목소리 특성상 상위 배음들이 부드럽게 이어지며, 기타나 신스처럼 날카로운 고주파 노이즈가 거의 없다.
이 때문에 보컬 배음은 스펙트로그램에서 "파도처럼 이어지는" 부드러운 수평 패턴을 형성한다.

## 일렉 기타 (담당자: 김상봉)
### 처리 개요 (Processing Overview)
전체 파이프라인은 **[Source Seperation] -> [Effect Chain Application]** 의 단계를 거친다.

1. **[공통과정]전처리 (Pre-processing)**: `separator.py`를 통해 `hydemucs_6s` 모델이 원본 오디오를 각 세션에 맞는 Stem 으로 분리하며, 본 모듈은 그중 `guitar` 트랙을 입력으로 사용한다.
2. **이펙팅 (Effecting)**: `pedalboard` 라이브러리를 사용하여, 가상의 페달보드를 구성하고 직렬(Series)로 신호를 처리한다.

### 이펙트 체인 구성 (Effect Chain Specification)

본 세션에서 설계한 페달보드 구성은 다음과 같다. 아래 표에 명시된 값은 **기본 설정값(Default)**이며, 사용 목적에 따라 수정, 랜덤화가 가능함.

| 순서 | 이펙터 (Effect Unit) | 주요 설정 (Key Parameters) | 음향적 의도 (Tonal Function) |
| :--- | :--- | :--- | :--- |
| **1** | **Noise Gate** | `threshold_db`: -60dB | 음원 분리 과정에서 발생할 수 있는 아티팩트 및 배경 노이즈 제거 |
| **2** | **Compressor** | `ratio`: 4:1, `attack`: 10ms | 다이내믹 레인지를 평탄화하여 단단한 피킹 뉘앙스 강조 |
| **3** | **Distortion** | `drive_db`: 12dB | 크런치(Crunch) 톤 형성 및 배음(Harmonics) 강조를 통한 존재감 부각 |
| **4** | **Chorus** | `rate_hz`: 1.2Hz, `depth`: 0.3 | 스테레오 이미지를 확장하고 몽환적인 공간감 부여 |
| **5** | **Reverb** | `room_size`: 0.4, `wet_level`: 0.3 | 소규모 클럽 공간의 자연스러운 잔향(Ambience) 시뮬레이션 |
| **6** | **Gain** | `gain_db`: 0dB | 이펙팅으로 인한 레벨 변화 보정 및 최종 볼륨 조절 |

### 파라미터 커스터마이징 및 랜덤화 (Configuration & Randomization)

본 모듈은 **데이터 증강(Data Augmentation)**을 위한 동적 파라미터 조정을 지원한다.

1. **사용자 정의 (User Customization)**:
    - 위에서 명시된 주요 파라미터(`drive_db`, `room_size` 등)는 함수 호출 시 인자(Arguments)를 통해 직접 수정할 수 있다.
2. **랜덤화 및 노이즈 주입 (Randomization & Noise Injection)**:
    - 학습 데이터의 다양성을 확보하기 위해 **파라미터 랜덤화(Stochastic Parameterization)** 기능을 지원한다.
    - 활성화 시, 각 이펙터의 수치가 지정된 범위 내에서 무작위로 변동되며, 필요에 따라 임의의 노이즈(Gaussian Noise 등)를 신호 체인에 추가해 모델의 강건성(Robustness)을 테스트할 수 있음.

## 베이스 (담당자: 유지성)
### 처리 개요 (Processing Overview)

본 모듈은 **Source Separation → Effect Chain Application** 의 2단계 파이프라인을 통해 밴드 사운드의 저음역대 중심을 잡는 베이스 기타 성분을 분리하고 전문적인 후처리를 수행한다.

1. **음원 분리 (Source Separation)**: Demucs의 `htdemucs_6s` 모델을 활용하여 6-stem 분리를 수행하며, 이 중 `bass` stem을 추출한다. 특히 킥 드럼(Kick Drum)과의 주파수 마스킹을 해소하고 순수 베이스 라인을 확보하는 데 주력한다.
2. **이펙트 처리 (Effect Processing)**: Spotify의 Pedalboard 라이브러리를 사용하여 추출된 베이스 성분에 최적화된 다이내믹 및 톤 보정 체인을 적용한다.

## 신디사이저 & 피아노 & 키보드 (담당자: 정진욱)

### 처리 개요 (Processing Overview)

본 모듈은 **Source Separation → Effect Chain Application** 의 2단계 파이프라인을 통해 대중가요 믹스에서 신디사이저, 피아노, 키보드 성분을 분리하고 전문적인 후처리를 수행한다.

1. **음원 분리 (Source Separation)**: Demucs의 `htdemucs_6s` 모델을 활용하여 6-stem 분리를 수행하며, 이 중 `piano` stem을 신디사이저/피아노/키보드 성분으로 추출한다.
2. **이펙트 처리 (Effect Processing)**: Spotify의 Pedalboard 라이브러리를 사용하여 추출된 신디사이저 성분에 최적화된 이펙트 체인을 적용한다.

### 음향 분리 전략 (Separation Strategy)

신디사이저, 피아노, 키보드는 전자 악기와 어쿠스틱 악기의 중간 영역에 위치하며, 다음과 같은 음향적 특성을 공유한다:

- **명확한 음높이 (Pitch Clarity)**: 기타나 드럼과 달리 정확한 음정을 가진 타악기적 특성
- **지속적인 배음 구조 (Sustained Harmonics)**: 건반 타격 후 일정 시간 동안 지속되는 안정적인 배음 패턴
- **중역대 에너지 집중 (Mid-range Energy)**: 약 200Hz~4kHz 사이에 주요 에너지가 분포

### 음향 분리 전략 (Separation Strategy)

베이스 기타는 화성적 기반과 리듬 그루브를 동시에 담당하며, 다음과 같은 음향적 특성을 고려하여 필터를 설계하였다:

- **저음역대 에너지 (Low-end Energy)**: 40Hz ~ 200Hz 대역의 기본 주파수(Fundamental)를 단단하게 유지하여 믹스의 무게중심을 확보
- **다이내믹스 제어 (Dynamic Consistency)**: 핑거링/피킹 강약에 따른 레벨 차이를 줄여, 전체 곡 내내 균일한 볼륨감 유지
- **중고역 배음 (Mid-High Harmonics)**: 소형 스피커 청취 환경을 고려하여, 500Hz ~ 2kHz 대역의 배음을 강조하거나 Saturation을 더해 존재감 부각

### 이펙트 체인 명세 (Effect Chain Specification)

분리된 베이스 오디오에 적용되는 이펙트 체인은 **"단단함(Solidity)"**과 **"명료도(Definition)"**에 초점을 맞춘다. 아래 표의 값은 **기본 설정값(Default)**이며, 프리셋 또는 파라미터를 통해 조정 가능하다.

| 순서 | 이펙터 (Effect Unit) | 주요 설정 (Key Parameters) | 음향적 의도 (Tonal Function) |
| :--- | :--- | :--- | :--- |
| **1** | **Noise Gate** | `threshold_db`: -55dB, `ratio`: 10:1 | 분리 과정에서 남은 미세한 노이즈 및 연주 사이의 험(Hum) 제거 |
| **2** | **Compressor** | `ratio`: 4:1, `attack`: 20ms, `release`: 100ms | 들쑥날쑥한 피킹 뉘앙스를 정리하여 단단하고 펀치감 있는 톤 형성 |
| **3** | **Distortion** | `drive_db`: 8dB | 진공관 앰프 느낌의 따뜻한 배음(Saturation) 추가 (존재감 향상) |
| **4** | **EQ - Low Shelf** | `freq`: 80Hz, `gain`: +2dB | 킥 드럼과 어우러지는 묵직한 서브 베이스 대역 보강 |
| **5** | **EQ - Mid Scoop** | `freq`: 400Hz, `gain`: -3dB, `Q`: 1.5 | '멍청한 소리(Muddy)'를 유발하는 중저역을 깎아내어 소리를 정돈 |
| **6** | **Chorus** | `rate_hz`: 0.5Hz, `depth`: 0.15 | 스테레오 이미지를 미세하게 확장하여 현대적인 베이스 톤 연출 |
| **7** | **Limiter** | `threshold_db`: -0.5dB | 최종 출력 피크 제어 및 클리핑 방지 |

### 프리셋 시스템 (Preset System)

다양한 연주 주법 및 장르에 대응하기 위해 5가지 사전 정의된 프리셋을 제공한다:

- **Default**: 핑거/피크 주법 모두에 어울리는 균형 잡힌 설정
- **Vintage**: 따뜻한 튜브 드라이브와 롤오프된 고역을 특징으로 하는 레트로 톤 (재즈, 블루스)
- **Modern**: 중역을 깎고(Scoop) 저역/고역을 강조하여 슬랩 주법에 최적화된 톤 (펑크, 팝)
- **Fuzz**: 강한 디스토션을 적용하여 록/메탈 장르에 적합한 공격적인 톤
- **Sub**: 가청 주파수 배음보다는 묵직한 저음(Sub-bass) 위주의 톤 (힙합, 일렉트로닉)

### 데이터 증강 및 랜덤화 (Data Augmentation)

기계 학습 모델의 강건성(Robustness)을 확보하기 위해, 이펙트 파라미터의 확률적 변조(Stochastic Modulation)를 지원한다:

- **RandomizedBassEffects 클래스**: 지정된 범위 내에서 파라미터를 무작위로 샘플링
- **범위 커스터마이징**: `drive_db`, `compressor_threshold` 등 핵심 인자의 변동 폭 설정 가능
- **재현성 보장**: Seed 값 설정을 통한 결정론적(Deterministic) 랜덤화 지원

## 신디사이저 & 피아노 & 키보드 (담당자: 정진욱)

### 처리 개요 (Processing Overview)

본 모듈은 **Source Separation → Effect Chain Application** 의 2단계 파이프라인을 통해 대중가요 믹스에서 신디사이저, 피아노, 키보드 성분을 분리하고 전문적인 후처리를 수행한다.

1. **음원 분리 (Source Separation)**: Demucs의 `htdemucs_6s` 모델을 활용하여 6-stem 분리를 수행하며, 이 중 `piano` stem을 신디사이저/피아노/키보드 성분으로 추출한다.
2. **이펙트 처리 (Effect Processing)**: Spotify의 Pedalboard 라이브러리를 사용하여 추출된 신디사이저 성분에 최적화된 이펙트 체인을 적용한다.

### 음향 분리 전략 (Separation Strategy)

신디사이저, 피아노, 키보드는 전자 악기와 어쿠스틱 악기의 중간 영역에 위치하며, 다음과 같은 음향적 특성을 공유한다:

- **명확한 음높이 (Pitch Clarity)**: 기타나 드럼과 달리 정확한 음정을 가진 타악기적 특성
- **지속적인 배음 구조 (Sustained Harmonics)**: 건반 타격 후 일정 시간 동안 지속되는 안정적인 배음 패턴
- **중역대 에너지 집중 (Mid-range Energy)**: 약 200Hz~4kHz 사이에 주요 에너지가 분포

Demucs의 `htdemucs_6s` 모델은 이러한 특성을 학습하여 piano stem으로 분류하며, 본 모듈은 이를 활용하여 높은 정확도의 분리를 수행한다.

### 이펙트 체인 명세 (Effect Chain Specification)

분리된 신디사이저/피아노 오디오에 적용되는 이펙트 체인은 다음과 같이 구성된다. 아래 표의 값은 **기본 설정값(Default)**이며, 프리셋 또는 파라미터를 통해 조정 가능하다.

| 순서 | 이펙터 (Effect Unit) | 주요 설정 (Key Parameters) | 음향적 의도 (Tonal Function) |
| :--- | :--- | :--- | :--- |
| **1** | **Noise Gate** | `threshold_db`: -60dB, `ratio`: 10:1 | 음원 분리 과정에서 발생하는 크로스토크 및 저레벨 아티팩트 제거 |
| **2** | **High-pass Filter** | `cutoff_hz`: 80Hz | 불필요한 저역 럼블 제거 및 베이스와의 주파수 충돌 방지 |
| **3** | **Compressor** | `threshold`: -20dB, `ratio`: 3:1, `attack`: 5ms | 다이내믹 레인지 균일화 및 어택 트랜지언트 컨트롤 |
| **4** | **EQ - Low Shelf** | `freq`: 200Hz, `gain`: 0dB | 저역 바디감 조절 |
| **5** | **EQ - Mid Peak** | `freq`: 1.5kHz, `gain`: +2dB, `Q`: 1.0 | Presence 대역 강조를 통한 음의 명료도 향상 |
| **6** | **EQ - High Shelf** | `freq`: 8kHz, `gain`: +1dB | 고역 밝기(Brightness) 추가 |
| **7** | **Chorus** | `rate`: 0.8Hz, `depth`: 0.25, `mix`: 0.3 | 스테레오 이미지 확장 및 공간적 풍성함 부여 |
| **8** | **Reverb** | `room_size`: 0.35, `wet`: 0.25, `damping`: 0.5 | 자연스러운 앰비언스 및 공간감 시뮬레이션 |
| **9** | **Limiter** | `threshold_db`: -1.0dB | 최종 출력 레벨 제한 및 클리핑 방지 |

### 프리셋 시스템 (Preset System)

다양한 음악 장르 및 프로덕션 스타일에 대응하기 위해 5가지 사전 정의된 프리셋을 제공한다:

- **Default**: 범용적이고 균형 잡힌 설정
- **Bright**: 중고역 강조를 통한 밝고 화려한 톤 (팝, 댄스 뮤직)
- **Warm**: 저역 부스트 및 고역 감쇠를 통한 따뜻하고 부드러운 톤 (발라드, 재즈)
- **Spacious**: 깊은 리버브와 강한 코러스로 광대한 공간감 연출 (앰비언트, 일렉트로닉)
- **Tight**: 강한 압축과 짧은 리버브로 타이트하고 펀치감 있는 사운드 (R&B, 힙합)

### 데이터 증강 및 랜덤화 (Data Augmentation)

기계 학습 모델의 강건성(Robustness)을 확보하기 위해, 이펙트 파라미터의 확률적 변조(Stochastic Modulation)를 지원한다:

- **RandomizedSynthEffects 클래스**: 지정된 범위 내에서 파라미터를 무작위로 샘플링
- **범위 커스터마이징**: 각 파라미터의 최소/최대값을 사용자가 정의 가능
- **재현성 보장**: Seed 값 설정을 통한 결정론적(Deterministic) 랜덤화 지원

이를 통해 동일한 소스 오디오로부터 음향 특성이 다른 다수의 샘플을 생성할 수 있으며, 이는 학습 데이터의 다양성 확보에 기여한다.

### 모듈 구조 (Module Structure)

```
hystemfx/synth/
├── separator.py       # Demucs 기반 음원 분리
├── effects.py         # Pedalboard 이펙트 체인
├── pipeline.py        # 통합 파이프라인 (분리 + 이펙트)
├── example.py         # 사용 예제 스크립트
└── __init__.py        # 모듈 인터페이스
```

### 사용 예시 (Usage Example)

```python
from hystemfx.synth import SynthPipeline

# 파이프라인 초기화
pipeline = SynthPipeline(
    separation_model="htdemucs_6s",
    device="cuda",
    effect_preset="bright"
)

# 파일 처리: 분리 + 이펙트 적용
pipeline.process_file(
    input_path="input_mix.wav",
    output_path="output_synth.wav"
)
```

상세한 사용 예제는 `hystemfx/synth/example.py`를 참조.
