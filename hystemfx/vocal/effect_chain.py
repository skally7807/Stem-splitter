"""
vocal.effect_chain

- 보컬 트랙에 적용할 이펙트(컴프레서, EQ, 리버브 등) 체인을 정의하는 모듈
- 외부에서 사용할 핵심 함수는 `build_vocal_chain(...)` 예정
- Spotify pedalboard 같은 이펙트 라이브러리를 조합해서 
  "보컬용 프리셋 체인"을 만들어 주는 역할만 담당한다.
"""

from typing import Any, Dict, Optional

def build_vocal_chain(config: Optional[Dict[str, Any]] = None):
    """
    보컬 전용 이펙트 체인을 생성하여 반환한다.

    Args:
        config: 
            - 컴프 세기, EQ 대역, 리버브 양 등
            - 나중에 YAML/JSON에서 읽어 온 설정을 그대로 넣을 수 있게 확장성을 둔다.

    Returns:
        chain:
            - pedalboard.Board 인스턴스
            - 또는 내부적으로 정의한 "이펙트 리스트" 객체
            - 중요한 건, effect_processor에서 그대로 받아서 apply할 수 있는 형태일 것.
    """
    # TODO: 실제 이펙트 체인 구성
    pass
