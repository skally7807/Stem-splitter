import librosa
import librosa.display
import matplotlib.pyplot as plt
import numpy as np

filename = 'YUDABINBAND_-_(mp3.pm).mp3'
y, sr = librosa.load(filename, sr=44100)

plt.figure(figsize=(15, 5))
librosa.display.waveshow(y, sr=sr)

plt.show()