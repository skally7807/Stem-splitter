"""
최종 완성 버전: Level 4.4 이펙트
"""

from pedalboard import Pedalboard, Gain, Compressor, Reverb, Limiter, Chorus
from pedalboard.io import AudioFile
from pathlib import Path
import sys

def apply_level_44_effects(audio, sample_rate):
    """Level 4.4 파라미터로 이펙트 적용"""
    
    board = Pedalboard([
        # Compressor (적당한 압축)
        Compressor(
            threshold_db=-19.0,
            ratio=3.4,
            attack_ms=10.0,
            release_ms=80.0
        ),
        
        # Reverb (자연스러운 공간감)
        Reverb(
            room_size=0.38,
            wet_level=0.27,
            damping=0.5,
            dry_level=0.8
        ),
        
        # Chorus (살짝 풍성하게)
        Chorus(
            rate_hz=1.0,
            depth=0.32,
            mix=0.32
        ),
        
        # Gain (적당한 볼륨 보정)
        Gain(gain_db=4.2),
        
        # Limiter (클리핑 방지)
        Limiter(threshold_db=-1.0)
    ])
    
    return board(audio, sample_rate)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("""
사용법: python apply_final_effects.py <파일경로>

Level 4.4 최적화 설정으로 이펙트를 적용합니다.
        """)
        sys.exit(1)
    
    input_file = sys.argv[1]
    input_path = Path(input_file)
    
    if not input_path.exists():
        print(f"❌ 파일을 찾을 수 없습니다: {input_file}")
        sys.exit(1)
    
    print(f"\n{'='*60}")
    print(f"🎛️  최종 이펙트 적용 (Level 4.4)")
    print(f"{'='*60}")
    print(f"📁 입력: {input_path.name}")
    print(f"")
    print(f"설정:")
    print(f"  Compressor: threshold=-19dB, ratio=3.4:1")
    print(f"  Reverb: room=0.38, wet=0.27")
    print(f"  Chorus: depth=0.32, mix=0.32")
    print(f"  Gain: +4.2dB")
    print(f"{'='*60}\n")
    
    # 오디오 로드
    with AudioFile(str(input_path)) as f:
        audio = f.read(f.frames)
        sample_rate = f.samplerate
    
    print(f"입력 볼륨: {abs(audio).max():.4f}")
    print("⏳ 이펙트 적용 중...\n")
    
    # 이펙트 적용
    processed = apply_level_44_effects(audio, sample_rate)
    
    print(f"출력 볼륨: {abs(processed).max():.4f}\n")
    
    # 저장
    output_file = input_path.parent / f"{input_path.stem}_final.wav"
    with AudioFile(str(output_file), 'w', sample_rate, processed.shape[0]) as f:
        f.write(processed)
    
    print(f"✅ 완료!")
    print(f"📂 저장: {output_file}")
    print(f"{'='*60}\n")
