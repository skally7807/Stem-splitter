"""
vocal.effect_chain

- 보컬 트랙에 적용할 이펙트(컴프레서, EQ, 리버브 등) 체인을 정의하는 모듈
- 외부에서 사용할 핵심 함수는 `build_vocal_chain(...)` 예정
- Spotify pedalboard 같은 이펙트 라이브러리를 조합해서 
  "보컬용 프리셋 체인"을 만들어 주는 역할만 담당한다.
"""