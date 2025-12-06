Quickstart
==========

HystemFX를 빠르게 시작하기 위한 가이드입니다. 

라이브러리 설치가 완료되었다면, 아래 예제를 통해 전체 파이프라인(Full Pipeline) 또는 개별 Stem 처리(Single Stem Processing)를 수행할 수 있습니다.

Full Pipeline 예제
------------------

오디오 파일 하나를 입력받아 **Stem 분리**부터 **각 세션별 이펙트 적용**까지 한 번에 수행하는 예제입니다.

.. code-block:: python

    from hystemfx.pipeline import run_pipeline
    from pedalboard import Pedalboard, Distortion, Reverb
    import os

    # 1. 입력 파일 준비 (예시)
    input_file = "mixed.wav"
    if not os.path.exists(input_file):
        print(f"Error: '{input_file}' not found.")
    
    # 2. 커스텀 이펙트 체인 정의 (선택 사항)
    # Pedalboard 객체를 직접 생성하여 특정 세션의 프리셋으로 전달할 수 있습니다.
    custom_guitar = Pedalboard([
        Distortion(drive_db=15.0),
        Reverb(room_size=0.5)
    ])

    # 3. 파이프라인 실행
    # input_path: 입력 오디오 파일
    # output_dir: 결과물이 저장될 디렉토리
    results = run_pipeline(
        input_path=input_file,
        output_dir="demo_output/full",
        vocal_preset="bright",
        synth_preset="warm",
        guitar_preset=custom_guitar,  # 커스텀 체인 적용
        bass_preset="vintage"
        # device="cuda"  # GPU 사용 시 설정 (기본값: 자동 감지)
    )

    print("Generated Files:", results)

Single Stem Processing 예제
---------------------------

이미 분리되어 있는 특정 Stem 파일에 이펙트만 적용하고 싶을 때 사용하는 방법입니다.

.. code-block:: python

    from hystemfx.pipeline import process_stem

    # process_stem 함수를 사용하여 단일 세션 처리
    process_stem(
        input_path="vocals_raw.wav",
        output_path="vocals_processed.wav",
        session_type="vocals",  # 'vocals', 'guitar', 'bass', 'synth' 중 선택
        preset="radio",         # 각 세션별로 제공되는 프리셋 이름 사용
        sr=44100
    )

    print("Processing Complete.")
