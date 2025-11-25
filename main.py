import os
from pydub import AudioSegment

base_path = "separated\htdemucs\YUDABINBAND_-_(mp3.pm)" 


try:
    bass = AudioSegment.from_wav(os.path.join(base_path, "bass.wav"))
    
    print("트랙 로드 완료!")

except FileNotFoundError:
    print("실패")
    exit()

print("2. 베이스 이펙트 적용 중...")
# 베이스 사운드 상승
processed_bass = bass + 6 


output_filename = "add_sound_BassBoost.mp3"
print(f"4. {output_filename} 파일로 저장 중...")

processed_bass.export(output_filename, format="mp3")

print("done!")