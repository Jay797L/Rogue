from domain.base.core.base_behavior import BaseBehavior

from . import _import as ci
from ._export import expose_entity


@ci.dataclass
class SnakeMageCell(ci.Cell):
    """Клетка змеиного мага."""

    content: str = "S"


@ci.dataclass(eq=False)
class SnakeMage(ci.Character):
    """Змеиный маг."""

    name: str = "snake_mage"
    hp: int = 100
    max_hp: int = 100
    strength: int = 20
    dexterity: int = 80
    scope: int = 15
    point: ci.Point = ci.Point(0, 0)
    cell: ci.Cell = ci.field(default_factory=SnakeMageCell)
    action: ci.Attack = ci.field(default_factory=ci.Attack)
    dop_action: ci.StunEffect = ci.field(default_factory=ci.StunEffect)
    art: tuple[str, ...] = (
        " ~^^~ ",
        "( o_o )",
        "/|  |\\",
        " vv vv",
        "      ",
        "      ",
    )


def snakemage_ai(
    entity: SnakeMage, target: ci.Point, map_manager: ci.MapManager
) -> tuple[ci.MoveOrder | None, list[ci.Effect]]:
    dop_directions = [
        a + b
        for a, b in zip(
            ci.ALL_DIRECTIONS, ci.islice(ci.cycle(ci.ALL_DIRECTIONS), 1, None)
        )
    ]
    effects, tried_to_attack = BaseBehavior.base_attack(
        entity, map_manager, ci.ALL_DIRECTIONS.extend(dop_directions)
    )
    if tried_to_attack:
        if effects:
            effects.append(
                entity.dop_action.from_caster(entity)
                .to_target(effects[0].target)
                .build()
            )
        return None, effects

    move_order = BaseBehavior.persecution(entity, target, map_manager)

    if move_order is not None:
        return move_order, []

    options = []
    diagonal_pairs = zip(
        ci.ALL_DIRECTIONS, ci.islice(ci.cycle(ci.ALL_DIRECTIONS), 1, None), strict=False
    )

    for diag1, diag2 in diagonal_pairs:
        intermediate1 = entity.point + diag1
        intermediate2 = entity.point + diag2
        target_point = entity.point + diag1 + diag2

        if map_manager.is_empty(target_point) and (
            map_manager.is_empty(intermediate1) or map_manager.is_empty(intermediate2)
        ):
            options.append(target_point)

    if options:
        move_order = (
            ci.MoveOrder(entity, ci.random.choice(options)) if options else None
        )
    return move_order, []


expose_entity(
    module_globals=globals(),
    preset_cls=SnakeMage,
    behavior_obj=snakemage_ai,
    register_strategy=ci.CollectionOfBehaviors.register_strategy,
)
