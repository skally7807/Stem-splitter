import numpy as np
import joblib
from sklearn.ensemble import RandomForestRegressor
from data_loader import load_paired_dataset
from utils import audio_to_spectrogram, compute_soft_mask
from features import extract_features

def train():
    # 1. 데이터 불러오기
    print("데이터를 불러옵니다...")
    # 너무 길면 오래 걸리니까 30초만 사용
    X_list, Y_list = load_paired_dataset(duration=30.0)

    if len(X_list) == 0:
        print("데이터가 없어서 종료합니다.")
        return

    X_train = []
    y_train = []

    print("학습 데이터를 만드는 중...")
    for i in range(len(X_list)):
        # 오디오 가져오기
        x_audio = X_list[i]
        y_audio = Y_list[i]

        # 특징 추출 (입력 데이터)
        # 결과 모양: (25, 시간)
        features = extract_features(x_audio, sr=22050)
        
        # 정답 마스크 만들기
        mix_mag, _ = audio_to_spectrogram(x_audio)
        piano_mag, _ = audio_to_spectrogram(y_audio)
        mask = compute_soft_mask(mix_mag, piano_mag)
        
        # 모델에 넣으려면 (시간, 특징) 모양이어야 해서 뒤집음(Transpose)
        features = features.T  # (시간, 25)
        mask = mask.T          # (시간, 1025)
        
        # 시간 길이가 안 맞으면 맞춤 (가끔 1프레임 차이남)
        min_len = min(len(features), len(mask))
        features = features[:min_len]
        mask = mask[:min_len]

        X_train.append(features)
        y_train.append(mask)

    # 리스트를 하나의 큰 배열로 합치기
    X_train = np.concatenate(X_train, axis=0)
    y_train = np.concatenate(y_train, axis=0)

    print(f"학습 데이터 크기: {X_train.shape}")
    print("AI 학습 시작! (시간이 좀 걸릴 수 있음)")

    # 랜덤 포레스트 모델 생성
    # n_jobs=-1은 컴퓨터 성능을 다 쓴다는 뜻
    model = RandomForestRegressor(n_estimators=10, max_depth=10, n_jobs=-1, random_state=42)
    model.fit(X_train, y_train)

    # 모델 저장
    print("모델 저장 중...")
    joblib.dump(model, 'piano_model.joblib')
    print("학습 완료! piano_model.joblib 파일이 생성되었습니다.")

if __name__ == "__main__":
    train()
