import logging
import random

from domain.base.core.base_effect import IEffectGenerator
from domain.base.core.character import Character
from domain.base.core.effect_frame import EffectFrame

logger = logging.getLogger(__name__)


def set_random_stats_to_character(target: Character):
    target.hp = random.randint(1, target.hp * 3)
    target.max_hp = random.randint(10, target.max_hp * 3)
    target.dexterity = random.randint(1, target.dexterity * 3)
    target.strength = random.randint(1, target.strength * 3)
    target.scope = random.randint(3, target.scope * 3)


class Attack(IEffectGenerator):
    def __init__(self, game: None = None, **kwargs):
        super().__init__(**kwargs)
        self.attribut = "hp"
        self.game = game

    def internal_calculations(self) -> list[EffectFrame]:
        if self.target is None or self.caster is None:
            raise ValueError("Caster and target must be set")
        if self.strength is None:
            self.strength = self.caster.strength

        # Запись статистики (остаётся)
        if self.game:
            if self.caster.name == "player":
                self.game.statistics.record_hit_dealt(self.strength)
            else:
                self.game.statistics.record_hit_taken(self.strength)

        return [EffectFrame(delay=0, delta=-self.strength)]


class Heal(IEffectGenerator):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.attribut = "hp"

    def internal_calculations(self) -> list[EffectFrame]:
        if self.target is None:
            raise ValueError("Target not set. Call to_target() first.")
        if self.attribut is None:
            raise ValueError("Attribut not set. Cal by_attribut() first.")

        return [EffectFrame(delay=0, delta=self.strength)]


class TMTRAINER(IEffectGenerator):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def internal_calculations(self) -> list[EffectFrame]:
        set_random_stats_to_character(self.target)
        return [
            EffectFrame(
                delay=random.randint(0, self.strength),
                delta=random.randint(0, self.strength),
            )
        ]


class InstatnceEffect(IEffectGenerator):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def internal_calculations(self) -> list[EffectFrame]:
        if self.target is None:
            raise ValueError("Target not set. Call to_target() first.")
        if self.attribut is None:
            raise ValueError("Attribut not set. Cal by_attribut() first.")

        return [EffectFrame(delay=0, delta=-self.strength)]


class TemporaryEffect(IEffectGenerator):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def internal_calculations(self) -> list[EffectFrame]:
        if self.target is None:
            raise ValueError("Target not set. Call to_target() first.")
        if self.attribut is None:
            raise ValueError("Attribut not set. Cal by_attribut() first.")

        return [
            EffectFrame(delay=0, delta=self.strength),
            EffectFrame(delay=20, delta=-self.strength),
        ]


class GradualEffect(IEffectGenerator):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def internal_calculations(self) -> list[EffectFrame]:
        if self.target is None:
            raise ValueError("Target not set. Call to_target() first.")
        if self.attribut is None:
            raise ValueError("Attribut not set. Cal by_attribut() first.")

        return [EffectFrame(delay=i, delta=self.strength) for i in range(20)]


class StunEffect(IEffectGenerator):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.attribut = "hp"
        self.strength = 0

    def internal_calculations(self) -> list[EffectFrame]:
        self.target.status.append("stun")
        return [EffectFrame(delay=0, delta=0)]
