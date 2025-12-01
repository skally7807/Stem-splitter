"""
여러 버전을 한 번에 만들어서 비교하기
"""

from pedalboard import Pedalboard, Gain, Compressor, Reverb, Limiter, Chorus, Distortion
from pedalboard.io import AudioFile
from pathlib import Path
import sys

def apply_version(audio, sample_rate, version_name):
    """버전별 이펙트 적용"""
    
    if version_name == "original":
        # 원본 (이펙트 없음)
        board = Pedalboard([Gain(gain_db=0.0)])
        
    elif version_name == "minimal":
        # 최소 (자연스러움)
        board = Pedalboard([
            Compressor(threshold_db=-30.0, ratio=2.0),
            Reverb(room_size=0.25, wet_level=0.15),
            Gain(gain_db=3.0),
        ])
        
    elif version_name == "moderate":
        # 중간 (적당한 이펙트)
        board = Pedalboard([
            Compressor(threshold_db=-20.0, ratio=3.0),
            Reverb(room_size=0.35, wet_level=0.25),
            Chorus(rate_hz=1.0, depth=0.3, mix=0.3),
            Gain(gain_db=4.0),
            Limiter(threshold_db=-1.0)
        ])
        
    elif version_name == "heavy":
        # 강함 (극적인 변화)
        board = Pedalboard([
            Compressor(threshold_db=-15.0, ratio=6.0),
            Chorus(rate_hz=1.5, depth=0.5, mix=0.5),
            Reverb(room_size=0.6, wet_level=0.4),
            Gain(gain_db=6.0),
            Limiter(threshold_db=-0.5)
        ])
        
    elif version_name == "extreme":
        # 극단적 (확실한 차이)
        board = Pedalboard([
            Distortion(drive_db=5.0),
            Compressor(threshold_db=-10.0, ratio=10.0),
            Chorus(rate_hz=2.0, depth=0.7, mix=0.7),
            Reverb(room_size=0.8, wet_level=0.5),
            Gain(gain_db=8.0),
            Limiter(threshold_db=-0.3)
        ])
    
    return board(audio, sample_rate)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("""
사용법: python compare_versions.py <파일경로>

5가지 버전을 한 번에 만듭니다:
  1. original - 원본 (이펙트 없음)
  2. minimal  - 최소 (자연스러움)
  3. moderate - 중간 (적당함)
  4. heavy    - 강함 (극적)
  5. extreme  - 극단적 (확실한 차이)
        """)
        sys.exit(1)
    
    input_file = sys.argv[1]
    input_path = Path(input_file)
    
    if not input_path.exists():
        print(f"❌ 파일을 찾을 수 없습니다: {input_file}")
        sys.exit(1)
    
    print(f"\n{'='*60}")
    print(f"🎛️  5가지 버전 비교 생성")
    print(f"{'='*60}")
    print(f"📁 입력: {input_path.name}")
    print(f"{'='*60}\n")
    
    # 오디오 로드
    with AudioFile(str(input_path)) as f:
        audio = f.read(f.frames)
        sample_rate = f.samplerate
    
    print(f"입력 볼륨: {abs(audio).max():.4f}\n")
    
    versions = ["original", "minimal", "moderate", "heavy", "extreme"]
    
    for i, version in enumerate(versions, 1):
        print(f"{i}/5 처리 중: {version}...")
        
        # 이펙트 적용
        processed = apply_version(audio, sample_rate, version)
        
        # 출력 볼륨 확인
        max_vol = abs(processed).max()
        print(f"     출력 볼륨: {max_vol:.4f}")
        
        # 저장
        output_file = input_path.parent / f"{input_path.stem}_{version}.wav"
        with AudioFile(str(output_file), 'w', sample_rate, processed.shape[0]) as f:
            f.write(processed)
        
        print(f"     저장: {output_file}\n")
    
    print(f"{'='*60}")
    print(f"✅ 완료! 5개 파일을 순서대로 들어보세요:")
    print(f"")
    print(f"1. original - 원본 (이펙트 없음)")
    print(f"2. minimal  - 살짝만 (자연스러움)")
    print(f"3. moderate - 적당하게 (균형)")
    print(f"4. heavy    - 강하게 (극적)")
    print(f"5. extreme  - 극단적 (확실한 차이)")
    print(f"")
    print(f"차이를 비교해보고 마음에 드는 버전을 선택하세요!")
    print(f"{'='*60}\n")
