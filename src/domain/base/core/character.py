from dataclasses import dataclass, field

from domain.base.core.entity import Entity
from domain.base.utils.point import Point


@dataclass(eq=False, frozen=False)
class Character(Entity):
    hp: int = 1
    max_hp: int = 1
    dexterity: int = 1
    scope: int = 1
    status: list[str] = field(default_factory=list)
    art: tuple[str, ...] = ()
    target: Point | None = None


def check_status_in_character(character: Character, status: str) -> bool:
    if status in character.status:
        character.status.remove(status)
        return True
    return False
