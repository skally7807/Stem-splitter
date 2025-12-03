class EffectBlock:
    def __init__(self):
        self.device = None # 실제 pedalboard 객체가 담길 곳

    """
    from core.effect_block import EffectBlock
    from pedalboard import Pedalboard, Reverb

    # 1. 'EffectBlock'을 상속받아서 나만의 이펙터 클래스 정의
    class MyCustomReverb(EffectBlock):
        def __init__(self):
            super().__init__()
            # 껍데기(self) 안에 진짜 알맹이(pedalboard.Reverb)를 담아둠
            self.device = Reverb(room_size=0.8)

    # ---------------------------------------------------------

    my_reverb = MyCustomReverb()

    board = Pedalboard([
        my_reverb.get_device()  # <- 이렇게 사용가능
    ])
    """
    
    def get_device(self):
        return self.device
    
    
    # 이후 bypass 같은 기능 추가 가능
    # 전처리인데 왜 bypass? -> 확률적 활성화로 전처리 다양하게 가능