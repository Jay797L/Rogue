from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from domain.base.core.effect import Effect

if TYPE_CHECKING:
    from domain.base.core.character import Character
    from domain.base.core.effect_frame import EffectFrame
    from domain.base.core.entity import Entity


class IEffectGenerator(ABC):
    def __init__(self):
        self.attribut: str | None = None
        self.caster: Entity | None = None
        self.target: Character | None = None
        self.strength: int | None = None

    def from_caster(self, caster: Character):
        self.caster = caster
        return self

    def to_target(self, target: Character):
        self.target = target
        return self

    def by_attribut(self, attribut: str):
        self.attribut = attribut
        return self

    def by_strength(self, strength: int):
        self.strength = strength
        return self

    def build(self) -> Effect:
        frames = self.internal_calculations()
        return Effect(self.target, self.caster, self.attribut, frames)

    @staticmethod
    @abstractmethod
    def internal_calculations() -> list[EffectFrame]:
        pass
