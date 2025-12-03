"""
Level 5 주변 초세밀 조정 (4.0 ~ 6.0 사이를 0.2 단위로)
"""

from pedalboard import Pedalboard, Gain, Compressor, Reverb, Limiter, Chorus
from pedalboard.io import AudioFile
from pathlib import Path
import sys

def apply_fine_level(audio, sample_rate, level):
    """4.0~6.0을 0.2 단위로 세분화 (총 11단계)"""
    
    # level 값을 기준으로 파라미터 보간
    # 4.0 (약함) -> 5.0 (중간) -> 6.0 (강함)
    
    # Compressor threshold: -20dB -> -15dB
    comp_threshold = -20.0 + (level - 4.0) * 2.5
    
    # Compressor ratio: 3.0 -> 5.0
    comp_ratio = 3.0 + (level - 4.0) * 1.0
    
    # Reverb room_size: 0.35 -> 0.50
    reverb_room = 0.35 + (level - 4.0) * 0.075
    
    # Reverb wet_level: 0.25 -> 0.35
    reverb_wet = 0.25 + (level - 4.0) * 0.05
    
    # Chorus depth: 0.3 -> 0.4
    chorus_depth = 0.3 + (level - 4.0) * 0.05
    
    # Chorus mix: 0.3 -> 0.4
    chorus_mix = 0.3 + (level - 4.0) * 0.05
    
    # Gain: 4.0dB -> 5.0dB
    gain_db = 4.0 + (level - 4.0) * 0.5
    
    board = Pedalboard([
        Compressor(
            threshold_db=comp_threshold,
            ratio=comp_ratio,
            attack_ms=10.0,
            release_ms=80.0
        ),
        Reverb(
            room_size=reverb_room,
            wet_level=reverb_wet,
            damping=0.5,
            dry_level=0.8
        ),
        Chorus(
            rate_hz=1.0,
            depth=chorus_depth,
            mix=chorus_mix
        ),
        Gain(gain_db=gain_db),
        Limiter(threshold_db=-1.0)
    ])
    
    return board(audio, sample_rate)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("""
사용법: python super_fine_tune.py <파일경로>

Level 4.0 ~ 6.0 사이를 0.2 단위로 세분화 (총 11단계)
  4.0, 4.2, 4.4, 4.6, 4.8, 5.0, 5.2, 5.4, 5.6, 5.8, 6.0
        """)
        sys.exit(1)
    
    input_file = sys.argv[1]
    input_path = Path(input_file)
    
    if not input_path.exists():
        print(f"❌ 파일을 찾을 수 없습니다: {input_file}")
        sys.exit(1)
    
    print(f"\n{'='*60}")
    print(f"🎛️  초세밀 조정 (Level 4.0~6.0, 0.2 단위)")
    print(f"{'='*60}")
    print(f"📁 입력: {input_path.name}")
    print(f"{'='*60}\n")
    
    # 오디오 로드
    with AudioFile(str(input_path)) as f:
        audio = f.read(f.frames)
        sample_rate = f.samplerate
    
    print(f"입력 볼륨: {abs(audio).max():.4f}\n")
    
    # 4.0부터 6.0까지 0.2 단위로
    levels = [round(4.0 + i * 0.2, 1) for i in range(11)]
    
    for i, level in enumerate(levels, 1):
        print(f"{i}/11 처리 중: Level {level:.1f}...")
        
        # 이펙트 적용
        processed = apply_fine_level(audio, sample_rate, level)
        
        # 출력 볼륨 확인
        max_vol = abs(processed).max()
        print(f"      출력 볼륨: {max_vol:.4f}")
        
        # 저장
        level_str = str(level).replace('.', '_')
        output_file = input_path.parent / f"{input_path.stem}_lv{level_str}.wav"
        with AudioFile(str(output_file), 'w', sample_rate, processed.shape[0]) as f:
            f.write(processed)
        
        print(f"      저장: {output_file}\n")
    
    print(f"{'='*60}")
    print(f"✅ 완료! 11개 레벨:")
    print(f"")
    for level in levels:
        marker = " ← 이전 Level 5" if level == 5.0 else ""
        print(f"  Level {level:.1f}{marker}")
    print(f"")
    print(f"5.0 전후를 들어보고 완벽한 레벨을 찾으세요!")
    print(f"{'='*60}\n")
