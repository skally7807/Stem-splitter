import librosa
import librosa.display
import matplotlib.pyplot as plt
import numpy as np
from src.stft import stft
from src.istft import istft

FILENAME = 'YUDABINBAND_-_(mp3.pm).mp3'
CUTOFF_HZ = 200
N_FFT = 2048
y, sr = librosa.load(FILENAME, sr=44100)

mag, phase = stft(y, sr, n_fft=N_FFT)

cutoff_bin = int(CUTOFF_HZ * N_FFT / sr)

mag_bass = mag.copy()
mag_bass[cutoff_bin:, :] = 0 
plt.figure(figsize=(12, 10))
plt.subplot(2, 1, 1)
mag_db = librosa.amplitude_to_db(mag, ref=np.max)
librosa.display.specshow(mag_db, sr=sr, x_axis='time', y_axis='log')
plt.colorbar(format='%+2.0f dB')
plt.title('Original')

# bass
plt.subplot(2, 1, 2)
mag_bass_db = librosa.amplitude_to_db(mag_bass, ref=np.max)
librosa.display.specshow(mag_bass_db, sr=sr, x_axis='time', y_axis='log')
plt.colorbar(format='%+2.0f dB')
plt.title(f'Bass Only (Under {CUTOFF_HZ}Hz)')

plt.tight_layout()
plt.show()