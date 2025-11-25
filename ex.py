import os
import torch
import shlex
import soundfile as sf
import demucs.separate

def my_save_audio_function(wav, path, **kwargs):
    """
    Demucs가 호출하는 방식: save_audio(source, path, **kwargs)
    """
    path = str(path)
    
    # 샘플 레이트(sample rate) 추출
    # 없으면 기본값 44100 사용
    sr = kwargs.get('samplerate', 44100)

    # GPU 텐서 -> CPU -> Numpy 변환
    if torch.is_tensor(wav):
        wav = wav.detach().cpu().numpy()
    
    # 차원 변환: (Channels, Time) -> (Time, Channels)
    # Soundfile은 (시간, 채널) 순서를 원하므로 뒤집어야 함
    if wav.ndim == 2 and wav.shape[0] < wav.shape[1]: 
        wav = wav.T 

    # 저장 (soundfile 사용)
    print(f"저장 중{os.path.basename(path)}")
    sf.write(path, wav, sr)

# Demucs의 저장 함수 교체
demucs.separate.save_audio = my_save_audio_function
print("시스템 패치 완료: 저장 함수를 성공적으로 교체했습니다.")
# =================================================================

def separate_audio_no_drums(input_file_path, output_dir="output"):
    
    device = "cuda" if torch.cuda.is_available() else "cpu"
    
    # segment 7초 설정
    cmd = (
        f'-n htdemucs_6s '
        f'--out "{output_dir}" '
        f'--device {device} '
        f'--jobs 4 '
        f'--segment 7 '
        f'"{input_file_path}"'
    )
    
    print(f"분리 시작: {os.path.basename(input_file_path)}")
    args = shlex.split(cmd)
    
    try:
        demucs.separate.main(args)
    except Exception as e:
        print(f"\n에러 발생: {e}")
        import traceback
        traceback.print_exc()
        return

    # 드럼 삭제
    song_name = os.path.basename(input_file_path).rsplit(".", 1)[0]
    result_path = os.path.join(output_dir, "htdemucs_6s", song_name)
    drum_file = os.path.join(result_path, "drums.wav")

    if os.path.exists(drum_file):
        try:
            os.remove(drum_file)
            print("Drums 트랙 삭제 완료")
        except:
            pass
    
    print(f"최종 완료 결과 경로: {result_path}")

if __name__ == "__main__":
    target_song = "YUDABINBAND_-_(mp3.pm).mp3" # 여기에 음성파일 이름 입력
    
    if os.path.exists(target_song):
        separate_audio_no_drums(target_song)
    else:
        print(f"파일을 찾을 수 없습니다: {target_song}")