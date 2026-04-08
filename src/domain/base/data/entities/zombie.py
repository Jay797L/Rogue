from domain.base.core.base_behavior import BaseBehavior

from . import _import as ci
from ._export import expose_entity


@ci.dataclass
class ZombieCell(ci.Cell):
    """Клетка зомби."""

    content: str = "Z"
    color: ci.COLORS = ci.COLORS.GREEN


@ci.dataclass(eq=False)
class Zombie(ci.Character):
    """Зомби."""

    name: str = "zombie"
    hp: int = 100
    max_hp: int = 100
    strength: int = 20
    dexterity: int = 20
    scope: int = 10
    point: ci.Point = ci.Point(0, 0)
    cell: ci.Cell = ci.field(default_factory=ZombieCell)
    action: ci.Attack = ci.field(default_factory=ci.Attack)
    art: tuple[str, ...] = (
        " .---.",
        "/ x x \\",
        "|  -  |",
        " \\_!_/",
        " /   \\",
        "      ",
    )


def zombie_ai(
    entity: Zombie, target: ci.Point, map_manager: ci.MapManager
) -> tuple[ci.MoveOrder | None, list[ci.Effect]]:

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
    preset_cls=Zombie,
    behavior_obj=zombie_ai,
    register_strategy=ci.CollectionOfBehaviors.register_strategy,
)
