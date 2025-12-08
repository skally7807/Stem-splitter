.. hystemfx documentation master file, created by
   sphinx-quickstart on Mon Dec  1 23:55:23 2025.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

hystemfx documentation
======================

**HystemFX** 는 딥러닝 기반의 음원 분리(Stem Separation)와 오디오 이펙트 처리를 위한 파이썬 라이브러리입니다.
복잡한 오디오 전처리 과정을 파이프라인 하나로 손쉽게 해결할 수 있도록 설계되었습니다.

.. note::
   이 프로젝트는 현재 개발 중인 버전(Alpha 0.1)입니다.

주요 기능 (Features)
--------------------

* **Stem Separation**: Demucs 모델을 활용하여 신디사이저(또는 피아노), 베이스, 기타, 보컬을 분리합니다.
* **Smart Effects Chain**: 각 악기(Stem)에 최적화된 이펙트 체인을 자동으로 적용합니다.
    * **Guitar**: Overdrive, Distortion, Chorus 등
    * **Bass**: Compressor, EQ 등
    * **Vocal**: Reverb, Delay 등
    * **Customizable**: `pedalboard` 객체를 직접 전달하여 사용자 정의 이펙트 체인 적용 가능
* **Easy Pipeline**: 단 몇 줄의 코드로 분리부터 마스터링까지 한 번에 처리합니다.

API 문서 (Modules)
------------------

라이브러리의 상세한 모듈 설명은 아래 링크를 참고하세요.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   quickstart
   modules
