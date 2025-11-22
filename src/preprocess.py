
import librosa
import numpy as np
from .config import SAMPLE_RATE, N_FFT, HOP_LENGTH
from stft import stft   

"""
- 오디오 파일(mp3/wav) 하나 로드
- STFT 적용해서 스펙트로그램 생성
- Magnitude 출력 크기 확인
"""


def load_audio(path: str, sr: int = SAMPLE_RATE) -> np.ndarray:
    """
    오디오 파일(mp3, wav 등)을 librosa로 로드합니다.

    Params
    -------
    path : str
        오디오 파일 경로
    sr : int
        샘플 레이트 (config에서 가져옴)

    Returns
    -------
    y : np.ndarray
        로드된 1D 오디오 파형 데이터 (float32)
    """
    # mono=True → 스테레오여도 왼/오른쪽을 하나의 채널로 합침
    y, _ = librosa.load(path, sr=sr, mono=True)
    return y


def compute_spectrogram(y: np.ndarray):
    """
    오디오 파형 → Magnitude 스펙트로그램 변환.



    Params
    -------
    y : np.ndarray
        오디오 파형

    Returns
    -------
    mag : np.ndarray
        Magnitude 스펙트로그램 (Freq x Time)
    """
    mag, phase = stft(y, sr=SAMPLE_RATE, n_fft=N_FFT, hop_length=HOP_LENGTH)
    return mag

