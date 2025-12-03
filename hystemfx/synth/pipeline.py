"""
Synth/Piano/Keyboard Processing Pipeline
신디사이저, 피아노, 키보드 분리 및 이펙트 처리 통합 파이프라인
"""

import numpy as np
from typing import Optional, Union, Dict
from pathlib import Path

from .separator import SynthSeparator, separate_synth
from .effects import SynthEffectsChain, RandomizedSynthEffects, apply_synth_effects


class SynthPipeline:
    """
    완전한 신디사이저/피아노/키보드 처리 파이프라인
    
    음원 분리 -> 이펙트 적용의 전체 프로세스를 관리합니다.
    """
    
    def __init__(
        self,
        separation_model: str = "htdemucs_6s",
        device: Optional[str] = None,
        effect_preset: str = "default",
        **effect_params
    ):
        """
        Parameters:
            separation_model (str): Demucs 모델 이름
            device (str): 'cuda', 'cpu' 또는 None
            effect_preset (str): 이펙트 프리셋 ("default", "bright", "warm", "spacious", "tight")
            **effect_params: 추가 이펙트 파라미터
        """
        self.separator = SynthSeparator(model_name=separation_model, device=device)
        self.effect_preset = effect_preset
        self.effect_params = effect_params
        
    def process(
        self,
        audio: np.ndarray,
        sample_rate: int,
        apply_effects: bool = True,
        return_all_stems: bool = False
    ) -> Union[np.ndarray, Dict[str, np.ndarray]]:
        """
        완전한 파이프라인 실행: 분리 -> 이펙트 적용
        
        Parameters:
            audio (np.ndarray): 입력 오디오 (전체 믹스)
            sample_rate (int): 샘플레이트
            apply_effects (bool): 이펙트 체인을 적용할지 여부
            return_all_stems (bool): 모든 stem을 반환할지 여부
            
        Returns:
            np.ndarray 또는 Dict: 처리된 신디사이저 오디오 또는 모든 stem
        """
        print("Step 1/2: Separating synth/piano/keyboard from mix...")
        
        # 음원 분리
        if return_all_stems:
            stems = self.separator.separate(audio, sample_rate, return_all_stems=True)
            synth_audio = stems["piano"]
        else:
            synth_audio = self.separator.separate(audio, sample_rate, return_all_stems=False)
        
        # 이펙트 적용
        if apply_effects:
            print("Step 2/2: Applying effects chain...")
            processed = apply_synth_effects(
                synth_audio,
                sample_rate,
                preset=self.effect_preset,
                **self.effect_params
            )
            
            if return_all_stems:
                stems["piano_processed"] = processed
                return stems
            else:
                return processed
        else:
            if return_all_stems:
                return stems
            else:
                return synth_audio
    
    def process_file(
        self,
        input_path: Union[str, Path],
        output_path: Optional[Union[str, Path]] = None,
        apply_effects: bool = True,
        save_separated_only: bool = False
    ) -> Optional[np.ndarray]:
        """
        파일에서 직접 처리
        
        Parameters:
            input_path (str | Path): 입력 오디오 파일 경로
            output_path (str | Path): 출력 파일 경로
            apply_effects (bool): 이펙트를 적용할지 여부
            save_separated_only (bool): 분리된 오디오만 저장할지 여부 (이펙트 없이)
            
        Returns:
            np.ndarray: 처리된 오디오 (output_path가 None이 아닐 때)
        """
        try:
            from pedalboard.io import AudioFile
        except ImportError:
            raise ImportError(
                "Pedalboard is not installed. Please install it with:\n"
                "pip install pedalboard"
            )
        
        # 오디오 파일 로드
        print(f"Loading audio from: {input_path}")
        with AudioFile(str(input_path)) as f:
            audio = f.read(f.frames)
            sample_rate = f.samplerate
        
        # 파이프라인 실행
        if save_separated_only:
            processed = self.process(audio, sample_rate, apply_effects=False)
        else:
            processed = self.process(audio, sample_rate, apply_effects=apply_effects)
        
        # 파일로 저장
        if output_path is not None:
            with AudioFile(
                str(output_path),
                'w',
                sample_rate,
                processed.shape[0]
            ) as f:
                f.write(processed)
            print(f"Processed audio saved to: {output_path}")
        
        return processed
    
    def batch_process(
        self,
        input_files: list,
        output_dir: Union[str, Path],
        apply_effects: bool = True,
        randomize_effects: bool = False
    ):
        """
        여러 파일 배치 처리
        
        Parameters:
            input_files (list): 입력 파일 경로 리스트
            output_dir (str | Path): 출력 디렉토리
            apply_effects (bool): 이펙트 적용 여부
            randomize_effects (bool): 각 파일마다 이펙트를 랜덤화할지 여부
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        if randomize_effects:
            randomizer = RandomizedSynthEffects()
        
        for i, input_file in enumerate(input_files):
            input_path = Path(input_file)
            output_path = output_dir / f"{input_path.stem}_synth_processed{input_path.suffix}"
            
            print(f"\n[{i+1}/{len(input_files)}] Processing: {input_path.name}")
            
            try:
                if randomize_effects and apply_effects:
                    # 랜덤 이펙트 사용
                    try:
                        from pedalboard.io import AudioFile
                    except ImportError:
                        raise ImportError("Pedalboard is not installed.")
                    
                    with AudioFile(str(input_path)) as f:
                        audio = f.read(f.frames)
                        sample_rate = f.samplerate
                    
                    # 분리
                    synth_audio = self.separator.separate(audio, sample_rate)
                    
                    # 랜덤 이펙트 적용
                    processed, params = randomizer.process(synth_audio, sample_rate)
                    print(f"  Applied randomized effects with params: {params}")
                    
                    # 저장
                    with AudioFile(str(output_path), 'w', sample_rate, processed.shape[0]) as f:
                        f.write(processed)
                else:
                    # 일반 처리
                    self.process_file(input_path, output_path, apply_effects=apply_effects)
                    
                print(f"  ✓ Saved to: {output_path}")
                
            except Exception as e:
                print(f"  ✗ Error processing {input_path.name}: {e}")


def process_synth_from_mix(
    audio: np.ndarray,
    sample_rate: int,
    apply_effects: bool = True,
    effect_preset: str = "default",
    separation_model: str = "htdemucs_6s",
    device: Optional[str] = None,
    **effect_params
) -> np.ndarray:
    """
    편의 함수: 믹스에서 신디사이저/피아노 분리 및 이펙트 적용
    
    Parameters:
        audio (np.ndarray): 입력 오디오 (전체 믹스)
        sample_rate (int): 샘플레이트
        apply_effects (bool): 이펙트 적용 여부
        effect_preset (str): 이펙트 프리셋
        separation_model (str): Demucs 모델 이름
        device (str): 'cuda', 'cpu' 또는 None
        **effect_params: 추가 이펙트 파라미터
        
    Returns:
        np.ndarray: 처리된 신디사이저/피아노 오디오
    """
    pipeline = SynthPipeline(
        separation_model=separation_model,
        device=device,
        effect_preset=effect_preset,
        **effect_params
    )
    
    return pipeline.process(audio, sample_rate, apply_effects=apply_effects)
