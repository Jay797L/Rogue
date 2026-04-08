from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from domain.base.core.effect_frame import EffectFrame

if TYPE_CHECKING:
    from domain.base.core.character import Character

logger = logging.getLogger(__name__)


class Effect:
    def __init__(
        self,
        target: Character | None,
        caster: Character | None,
        attribut: str,
        frames: list[EffectFrame],
    ):
        self.target = target
        self.caster = caster
        self.attribut = attribut
        self.frames = frames
        self._current_frame_index = 0
        self._remaining_delay = 0

    def apply(self) -> None:

        if self._current_frame_index >= len(self.frames):
            return

        if self._remaining_delay > 0:
            self._remaining_delay -= 1
            return

        frame = self.frames[self._current_frame_index]
        if frame.delay > 0:
            self._remaining_delay = frame.delay - 1
            return

        if not hasattr(self.target, self.attribut):
            logger.warning(
                "Cannot apply effect: {} has no attribute '{}'. Skipping effect {}",
                self.target,
                self.attribut,
                self,
            )
            self._current_frame_index += 1
            return

        current_value = getattr(self.target, self.attribut)
        setattr(self.target, self.attribut, current_value + frame.delta)
        logger.debug(
            "Applied {} to {}.{} -> {}",
            frame.delta,
            self.target,
            self.attribut,
            getattr(self.target, self.attribut),
        )

        self._current_frame_index += 1

    @property
    def its_time_to_die(self) -> bool:
        return self._current_frame_index >= len(self.frames)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(target={self.target}, "
            f"caster={self.caster}, attribut={self.attribut}, "
            f"frame={self._current_frame_index}/{len(self.frames)}, "
            f"delay_left={self._remaining_delay})"
        )
