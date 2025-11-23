
import matplotlib.pyplot as plt
import numpy as np
import librosa

"""
- 스펙트로그램 한 장을 이미지로 저장해 확인하기
"""


def save_spectrogram(mag: np.ndarray, path: str):
    """
    Magnitude 스펙트로그램을 사람이 보기 쉬운 dB(데시벨) 스케일로 변환하여
    PNG 이미지로 저장합니다.

    Params
    -------
    mag : np.ndarray
        Magnitude 스펙트로그램 (Freq x Time)
    path : str
        저장할 이미지 경로
    """

    # dB 스케일로 변환 (로그 스케일: 작은 값도 잘 보임)
    mag_db = librosa.amplitude_to_db(mag, ref=np.max)

    # 이미지 생성
    plt.figure(figsize=(6, 4))
    plt.imshow(mag_db, aspect='auto', origin='lower', cmap='magma')
    plt.axis('off')  # 축 숨김
    plt.tight_layout()

    # 파일 저장
    plt.savefig(path)
    plt.close()

