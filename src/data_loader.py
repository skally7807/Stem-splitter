import os
import librosa
import numpy as np
import warnings
import imageio_ffmpeg
from pydub import AudioSegment

# ffmpeg 경로 설정 (librosa가 찾을 수 있도록)
ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
os.environ['PATH'] += os.pathsep + os.path.dirname(ffmpeg_path)

# pydub에도 ffmpeg 경로 알려주기
AudioSegment.converter = ffmpeg_path
AudioSegment.ffmpeg = ffmpeg_path
AudioSegment.ffprobe = ffmpeg_path

# 경고 메시지 무시 (너무 많이 떠서)
warnings.filterwarnings('ignore')

def load_audio_robust(path, sr=22050, duration=None):
    """
    librosa로 로드 시도 후 실패하면 pydub으로 재시도하는 함수
    """
    try:
        # 1차 시도: librosa (빠름)
        y, _ = librosa.load(path, sr=sr, mono=True, duration=duration)
        return y
    except Exception as e:
        # 2차 시도: pydub (강력함)
        try:
            # pydub은 ffmpeg를 직접 사용하므로 더 강력함
            audio = AudioSegment.from_file(path)
            if duration:
                audio = audio[:int(duration*1000)] # pydub은 밀리초 단위
            
            # 샘플 레이트 변환 및 모노 변환
            audio = audio.set_frame_rate(sr).set_channels(1)
            
            # numpy 배열로 변환 (int16 -> float32 정규화)
            y = np.array(audio.get_array_of_samples()).astype(np.float32) / 32768.0
            return y
        except Exception as e2:
            # 둘 다 실패하면 에러 던짐
            raise e2

def load_paired_dataset(data_dir='data', sr=22050, duration=None):
    """
    [Teacher-Student 학습 전략]
    data/mixed 폴더(원본)와 data/stems/piano 폴더(SOTA 모델이 만든 정답)에서
    파일명이 일치하는 쌍(Pair)을 로드합니다.
    
    Args:
        data_dir (str): 데이터 루트 디렉토리
        sr (int): 샘플 레이트 (기본 22050Hz)
        duration (float): 로드할 길이 (None이면 전체 로드, 데모용으론 30.0 추천)
        
    Returns:
        mixed_list (list): 원본 오디오 배열 리스트 (X)
        target_list (list): 정답 피아노 오디오 배열 리스트 (Y)
    """
    mixed_dir = os.path.join(data_dir, 'mixed')
    target_dir = os.path.join(data_dir, 'piano_stems')
    
    mixed_list = []
    target_list = []
    
    # mixed 폴더에 있는 파일 목록 스캔
    if not os.path.exists(mixed_dir) or not os.path.exists(target_dir):
        print("오류: data/mixed 또는 data/stems/piano 폴더가 없습니다.")
        return [], []

    files = os.listdir(mixed_dir)
    valid_files = [f for f in files if f.lower().endswith(('.mp3', '.wav', '.flac'))]
    
    print(f"데이터 로딩 시작... (총 {len(valid_files)}개 파일 검색)")
    
    for filename in valid_files:
        # 확장자를 제외한 파일명(stem) 추출 (예: song1.mp3 -> song1)
        file_stem = os.path.splitext(filename)[0]
        
        # 1. Mixed 파일 경로
        mixed_path = os.path.join(mixed_dir, filename)
        
        # 2. Target 파일 경로 찾기 (확장자가 달라도 이름이 같으면 됨)
        # wav, mp3, flac 순서로 정답 파일이 있는지 확인
        target_path = None
        for ext in ['.wav', '.mp3', '.flac']:
            temp_path = os.path.join(target_dir, file_stem + ext)
            if os.path.exists(temp_path):
                target_path = temp_path
                break
        
        if target_path is None:
            print(f"건너뜀: '{filename}'의 짝이 되는 피아노 파일이 없습니다.")
            continue
            
        try:
            # load_audio_robust 함수 사용
            y_mixed = load_audio_robust(mixed_path, sr=sr, duration=duration)
            y_target = load_audio_robust(target_path, sr=sr, duration=duration)
            
            # 길이 맞추기
            min_len = min(len(y_mixed), len(y_target))
            y_mixed = y_mixed[:min_len]
            y_target = y_target[:min_len]
            
            # 너무 짧은 파일은 버림 (1초 미만)
            if min_len < sr:
                print(f"건너뜀: '{filename}' 파일이 너무 짧습니다.")
                continue

            mixed_list.append(y_mixed)
            target_list.append(y_target)
            
            print(f"로드 성공: {file_stem} (길이: {min_len/sr:.1f}초)")
            
        except Exception as e:
            print(f"에러 발생 ({filename}): {e}")
            print("  -> 이 파일은 건너뜁니다.")
            continue
            
    print(f"학습 데이터 준비 완료: 총 {len(mixed_list)}쌍")
    return mixed_list, target_list

# --- 테스트 실행 코드 ---
if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(current_dir)
    data_path = os.path.join(root_dir, 'data')
    
    X, Y = load_paired_dataset(data_dir=data_path, duration=10.0)