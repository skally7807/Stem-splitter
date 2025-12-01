# Synth Scripts

신디사이저/피아노/키보드 분리 및 이펙트 테스트 스크립트 모음

## 📂 파일 구조

### 기본 사용
- `test_separation_only.py` - 이펙트 없이 순수 분리만
- `apply_final_effects.py` - Level 4.4 최적 이펙트 적용 (추천!)

### 이펙트 테스트
- `add_effects.py` - 프리셋 이펙트 적용
- `add_minimal_effects.py` - 최소 이펙트
- `compare_versions.py` - 5가지 버전 비교
- `fine_tune_effects.py` - 7단계 세밀 조정
- `super_fine_tune.py` - 11단계 초세밀 조정

### 디버깅
- `test_effects_debug.py` - 이펙트 체인 단계별 디버깅
- `check_all_stems.py` - 모든 6개 stem 확인

## 🚀 추천 워크플로우

### 1. 기본 사용 (빠르게)
```bash
# 1단계: 분리
python hystemfx/synth/scripts/test_separation_only.py "노래.mp3"

# 2단계: 최적 이펙트 적용 (Level 4.4)
python hystemfx/synth/scripts/apply_final_effects.py "output/노래_synth_only.wav"
```

### 2. 프리셋 테스트
```bash
# 분리
python hystemfx/synth/scripts/test_separation_only.py "노래.mp3"

# 다양한 프리셋 비교
python hystemfx/synth/scripts/compare_versions.py "output/노래_synth_only.wav"
```

### 3. 세밀 조정이 필요할 때
```bash
# 7단계 조정
python hystemfx/synth/scripts/fine_tune_effects.py "output/노래_synth_only.wav"

# 마음에 드는 레벨 주변 초세밀 조정
python hystemfx/synth/scripts/super_fine_tune.py "output/노래_synth_only.wav"
```

## 📊 최적 설정 (Level 4.4)

테스트 결과 가장 자연스럽고 균형잡힌 설정:

- **Compressor**: threshold=-19dB, ratio=3.4:1
- **Reverb**: room_size=0.38, wet_level=0.27
- **Chorus**: depth=0.32, mix=0.32
- **Gain**: +4.2dB

## 💡 팁

1. 항상 `test_separation_only.py`로 먼저 분리 품질 확인
2. 이펙트가 만족스럽지 않으면 `compare_versions.py`로 여러 버전 비교
3. `apply_final_effects.py`가 가장 검증된 설정
