"""
Guitar Processing Pipeline
기타 분리 및 이펙트 처리 통합 파이프라인

이 모듈은 전체 믹스 오디오에서 기타 성분을 분리하고,
설정된 이펙트 체인을 적용하여 최종 결과물을 생성하는 파이프라인을 제공합니다.
"""

import numpy as np
from typing import Optional, Union, Dict
from pathlib import Path

from .separator import GuitarSeparator, separate_guitar
from .effects import GuitarEffectsChain

class GuitarPipeline:
    """
    기타 처리를 위한 통합 파이프라인 클래스임.
    
    이 클래스는 Demucs를 사용한 기타 분리(Separation)와 Pedalboard를 사용한 이펙트 처리(Effect Processing)를
    하나의 워크플로우로 통합하여 관리함.
    
    주요 기능:
    - 단일 파일 처리 (`process_file`)
    - 메모리 상의 오디오 데이터 처리 (`process`)
    - 다중 파일 배치 처리 (`batch_process`)
    """
    
    def __init__(
        self,
        separation_model: str = "htdemucs_6s",
        device: Optional[str] = None,
        effect_preset: str = "clean",
        **effect_params
    ):
        """
        GuitarPipeline 인스턴스를 초기화함.

        :param separation_model: 사용할 Demucs 모델 이름 (기본값: "htdemucs_6s")
        :param device: 연산에 사용할 디바이스 ('cuda', 'cpu' 또는 None). None일 경우 자동 선택됨.
        :param effect_preset: 적용할 이펙트 프리셋 이름 (예: "clean", "distortion", "crunch")
        :param effect_params: 이펙트 체인에 전달할 추가 파라미터들
        """
        self.separator = GuitarSeparator(model_name=separation_model, device=device)
        self.effect_preset = effect_preset
        self.effect_params = effect_params
        # GuitarEffectsChain takes preset in init
        self.effects_chain = GuitarEffectsChain(preset=effect_preset, **effect_params)
        
    def process(
        self,
        audio: np.ndarray,
        sample_rate: int,
        apply_effects: bool = True,
        return_all_stems: bool = False
    ) -> Union[np.ndarray, Dict[str, np.ndarray]]:
        """
        메모리 상의 오디오 데이터(NumPy 배열)를 처리함.
        
        1. 입력된 믹스 오디오에서 기타 트랙을 분리함.
        2. (옵션) 분리된 기타 트랙에 설정된 이펙트 프리셋을 적용함.

        :param audio: 입력 오디오 데이터 (NumPy 배열, shape: [channels, samples] 또는 [samples])
        :param sample_rate: 오디오의 샘플 레이트 (Hz)
        :param apply_effects: 이펙트 체인을 적용할지 여부 (기본값: True)
        :param return_all_stems: True일 경우, 분리된 모든 스템(기타 외)을 포함한 딕셔너리를 반환함.
        
        :return: 
            - 기본적으로 처리된 기타 오디오 배열(np.ndarray)을 반환함.
            - `return_all_stems=True`인 경우, `{'guitar': ..., 'guitar_processed': ..., ...}` 형태의 딕셔너리를 반환함.
        """
        print("Step 1/2: Separating guitar from mix...")
        
        # 음원 분리
        if return_all_stems:
            stems = self.separator.separate(audio, sample_rate, return_all_stems=True)
            guitar_audio = stems["guitar"]
        else:
            guitar_audio = self.separator.separate(audio, sample_rate, return_all_stems=False)
        
        # 이펙트 적용
        if apply_effects:
            print("Step 2/2: Applying effects chain...")
            # GuitarEffectsChain.process takes (audio, sample_rate)
            processed = self.effects_chain.process(guitar_audio, sample_rate)
            
            if return_all_stems:
                stems["guitar_processed"] = processed
                return stems
            else:
                return processed
        else:
            if return_all_stems:
                return stems
            else:
                return guitar_audio
    
    def process_file(
        self,
        input_path: Union[str, Path],
        output_path: Optional[Union[str, Path]] = None,
        apply_effects: bool = True,
        save_separated_only: bool = False
    ) -> Optional[np.ndarray]:
        """
        오디오 파일을 읽어서 분리 및 이펙트 처리를 수행하고, 결과를 파일로 저장함.

        :param input_path: 입력 오디오 파일의 경로 (wav, mp3 등 지원)
        :param output_path: 처리된 오디오를 저장할 경로 (None일 경우 저장하지 않음)
        :param apply_effects: 이펙트 적용 여부 (기본값: True)
        :param save_separated_only: True일 경우 이펙트 처리 없이 분리된 원본(Clean) 스템만 저장함.
        
        :return: 처리된 오디오 데이터 (NumPy 배열)
        :raises ImportError: pedalboard 라이브러리가 설치되지 않은 경우 발생
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
        apply_effects: bool = True
    ):
        """
        여러 오디오 파일을 일괄 처리(Batch Processing)함.

        :param input_files: 입력 파일 경로들의 리스트
        :param output_dir: 결과 파일을 저장할 디렉토리 경로
        :param apply_effects: 이펙트 적용 여부
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        for i, input_file in enumerate(input_files):
            input_path = Path(input_file)
            output_path = output_dir / f"{input_path.stem}_guitar_processed{input_path.suffix}"
            
            print(f"\n[{i+1}/{len(input_files)}] Processing: {input_path.name}")
            
            try:
                self.process_file(input_path, output_path, apply_effects=apply_effects)
                print(f"  ✓ Saved to: {output_path}")
                
            except Exception as e:
                print(f"  ✗ Error processing {input_path.name}: {e}")


def process_guitar_from_mix(
    audio: np.ndarray,
    sample_rate: int,
    apply_effects: bool = True,
    effect_preset: str = "clean",
    separation_model: str = "htdemucs_6s",
    device: Optional[str] = None,
    **effect_params
) -> np.ndarray:
    """
    [편의 함수] 믹스 오디오에서 기타를 분리하고 이펙트를 적용함.
    
    GuitarPipeline 클래스를 직접 인스턴스화하지 않고, 함수 호출 한 번으로 처리를 수행하고 싶을 때 유용함.

    :param audio: 입력 믹스 오디오 데이터 (NumPy 배열)
    :param sample_rate: 샘플 레이트 (Hz)
    :param apply_effects: 이펙트 적용 여부 (기본값: True)
    :param effect_preset: 적용할 이펙트 프리셋 이름
    :param separation_model: 사용할 Demucs 모델 이름
    :param device: 연산 장치 ('cuda' 또는 'cpu')
    :param effect_params: 추가 이펙트 파라미터
    
    :return: 처리된 기타 오디오 데이터 (NumPy 배열)
    """
    pipeline = GuitarPipeline(
        separation_model=separation_model,
        device=device,
        effect_preset=effect_preset,
        **effect_params
    )
    
    return pipeline.process(audio, sample_rate, apply_effects=apply_effects)
