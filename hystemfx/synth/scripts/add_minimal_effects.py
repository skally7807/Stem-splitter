"""
최소 이펙트로 자연스럽게 (볼륨 보존)
"""

from pedalboard import Pedalboard, Gain, Compressor, Reverb, Limiter
from pedalboard.io import AudioFile
from pathlib import Path
import sys

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("사용법: python add_minimal_effects.py <파일경로>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    input_path = Path(input_file)
    
    if not input_path.exists():
        print(f"❌ 파일을 찾을 수 없습니다: {input_file}")
        sys.exit(1)
    
    print(f"\n{'='*60}")
    print(f"🎛️  최소 이펙트 적용 (자연스러움 중시)")
    print(f"{'='*60}")
    print(f"📁 입력: {input_path.name}")
    print(f"{'='*60}\n")
    
    # 오디오 로드
    with AudioFile(str(input_path)) as f:
        audio = f.read(f.frames)
        sample_rate = f.samplerate
    
    print(f"입력 볼륨: {abs(audio).max():.4f}")
    
    # 최소 이펙트 체인 (볼륨 보존!)
    board = Pedalboard([
        # 1. 약한 컴프레서 (다이내믹 보존)
        Compressor(
            threshold_db=-30.0,  # 높은 threshold
            ratio=2.0,           # 약한 압축
            attack_ms=10.0,
            release_ms=100.0
        ),
        
        # 2. 약한 리버브 (공간감만)
        Reverb(
            room_size=0.25,
            wet_level=0.15,      # 매우 약하게
            dry_level=0.95,      # 원음 거의 유지
        ),
        
        # 3. 볼륨 보정 (+3dB)
        Gain(gain_db=3.0),
        
        # 4. 리미터 (클리핑 방지)
        Limiter(threshold_db=-1.0)
    ])
    
    print("⏳ 이펙트 적용 중...\n")
    
    # 처리
    processed = board(audio, sample_rate)
    
    print(f"출력 볼륨: {abs(processed).max():.4f}\n")
    
    # 저장
    output_file = input_path.parent / f"{input_path.stem}_minimal.wav"
    with AudioFile(str(output_file), 'w', sample_rate, processed.shape[0]) as f:
        f.write(processed)
    
    print(f"✅ 완료!")
    print(f"📂 저장: {output_file}")
    print(f"{'='*60}\n")
