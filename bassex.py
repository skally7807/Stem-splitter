import os
import sys
import subprocess
import demucs.separate
import shutil

def run_demucs_bass_only(filename):
    song_name = os.path.splitext(filename)[0]
    output_path = os.path.join("separated", "htdemucs", song_name, "bass.wav")

    cmd = ["-n", "htdemucs", "--two-stems", "bass", filename]
    
    try:
        # Demucs 실행
        demucs.separate.main(cmd)
        
        # 4. 결과 확인
        if os.path.exists(output_path):
            print(f"베이스 파일이 생성되었습니다: {output_path}")
            print("이제 이 파일로 이펙팅 작업을 할 수 있습니다.")
        else:
            print("실패")
            
    except Exception as e:
        print(f"\n에러 발생: {e}")

if __name__ == "__main__":
    target_song = "YUDABINBAND_-_(mp3.pm).mp3" 
    
    if os.path.exists(target_song):
        run_demucs_bass_only(target_song)
    else:
        print(f"'{target_song}' 파일을 찾을 수 없습니다. 파일 이름을 확인해주세요.")