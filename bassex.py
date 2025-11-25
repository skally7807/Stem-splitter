import os
import sys
import subprocess
import demucs.separate
import shutil

def run_demucs_bass_only(filename):
    print(f"--- 작업 시작: {filename} ---")
    
    # 1. FFmpeg가 잘 들어왔는지 확인
    if not (os.path.exists("ffmpeg.exe") or shutil.which("ffmpeg")):
        print("[오류] ffmpeg.exe를 찾을 수 없습니다!")
        print("다운로드 받은 ffmpeg.exe를 이 파이썬 파일 옆에 두셔야 합니다.")
        return

    # 2. 결과가 저장될 경로 미리 계산
    # 예: separated/htdemucs/노래제목/bass.wav
    song_name = os.path.splitext(filename)[0]
    output_path = os.path.join("separated", "htdemucs", song_name, "bass.wav")

    # 3. Demucs 실행 명령어 구성
    # --two-stems bass: 베이스와 나머지로만 분리 (시간 절약)
    cmd = ["-n", "htdemucs", "--two-stems", "bass", filename]
    
    print("🤖 AI가 베이스를 분리하는 중입니다... (1~3분 소요)")
    
    try:
        # Demucs 실행
        demucs.separate.main(cmd)
        
        # 4. 결과 확인
        if os.path.exists(output_path):
            print("\n✅ 성공!!!")
            print(f"베이스 파일이 생성되었습니다: {output_path}")
            print("이제 이 파일로 이펙팅 작업을 할 수 있습니다.")
        else:
            print("\n❌ 실패: 에러는 없었지만 파일이 안 보입니다.")
            
    except Exception as e:
        print(f"\n❌ 에러 발생: {e}")

if __name__ == "__main__":
    # 여기에 분리할 파일명을 정확히 적으세요
    # 파일이 프로젝트 폴더에 있어야 합니다.
    target_song = "YUDABINBAND_-_(mp3.pm).mp3" 
    
    if os.path.exists(target_song):
        run_demucs_bass_only(target_song)
    else:
        print(f"'{target_song}' 파일을 찾을 수 없습니다. 파일 이름을 확인해주세요.")