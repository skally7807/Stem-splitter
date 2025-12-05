# Synth Module 사용 가이드

## 설치

필요한 패키지를 설치합니다:

```bash
pip install demucs
pip install pedalboard
```

## 빠른 시작

### 1. 가장 간단한 사용법 (올인원)

```python
from hystemfx.synth import SynthPipeline

# 파이프라인 생성
pipeline = SynthPipeline(
    separation_model="htdemucs_6s",
    device="cuda",  # GPU 사용, CPU만 있으면 "cpu"
    effect_preset="default"  # 또는 "bright", "warm", "spacious", "tight"
)

# 파일 처리: 분리 + 이펙트 적용을 한 번에
pipeline.process_file(
    input_path="내_노래.wav",
    output_path="신디사이저_추출.wav"
)
```

### 2. 음원 분리만 하기 (이펙트 없이)

```python
from hystemfx.synth import SynthSeparator

separator = SynthSeparator(model_name="htdemucs_6s")

# 파일에서 신디사이저/피아노만 분리
separator.separate_file(
    input_path="내_노래.wav",
    output_path="신디사이저만_분리.wav"
)
```

### 3. 이펙트만 적용하기 (이미 분리된 파일에)

```python
from hystemfx.synth import apply_synth_effects
from pedalboard.io import AudioFile

# 오디오 로드
with AudioFile("신디사이저만_분리.wav") as f:
    audio = f.read(f.frames)
    sample_rate = f.samplerate

# 이펙트 적용 (프리셋 사용)
processed = apply_synth_effects(
    audio, 
    sample_rate, 
    preset="bright"  # 밝은 톤
)

# 저장
with AudioFile("신디사이저_밝게.wav", 'w', sample_rate, processed.shape[0]) as f:
    f.write(processed)
```

### 4. 세밀한 파라미터 조정

```python
from hystemfx.synth import SynthEffectsChain
from pedalboard.io import AudioFile

# 커스텀 이펙트 체인 생성
effects = SynthEffectsChain(
    comp_ratio=4.0,              # 컴프레서 비율
    eq_mid_gain_db=3.0,          # 중역 +3dB
    chorus_mix=0.4,              # 코러스 40%
    reverb_room_size=0.5,        # 리버브 룸 사이즈
    reverb_wet_level=0.3         # 리버브 양 30%
)

# 오디오 로드
with AudioFile("신디사이저만_분리.wav") as f:
    audio = f.read(f.frames)
    sample_rate = f.samplerate

# 이펙트 적용
processed = effects.process(audio, sample_rate)

# 저장
with AudioFile("커스텀_이펙트.wav", 'w', sample_rate, processed.shape[0]) as f:
    f.write(processed)
```

## 프리셋 종류

- **default**: 범용적이고 균형 잡힌 설정
- **bright**: 밝고 화려한 톤 (팝, 댄스)
- **warm**: 따뜻하고 부드러운 톤 (발라드, 재즈)
- **spacious**: 광대한 공간감 (앰비언트, 일렉트로닉)
- **tight**: 타이트하고 펀치감 있는 사운드 (R&B, 힙합)

## 배치 처리 (여러 파일 한 번에)

```python
from hystemfx.synth import SynthPipeline

pipeline = SynthPipeline(effect_preset="bright")

# 여러 파일 한 번에 처리
input_files = ["노래1.wav", "노래2.wav", "노래3.wav"]

pipeline.batch_process(
    input_files=input_files,
    output_dir="출력폴더",
    apply_effects=True
)
```

## 데이터 증강 (랜덤 이펙트)

```python
from hystemfx.synth import RandomizedSynthEffects
from pedalboard.io import AudioFile

randomizer = RandomizedSynthEffects(seed=42)  # 재현 가능

with AudioFile("신디사이저.wav") as f:
    audio = f.read(f.frames)
    sample_rate = f.samplerate

# 5가지 다른 버전 생성
for i in range(5):
    processed, params = randomizer.process(audio, sample_rate)
    
    with AudioFile(f"버전_{i+1}.wav", 'w', sample_rate, processed.shape[0]) as f:
        f.write(processed)
    
    print(f"버전 {i+1} 파라미터: {params}")
```

## 참고사항

- **GPU 사용**: `device="cuda"` 설정 시 훨씬 빠름 (CUDA 필요)
- **메모리**: 긴 곡은 메모리를 많이 사용할 수 있음
- **처리 시간**: 3분 곡 기준 GPU에서 약 10-20초, CPU에서 1-2분 정도

더 많은 예제는 `hystemfx/synth/example.py`를 참고하세요!
