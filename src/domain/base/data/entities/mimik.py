import random

from domain.base.core.base_behavior import BaseBehavior

from . import _import as ci
from ._export import expose_entity

ITEM_SYMBOLS = ["!", "?", "&", "$", "+", "^", "%"]


@ci.dataclass
class MimikCell(ci.Cell):
    """Клетка мимика – изначально выглядит как случайный предмет."""

    content: str = ci.field(default_factory=lambda: random.choice(ITEM_SYMBOLS))
    color: ci.COLORS = ci.COLORS.WHITE
    blocking_vision: bool = False


@ci.dataclass(eq=False)
class Mimik(ci.Character):
    """Мимик – имитирует предмет, пока не обнаружен."""

    name: str = "mimik"
    hp: int = 200
    max_hp: int = 200
    strength: int = 5
    dexterity: int = 30
    scope: int = 5
    point: ci.Point = ci.Point(0, 0)
    cell: ci.Cell = ci.field(default_factory=MimikCell)
    action: ci.Attack = ci.field(default_factory=ci.Attack)
    status: list[str] = ci.field(default_factory=lambda: ["hide"])
    art: tuple[str, ...] = (
        "+----+",
        "| oo |",
        "| <> |",
        "+----+",
        "  \\/  ",
        "      ",
    )

    def reveal(self):
        """Раскрывает мимика: меняет внешний вид и убирает статус скрытия."""
        if "hide" in self.status:
            self.status.remove("hide")
            self.cell.content = "m"
            self.cell.color = ci.COLORS.WHITE


def mimik_ai(
    entity: Mimik, target: ci.Point, map_manager: ci.MapManager
) -> tuple[ci.MoveOrder | None, list[ci.Effect]]:
    """
    AI for Mimik enemy.
    - When hidden ('hide' status): does nothing, just mimics an item
    - When revealed (after being hit): can attack, chase player, and move
    """

    if "hide" in entity.status:
        return None, []

    effects, tried_to_attack = BaseBehavior.base_attack(entity, map_manager)
    if tried_to_attack:
        return None, effects

    move_order = BaseBehavior.persecution(entity, target, map_manager)
    if move_order is not None:
        return move_order, []

    options = BaseBehavior.ebluet(entity, map_manager)
    if options:
        move_order = ci.MoveOrder(entity, ci.random.choice(options))

    return move_order, []


expose_entity(
    module_globals=globals(),
    preset_cls=Mimik,
    behavior_obj=mimik_ai,
    register_strategy=ci.CollectionOfBehaviors.register_strategy,
)
