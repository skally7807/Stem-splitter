# HystemFX Audio I/O Module

## Overview

The `hystemfx.core.io` module provides standardized audio file I/O operations for the HystemFX audio processing pipeline.

## Standard Settings

- **Sample Rate**: 44,100 Hz (CD quality)
- **Channels**: Stereo (2 channels) by default
- **Normalization**: False by default (can be enabled at processing stages)
- **Format**: WAV (default), with support for other formats via soundfile

## Functions

### `load_audio()`

Load audio files with standardized settings.

```python
from hystemfx.core.io import load_audio

# Basic usage - load stereo audio at 44.1kHz
audio, sr = load_audio('input.wav')
print(f"Shape: {audio.shape}, Sample Rate: {sr}")
# Output: Shape: (220500, 2), Sample Rate: 44100

# Load as mono (for processing stages that require it)
audio_mono, sr = load_audio('input.wav', mono=True)
print(f"Shape: {audio_mono.shape}")
# Output: Shape: (220500,)

# Load with normalization (optional, for specific stages)
audio_norm, sr = load_audio('input.wav', normalize=True)
```

**Parameters:**
- `path`: Path to the audio file (str or Path)
- `sr`: Target sample rate (default: 44100 Hz)
- `mono`: Convert to mono if True (default: False)
- `normalize`: Normalize to [-1, 1] range if True (default: False)
- `dtype`: Data type for audio array (default: 'float32')

**Returns:**
- `audio`: numpy array - shape (samples,) for mono or (samples, channels) for stereo
- `sr`: sample rate (int)

---

### `save_audio()`

Save audio files with standardized settings.

```python
from hystemfx.core.io import save_audio
import numpy as np

# Create some audio data (1 second of stereo)
audio = np.random.randn(44100, 2) * 0.1

# Basic usage - save stereo audio
save_audio(audio, 'output/result.wav')

# Save with normalization
save_audio(audio, 'output/normalized.wav', normalize=True)

# Save with different bit depths
save_audio(audio, 'output/high_quality.wav', subtype='PCM_24')  # 24-bit
save_audio(audio, 'output/float.wav', subtype='FLOAT')  # 32-bit float
```

**Parameters:**
- `audio`: Audio data to save (numpy array)
- `path`: Target path for the audio file (str or Path)
- `sr`: Sample rate (default: 44100 Hz)
- `normalize`: Normalize before saving if True (default: False)
- `subtype`: Audio format subtype (default: 'PCM_16')
  - Options: 'PCM_16', 'PCM_24', 'PCM_32', 'FLOAT'
- `create_dirs`: Create parent directories if they don't exist (default: True)

---

### `get_audio_info()`

Get metadata about an audio file without loading the entire file.

```python
from hystemfx.core.io import get_audio_info

info = get_audio_info('input.wav')
print(f"Duration: {info['duration']:.2f}s")
print(f"Channels: {info['channels']}")
print(f"Sample rate: {info['samplerate']} Hz")
```

**Parameters:**
- `path`: Path to the audio file (str or Path)

**Returns:**
- Dictionary containing:
  - `samplerate`: Sample rate in Hz
  - `channels`: Number of channels
  - `duration`: Duration in seconds
  - `frames`: Total number of frames
  - `format`: File format (e.g., 'WAV')
  - `subtype`: Format subtype (e.g., 'PCM_16')

---

## Usage Philosophy

### When to use `normalize=False` (default)

- **Loading files**: Keep original dynamic range
- **Saving intermediate results**: Preserve processing chain dynamics
- **Final output**: Only if you want to maintain original levels

### When to use `normalize=True`

- **Specific processing stages**: When a processor expects normalized input
- **Preventing clipping**: When audio might exceed [-1, 1] range
- **Mastering/final output**: To achieve consistent output levels

### When to use `mono=False` (default)

- **Most processing**: Preserve stereo information
- **Effect chains**: Most effects work well with stereo
- **Final output**: Maintain stereo field

### When to use `mono=True`

- **Specific processors**: If a processor requires mono input
- **Analysis**: For pitch detection, onset detection, etc.
- **Size optimization**: When stereo information is not needed

---

## Examples

### Complete Processing Pipeline

```python
from hystemfx.core.io import load_audio, save_audio, get_audio_info

# 1. Check file info first
info = get_audio_info('input.wav')
print(f"Processing {info['duration']:.1f}s of audio...")

# 2. Load audio (stereo, no normalization by default)
audio, sr = load_audio('input.wav')

# 3. Process audio (your processing here)
# processed = your_processor(audio)

# 4. Save result (no normalization by default)
save_audio(audio, 'output/processed.wav')

# 5. Or save with normalization if needed
save_audio(audio, 'output/processed_normalized.wav', normalize=True)
```

### Batch Processing

```python
from pathlib import Path
from hystemfx.core.io import load_audio, save_audio

input_dir = Path('input/')
output_dir = Path('output/')

for audio_file in input_dir.glob('*.wav'):
    # Load
    audio, sr = load_audio(audio_file)
    
    # Process
    # processed = your_processor(audio)
    
    # Save with same filename
    output_path = output_dir / audio_file.name
    save_audio(audio, output_path)
```

---

## Technical Notes

### Sample Rate Handling

The module will automatically resample audio to 44.1kHz if the source file has a different sample rate. This uses librosa's high-quality resampling.

### Stereo to Mono Conversion

When `mono=True`, the conversion is done by averaging the channels:
```python
mono = np.mean(stereo, axis=1)
```

This preserves the center-panned content while mixing down L/R channels.

### Bit Depth Options

The `subtype` parameter controls the bit depth and encoding:
- `'PCM_16'`: 16-bit PCM (default) - good balance of quality and size
- `'PCM_24'`: 24-bit PCM - higher dynamic range
- `'PCM_32'`: 32-bit PCM - maximum integer precision
- `'FLOAT'`: 32-bit float - best for intermediate processing

---

## Installation

```bash
pip install -r requirements.txt
```

Or install dependencies individually:
```bash
pip install soundfile librosa numpy
```

---

## Testing

Run the test script to verify the module:

```bash
python test_io.py
```

This will test all major functions and create sample audio files in the `output/` directory.
