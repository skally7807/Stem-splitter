"""
Synth/Piano/Keyboard Processing Pipeline
신디사이저, 피아노, 키보드 분리 및 이펙트 처리 통합 파이프라인

이 모듈은 전체 믹스 오디오에서 신디사이저(피아노, 키보드 포함) 성분을 분리하고,
설정된 이펙트 체인을 적용하여 최종 결과물을 생성하는 파이프라인을 제공합니다.
"""

import numpy as np
from typing import Optional, Union, Dict
from pathlib import Path

from .separator import SynthSeparator, separate_synth
from .effects import SynthEffectsChain, RandomizedSynthEffects, apply_synth_effects


class SynthPipeline:
    """
    완전한 신디사이저/피아노/키보드 처리 파이프라인 클래스임.
    
    음원 분리(Separation)부터 이펙트 적용(Effect Processing)까지의 전체 워크플로우를 관리함.
    단일 파일 처리, 메모리 상의 오디오 처리, 배치 처리를 모두 지원함.
    """
    
    def __init__(
        self,
        separation_model: str = "htdemucs_6s",
        device: Optional[str] = None,
        effect_preset: str = "default",
        **effect_params
    ):
        """
        SynthPipeline 인스턴스를 초기화함.

        :param separation_model: 사용할 Demucs 모델 이름 (기본값: "htdemucs_6s")
        :param device: 연산에 사용할 디바이스 ('cuda', 'cpu' 또는 None). None일 경우 자동 선택됨.
        :param effect_preset: 적용할 이펙트 프리셋 이름 ("default", "bright", "warm", "spacious", "tight" 등)
        :param effect_params: 이펙트 체인에 전달할 추가 파라미터들
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
        메모리 상의 오디오 데이터에 대해 파이프라인을 실행함.
        
        1. Demucs를 사용하여 믹스에서 신디사이저/피아노 트랙을 분리함.
        2. (옵션) 분리된 트랙에 이펙트 체인을 적용함.

        :param audio: 입력 오디오 데이터 (NumPy 배열, shape: [channels, samples] 또는 [samples])
        :param sample_rate: 오디오의 샘플 레이트 (Hz)
        :param apply_effects: 이펙트 체인을 적용할지 여부 (기본값: True)
        :param return_all_stems: True일 경우, 분리된 모든 스템(드럼, 베이스 등 포함)을 딕셔너리로 반환함.
        
        :return: 처리된 신디사이저 오디오 배열, 또는 모든 스템이 포함된 딕셔너리
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
        오디오 파일을 읽어서 파이프라인을 처리하고, 결과를 파일로 저장함.

        :param input_path: 입력 오디오 파일의 경로
        :param output_path: 처리된 오디오를 저장할 경로 (None일 경우 저장하지 않음)
        :param apply_effects: 이펙트 적용 여부 (기본값: True)
        :param save_separated_only: True일 경우 이펙트 없이 분리된 원본 스템만 저장함.
        
        :return: 처리된 오디오 데이터 (NumPy 배열)
        :raises ImportError: pedalboard가 설치되지 않은 경우 발생
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
        여러 오디오 파일을 일괄 처리(Batch Processing)함.

        :param input_files: 입력 파일 경로들의 리스트
        :param output_dir: 결과 파일을 저장할 디렉토리 경로
        :param apply_effects: 이펙트 적용 여부
        :param randomize_effects: True일 경우 각 파일마다 랜덤한 이펙트 파라미터를 적용함.
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
    [편의 함수] 믹스 오디오에서 신디사이저/피아노를 분리하고 이펙트를 적용함.
    
    SynthPipeline 클래스를 인스턴스화하지 않고 빠르게 처리하고 싶을 때 사용하셈.

    :param audio: 입력 믹스 오디오 데이터
    :param sample_rate: 샘플 레이트
    :param apply_effects: 이펙트 적용 여부
    :param effect_preset: 이펙트 프리셋 이름
    :param separation_model: Demucs 모델 이름
    :param device: 실행 디바이스
    :param effect_params: 추가 이펙트 파라미터
    
    :return: 처리된 오디오 데이터
    """
    pipeline = SynthPipeline(
        separation_model=separation_model,
        device=device,
        effect_preset=effect_preset,
        **effect_params
    )
    
    return pipeline.process(audio, sample_rate, apply_effects=apply_effects)
