"""
Audio I/O module for HystemFX

Standard settings:
- Sample Rate: 44,100 Hz (constant across all operations)
- Channels: Stereo (2 channels) by default
- Normalization: False by default (can be enabled at processing stages)
- Format: WAV (default), with support for other formats via soundfile
"""

import numpy as np
import soundfile as sf
from pathlib import Path
from typing import Tuple, Optional, Union

# Global configuration
DEFAULT_SAMPLE_RATE = 44100  # Standard CD quality sample rate


def load_audio(
    path: Union[str, Path],
    sr: int = DEFAULT_SAMPLE_RATE,
    mono: bool = False,
    normalize: bool = False,
    dtype: str = 'float32'
) -> Tuple[np.ndarray, int]:
    """
    Load audio file with standardized settings.
    
    :param path: Path to the audio file
    :type path: str or Path
    :param sr: Target sample rate (default: 44100 Hz)
    :type sr: int
    :param mono: Convert to mono if True, keep stereo if False (default: False)
    :type mono: bool
    :param normalize: Normalize audio to [-1, 1] range if True (default: False)
    :type normalize: bool
    :param dtype: Data type for the audio array (default: 'float32')
    :type dtype: str
    :return: Tuple of (audio_data, sample_rate)
        - audio_data: numpy array of shape (samples,) for mono or (samples, channels) for stereo
        - sample_rate: sample rate of the audio
    :rtype: Tuple[np.ndarray, int]
    
    :raises FileNotFoundError: If the audio file does not exist
    :raises RuntimeError: If there's an error reading the audio file
    
    Example:
        >>> audio, sr = load_audio('input.wav')
        >>> print(f"Shape: {audio.shape}, Sample Rate: {sr}")
        Shape: (220500, 2), Sample Rate: 44100
        
        >>> # Load as mono
        >>> audio_mono, sr = load_audio('input.wav', mono=True)
        >>> print(f"Shape: {audio_mono.shape}")
        Shape: (220500,)
    """
    path = Path(path)
    
    if not path.exists():
        raise FileNotFoundError(f"Audio file not found: {path}")
    
    try:
        # Load audio file
        audio, original_sr = sf.read(str(path), dtype=dtype)
        
        # Resample if necessary
        if original_sr != sr:
            import librosa
            audio = librosa.resample(audio.T, orig_sr=original_sr, target_sr=sr).T
        
        # Convert to mono if requested (processor stage can also do this)
        if mono and audio.ndim > 1:
            audio = np.mean(audio, axis=1)
        
        # Normalize if requested
        if normalize:
            max_val = np.abs(audio).max()
            if max_val > 0:
                audio = audio / max_val
        
        return audio, sr
        
    except Exception as e:
        raise RuntimeError(f"Error loading audio file {path}: {str(e)}")


def save_audio(
    audio: np.ndarray,
    path: Union[str, Path],
    sr: int = DEFAULT_SAMPLE_RATE,
    normalize: bool = False,
    subtype: str = 'PCM_16',
    create_dirs: bool = True
) -> None:
    """
    Save audio file with standardized settings.
    
    :param audio: Audio data to save (shape: (samples,) for mono or (samples, channels) for stereo)
    :type audio: np.ndarray
    :param path: Target path to save the audio file
    :type path: str or Path
    :param sr: Sample rate (default: 44100 Hz)
    :type sr: int
    :param normalize: Normalize audio before saving if True (default: False)
    :type normalize: bool
    :param subtype: Audio format subtype (default: 'PCM_16' for 16-bit WAV)
        Common options: 'PCM_16', 'PCM_24', 'PCM_32', 'FLOAT'
    :type subtype: str
    :param create_dirs: Create parent directories if they don't exist (default: True)
    :type create_dirs: bool
    :return: None
    
    :raises ValueError: If audio data is invalid
    :raises RuntimeError: If there's an error writing the audio file
    
    Example:
        >>> audio = np.random.randn(44100, 2)  # 1 second of stereo audio
        >>> save_audio(audio, 'output/result.wav')
        
        >>> # Save with normalization
        >>> save_audio(audio, 'output/normalized.wav', normalize=True)
        
        >>> # Save as 24-bit audio
        >>> save_audio(audio, 'output/high_quality.wav', subtype='PCM_24')
    """
    path = Path(path)
    
    # Create parent directories if needed
    if create_dirs:
        path.parent.mkdir(parents=True, exist_ok=True)
    
    # Validate audio data
    if not isinstance(audio, np.ndarray):
        raise ValueError("Audio data must be a numpy array")
    
    if audio.size == 0:
        raise ValueError("Audio data is empty")
    
    # Normalize if requested
    if normalize:
        max_val = np.abs(audio).max()
        if max_val > 0:
            audio = audio / max_val
    
    try:
        # Save audio file
        sf.write(str(path), audio, sr, subtype=subtype)
        
    except Exception as e:
        raise RuntimeError(f"Error saving audio file {path}: {str(e)}")


def get_audio_info(path: Union[str, Path]) -> dict:
    """
    Get information about an audio file without loading the full data.
    
    :param path: Path to the audio file
    :type path: str or Path
    :return: Dictionary containing audio information (samplerate, channels, duration, format, etc.)
    :rtype: dict
    
    :raises FileNotFoundError: If the audio file does not exist
    
    Example:
        >>> info = get_audio_info('input.wav')
        >>> print(f"Duration: {info['duration']:.2f}s, Channels: {info['channels']}")
        Duration: 5.00s, Channels: 2
    """
    path = Path(path)
    
    if not path.exists():
        raise FileNotFoundError(f"Audio file not found: {path}")
    
    info = sf.info(str(path))
    
    return {
        'samplerate': info.samplerate,
        'channels': info.channels,
        'duration': info.duration,
        'frames': info.frames,
        'format': info.format,
        'subtype': info.subtype,
    }