"""
신디사이저/피아노/키보드 분리 및 이펙트 처리 사용 예제
Synth Module Usage Examples
"""

import numpy as np
from pathlib import Path

# 예제 1: 기본 사용 - 파이프라인으로 한 번에 처리
def example_basic_pipeline():
    """가장 간단한 사용 방법: 믹스에서 신디사이저 분리하고 이펙트 적용"""
    from hystemfx.synth import SynthPipeline
    
    # 파이프라인 생성
    pipeline = SynthPipeline(
        separation_model="htdemucs_6s",
        device="cuda",  # 또는 "cpu"
        effect_preset="default"
    )
    
    # 파일 처리
    pipeline.process_file(
        input_path="input_song.wav",
        output_path="output_synth.wav",
        apply_effects=True
    )
    print("✓ 처리 완료!")


# 예제 2: 분리만 수행 (이펙트 없이)
def example_separation_only():
    """음원 분리만 수행하고 이펙트는 적용하지 않음"""
    from hystemfx.synth import SynthSeparator
    
    separator = SynthSeparator(model_name="htdemucs_6s")
    
    # 파일에서 직접 분리
    synth_audio = separator.separate_file(
        input_path="input_song.wav",
        output_path="separated_synth.wav",
        return_audio=True
    )
    
    print(f"분리된 오디오 shape: {synth_audio.shape}")


# 예제 3: 이펙트만 적용 (이미 분리된 오디오에)
def example_effects_only():
    """이미 분리된 신디사이저 오디오에 이펙트만 적용"""
    from hystemfx.synth import SynthEffectsChain
    from pedalboard.io import AudioFile
    
    # 이펙트 체인 생성
    effects = SynthEffectsChain(
        comp_ratio=4.0,           # Compressor 비율
        eq_mid_gain_db=3.0,       # Mid 주파수 부스트
        chorus_mix=0.4,           # Chorus 믹스
        reverb_room_size=0.5,     # Reverb 룸 사이즈
        reverb_wet_level=0.3      # Reverb 양
    )
    
    # 오디오 로드
    with AudioFile("separated_synth.wav") as f:
        audio = f.read(f.frames)
        sample_rate = f.samplerate
    
    # 이펙트 적용
    processed = effects.process(audio, sample_rate)
    
    # 저장
    with AudioFile("synth_with_effects.wav", 'w', sample_rate, processed.shape[0]) as f:
        f.write(processed)
    
    print("✓ 이펙트 적용 완료!")


# 예제 4: 프리셋 사용
def example_presets():
    """다양한 프리셋으로 이펙트 적용"""
    from hystemfx.synth import apply_synth_effects
    from pedalboard.io import AudioFile
    
    # 오디오 로드
    with AudioFile("separated_synth.wav") as f:
        audio = f.read(f.frames)
        sample_rate = f.samplerate
    
    # 다양한 프리셋 테스트
    presets = ["default", "bright", "warm", "spacious", "tight"]
    
    for preset in presets:
        processed = apply_synth_effects(
            audio, 
            sample_rate, 
            preset=preset
        )
        
        # 저장
        output_path = f"synth_{preset}.wav"
        with AudioFile(output_path, 'w', sample_rate, processed.shape[0]) as f:
            f.write(processed)
        
        print(f"✓ {preset} 프리셋 적용 완료 -> {output_path}")


# 예제 5: 커스텀 파라미터로 이펙트 체인 구성
def example_custom_parameters():
    """세밀한 파라미터 조정"""
    from hystemfx.synth import SynthEffectsChain
    from pedalboard.io import AudioFile
    
    # 커스텀 이펙트 체인
    effects = SynthEffectsChain(
        # Noise Gate
        gate_threshold_db=-55.0,
        
        # High-pass Filter
        highpass_cutoff_hz=100.0,
        
        # Compressor
        comp_threshold_db=-18.0,
        comp_ratio=3.5,
        comp_attack_ms=8.0,
        comp_release_ms=60.0,
        
        # EQ
        eq_low_gain_db=1.0,       # 200Hz 부근
        eq_mid_gain_db=2.5,       # 1.5kHz (presence)
        eq_high_gain_db=1.5,      # 8kHz (brightness)
        
        # Chorus
        chorus_rate_hz=1.0,
        chorus_depth=0.3,
        chorus_mix=0.35,
        
        # Reverb
        reverb_room_size=0.4,
        reverb_damping=0.6,
        reverb_wet_level=0.28,
        reverb_dry_level=0.8,
        reverb_width=1.0,
        
        # Limiter
        limiter_threshold_db=-0.5
    )
    
    # 파라미터 확인
    print("현재 파라미터:")
    for key, value in effects.get_params().items():
        print(f"  {key}: {value}")
    
    # 오디오 처리
    with AudioFile("separated_synth.wav") as f:
        audio = f.read(f.frames)
        sample_rate = f.samplerate
    
    processed = effects.process(audio, sample_rate)
    
    # 저장
    with AudioFile("synth_custom.wav", 'w', sample_rate, processed.shape[0]) as f:
        f.write(processed)
    
    print("✓ 커스텀 파라미터 적용 완료!")


# 예제 6: 배치 처리
def example_batch_processing():
    """여러 파일 한 번에 처리"""
    from hystemfx.synth import SynthPipeline
    
    pipeline = SynthPipeline(
        separation_model="htdemucs_6s",
        effect_preset="bright"
    )
    
    # 입력 파일 리스트
    input_files = [
        "song1.wav",
        "song2.wav",
        "song3.wav"
    ]
    
    # 배치 처리
    pipeline.batch_process(
        input_files=input_files,
        output_dir="output_synth",
        apply_effects=True,
        randomize_effects=False  # True로 하면 각 파일마다 랜덤 이펙트
    )


# 예제 7: 랜덤화된 이펙트로 데이터 증강
def example_data_augmentation():
    """데이터 증강을 위한 랜덤 이펙트"""
    from hystemfx.synth import RandomizedSynthEffects
    from pedalboard.io import AudioFile
    
    # 랜덤 이펙트 생성기
    randomizer = RandomizedSynthEffects(
        gate_threshold_range=(-70.0, -50.0),
        comp_ratio_range=(2.0, 5.0),
        eq_mid_gain_range=(0.0, 4.0),
        chorus_mix_range=(0.2, 0.5),
        reverb_room_size_range=(0.2, 0.5),
        seed=42  # 재현성을 위한 시드
    )
    
    # 오디오 로드
    with AudioFile("separated_synth.wav") as f:
        audio = f.read(f.frames)
        sample_rate = f.samplerate
    
    # 여러 버전 생성
    for i in range(5):
        processed, params = randomizer.process(audio, sample_rate)
        
        print(f"\n버전 {i+1} 파라미터:")
        print(f"  Compressor Ratio: {params['comp_ratio']:.2f}")
        print(f"  Mid EQ Gain: {params['eq_mid_gain_db']:.2f} dB")
        print(f"  Reverb Room Size: {params['reverb_room_size']:.2f}")
        
        # 저장
        output_path = f"synth_augmented_{i+1}.wav"
        with AudioFile(output_path, 'w', sample_rate, processed.shape[0]) as f:
            f.write(processed)
        
        print(f"  ✓ 저장: {output_path}")


# 예제 8: 모든 stem 확인하기
def example_all_stems():
    """분리된 모든 stem 확인"""
    from hystemfx.synth import SynthSeparator
    from pedalboard.io import AudioFile
    
    separator = SynthSeparator()
    
    # 오디오 로드
    with AudioFile("input_song.wav") as f:
        audio = f.read(f.frames)
        sample_rate = f.samplerate
    
    # 모든 stem 분리
    stems = separator.separate(audio, sample_rate, return_all_stems=True)
    
    # stem 이름: drums, bass, other, vocals, guitar, piano
    for stem_name, stem_audio in stems.items():
        output_path = f"stem_{stem_name}.wav"
        with AudioFile(output_path, 'w', sample_rate, stem_audio.shape[0]) as f:
            f.write(stem_audio)
        print(f"✓ {stem_name}: {output_path}")


# 예제 9: NumPy 배열로 직접 처리
def example_numpy_processing():
    """NumPy 배열로 직접 처리하기"""
    from hystemfx.synth import process_synth_from_mix
    from pedalboard.io import AudioFile
    
    # 오디오를 NumPy 배열로 로드
    with AudioFile("input_song.wav") as f:
        audio = f.read(f.frames)
        sample_rate = f.samplerate
    
    print(f"입력 오디오 shape: {audio.shape}")
    
    # 처리
    processed = process_synth_from_mix(
        audio=audio,
        sample_rate=sample_rate,
        apply_effects=True,
        effect_preset="spacious",
        device="cuda"
    )
    
    print(f"출력 오디오 shape: {processed.shape}")
    
    # 저장
    with AudioFile("output_numpy.wav", 'w', sample_rate, processed.shape[0]) as f:
        f.write(processed)


# 예제 10: 파라미터 동적 업데이트
def example_dynamic_update():
    """실시간으로 파라미터 변경"""
    from hystemfx.synth import SynthEffectsChain
    from pedalboard.io import AudioFile
    
    # 이펙트 체인 생성
    effects = SynthEffectsChain()
    
    # 오디오 로드
    with AudioFile("separated_synth.wav") as f:
        audio = f.read(f.frames)
        sample_rate = f.samplerate
    
    # 첫 번째 처리
    processed1 = effects.process(audio, sample_rate)
    with AudioFile("synth_v1.wav", 'w', sample_rate, processed1.shape[0]) as f:
        f.write(processed1)
    
    # 파라미터 업데이트
    effects.update_params(
        comp_ratio=6.0,
        reverb_room_size=0.7,
        chorus_mix=0.5
    )
    
    # 두 번째 처리 (새 파라미터로)
    processed2 = effects.process(audio, sample_rate)
    with AudioFile("synth_v2.wav", 'w', sample_rate, processed2.shape[0]) as f:
        f.write(processed2)
    
    print("✓ 두 가지 버전 생성 완료!")


if __name__ == "__main__":
    print("=== 신디사이저/피아노/키보드 분리 및 이펙트 처리 예제 ===\n")
    
    # 실행할 예제 선택
    print("사용 가능한 예제:")
    print("1. 기본 파이프라인 사용")
    print("2. 분리만 수행")
    print("3. 이펙트만 적용")
    print("4. 프리셋 사용")
    print("5. 커스텀 파라미터")
    print("6. 배치 처리")
    print("7. 데이터 증강 (랜덤 이펙트)")
    print("8. 모든 stem 확인")
    print("9. NumPy 배열 처리")
    print("10. 파라미터 동적 업데이트")
    
    # 예제 1 실행 (기본)
    # example_basic_pipeline()
