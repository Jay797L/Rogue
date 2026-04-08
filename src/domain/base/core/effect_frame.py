from dataclasses import dataclass


@dataclass(frozen=True)
class EffectFrame:
    delay: int = 0
    delta: int = 0
