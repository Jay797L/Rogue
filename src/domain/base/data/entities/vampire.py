from domain.base.core.base_behavior import BaseBehavior

from . import _import as ci
from ._export import expose_entity


@ci.dataclass
class VampireCell(ci.Cell):
    """Клетка вампира."""

    content: str = "V"
    color: ci.COLORS = ci.COLORS.RED


@ci.dataclass(eq=False)
class Vampire(ci.Character):
    """Вампир."""

    name: str = "vampire"
    hp: int = 200
    max_hp: int = 200
    strength: int = 20
    dexterity: int = 40
    scope: int = 15
    point: ci.Point = ci.Point(0, 0)
    cell: ci.Cell = ci.field(default_factory=VampireCell)
    action: ci.Attack = ci.field(default_factory=ci.Attack)
    dop_action: ci.Heal = ci.field(default_factory=ci.Heal)
    art: tuple[str, ...] = (
        " .---.",
        "/ o o \\",
        "|  v  |",
        " \\_!_/",
        " /|\\",
        "/ \\",
    )


def vampire_ai(
    entity: Vampire, target: ci.Point, map_manager: ci.MapManager
) -> tuple[ci.MoveOrder | None, list[ci.Effect]]:

    effects, tried_to_attack = BaseBehavior.base_attack(entity, map_manager)
    if tried_to_attack:
        if effects:
            effects.append(
                entity.dop_action.from_caster(entity)
                .to_target(entity)
                .by_strength(entity.strength)
                .build()
            )
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
    preset_cls=Vampire,
    behavior_obj=vampire_ai,
    register_strategy=ci.CollectionOfBehaviors.register_strategy,
)
