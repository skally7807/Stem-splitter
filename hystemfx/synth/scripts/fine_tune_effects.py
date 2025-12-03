"""
minimal과 heavy 사이 세분화 버전
"""

from pedalboard import Pedalboard, Gain, Compressor, Reverb, Limiter, Chorus
from pedalboard.io import AudioFile
from pathlib import Path
import sys

def apply_level(audio, sample_rate, level):
    """레벨별 이펙트 적용 (1~7)"""
    
    if level == 1:
        # Level 1: 거의 원본
        board = Pedalboard([
            Compressor(threshold_db=-35.0, ratio=1.5),
            Reverb(room_size=0.2, wet_level=0.1),
            Gain(gain_db=2.0),
        ])
        
    elif level == 2:
        # Level 2: 매우 약함
        board = Pedalboard([
            Compressor(threshold_db=-30.0, ratio=2.0),
            Reverb(room_size=0.25, wet_level=0.15),
            Gain(gain_db=3.0),
        ])
        
    elif level == 3:
        # Level 3: 약함
        board = Pedalboard([
            Compressor(threshold_db=-25.0, ratio=2.5),
            Reverb(room_size=0.3, wet_level=0.2),
            Chorus(rate_hz=0.8, depth=0.2, mix=0.2),
            Gain(gain_db=3.5),
        ])
        
    elif level == 4:
        # Level 4: 중간 (균형)
        board = Pedalboard([
            Compressor(threshold_db=-20.0, ratio=3.0),
            Reverb(room_size=0.35, wet_level=0.25),
            Chorus(rate_hz=1.0, depth=0.3, mix=0.3),
            Gain(gain_db=4.0),
            Limiter(threshold_db=-1.0)
        ])
        
    elif level == 5:
        # Level 5: 중간-강함
        board = Pedalboard([
            Compressor(threshold_db=-18.0, ratio=4.0),
            Reverb(room_size=0.4, wet_level=0.3),
            Chorus(rate_hz=1.2, depth=0.35, mix=0.35),
            Gain(gain_db=4.5),
            Limiter(threshold_db=-1.0)
        ])
        
    elif level == 6:
        # Level 6: 강함
        board = Pedalboard([
            Compressor(threshold_db=-15.0, ratio=5.0),
            Reverb(room_size=0.5, wet_level=0.35),
            Chorus(rate_hz=1.5, depth=0.4, mix=0.4),
            Gain(gain_db=5.0),
            Limiter(threshold_db=-0.8)
        ])
        
    elif level == 7:
        # Level 7: 매우 강함
        board = Pedalboard([
            Compressor(threshold_db=-15.0, ratio=6.0),
            Chorus(rate_hz=1.5, depth=0.5, mix=0.5),
            Reverb(room_size=0.6, wet_level=0.4),
            Gain(gain_db=6.0),
            Limiter(threshold_db=-1.0)
        ])
    
    return board(audio, sample_rate)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("""
사용법: python fine_tune_effects.py <파일경로>

7단계 세밀 조정:
  Level 1 - 거의 원본
  Level 2 - 매우 약함 (minimal)
  Level 3 - 약함
  Level 4 - 중간 (균형)
  Level 5 - 중간-강함
  Level 6 - 강함
  Level 7 - 매우 강함 (heavy)
        """)
        sys.exit(1)
    
    input_file = sys.argv[1]
    input_path = Path(input_file)
    
    if not input_path.exists():
        print(f"❌ 파일을 찾을 수 없습니다: {input_file}")
        sys.exit(1)
    
    print(f"\n{'='*60}")
    print(f"🎛️  7단계 세밀 조정")
    print(f"{'='*60}")
    print(f"📁 입력: {input_path.name}")
    print(f"{'='*60}\n")
    
    # 오디오 로드
    with AudioFile(str(input_path)) as f:
        audio = f.read(f.frames)
        sample_rate = f.samplerate
    
    print(f"입력 볼륨: {abs(audio).max():.4f}\n")
    
    level_names = [
        "거의 원본",
        "매우 약함",
        "약함",
        "중간",
        "중간-강함",
        "강함",
        "매우 강함"
    ]
    
    for level in range(1, 8):
        print(f"{level}/7 처리 중: Level {level} ({level_names[level-1]})...")
        
        # 이펙트 적용
        processed = apply_level(audio, sample_rate, level)
        
        # 출력 볼륨 확인
        max_vol = abs(processed).max()
        print(f"     출력 볼륨: {max_vol:.4f}")
        
        # 저장
        output_file = input_path.parent / f"{input_path.stem}_level{level}.wav"
        with AudioFile(str(output_file), 'w', sample_rate, processed.shape[0]) as f:
            f.write(processed)
        
        print(f"     저장: {output_file}\n")
    
    print(f"{'='*60}")
    print(f"✅ 완료! 7개 레벨을 순서대로 들어보세요:")
    print(f"")
    for level in range(1, 8):
        print(f"Level {level}: {level_names[level-1]}")
    print(f"")
    print(f"마음에 드는 레벨을 찾아보세요!")
    print(f"{'='*60}\n")
