from domain.base.core.base_behavior import BaseBehavior

from . import _import as ci
from ._export import expose_entity


@ci.dataclass
class OgrCell(ci.Cell):
    """Клетка огра."""

    content: str = "O"


@ci.dataclass(eq=False)
class Ogr(ci.Character):
    """Огр."""

    name: str = "ogr"
    hp: int = 300
    max_hp: int = 300
    strength: int = 50
    dexterity: int = 5
    scope: int = 10
    point: ci.Point = ci.Point(0, 0)
    cell: ci.Cell = ci.field(default_factory=OgrCell)
    action: ci.Attack = ci.field(default_factory=ci.Attack)
    art: tuple[str, ...] = (
        " .---.",
        "/ o o \\",
        "|  ^  |",
        "\\ \\_/ /",
        " '---' ",
        "      ",
    )


def ogr_ai(
    entity: Ogr, target: ci.Point, map_manager: ci.MapManager
) -> tuple[ci.MoveOrder | None, list[ci.Effect]]:
    """
    AI for Ogr enemy.
    High strength, low dexterity - prefers direct confrontation.
    """

    effects, tried_to_attack = BaseBehavior.base_attack(entity, map_manager)
    if tried_to_attack:
        return None, effects

    move_order = BaseBehavior.persecution(entity, target, map_manager)
    if move_order is not None:
        return move_order, []

    options = BaseBehavior.ebluet(entity, map_manager)
    if options:
        return ci.MoveOrder(entity, ci.random.choice(options)), []

    return None, []


expose_entity(
    module_globals=globals(),
    preset_cls=Ogr,
    behavior_obj=ogr_ai,
    register_strategy=ci.CollectionOfBehaviors.register_strategy,
)
