from domain.base.core.base_behavior import BaseBehavior

from . import _import as ci
from ._export import expose_entity


@ci.dataclass
class GhostCell(ci.Cell):
    """Клетка призрака."""

    content: str = "G"


@ci.dataclass(eq=False)
class Ghost(ci.Character):
    """Призрак."""

    name: str = "ghost"
    hp: int = 50
    max_hp: int = 50
    strength: int = 5
    dexterity: int = 30
    scope: int = 5
    point: ci.Point = ci.Point(0, 0)
    cell: ci.Cell = ci.field(default_factory=GhostCell)
    action: ci.Attack = ci.field(default_factory=ci.Attack)
    art: tuple[str, ...] = (
        " .--. ",
        "/    \\",
        "| () |",
        " \\__/ ",
        "  ~~  ",
        "      ",
    )


def ghost_ai(
    entity: Ghost, target: ci.Point, map_manager: ci.MapManager
) -> tuple[ci.MoveOrder | None, list[ci.Effect]]:
    effects, tried_to_attack = BaseBehavior.base_attack(entity, map_manager)
    if tried_to_attack:
        return None, effects

    move_order = BaseBehavior.persecution(entity, target, map_manager)
    if move_order is not None:
        return move_order, []
    options = []
    max_distance = 5

    for first_direction in ci.ALL_DIRECTIONS[:4]:
        current_point = entity.point
        first_move = first_direction + current_point

        if not map_manager.is_empty(first_move):
            continue

        current_point = first_move

        remaining_steps = ci.random.randint(0, max_distance - 1)
        for _ in range(remaining_steps):
            direction_index = ci.random.randint(0, len(ci.ALL_DIRECTIONS) - 1)
            direction = ci.ALL_DIRECTIONS[direction_index]
            next_point = direction + current_point

            if not map_manager.is_empty(next_point):
                break
            current_point = next_point

        if current_point not in options:
            options.append(current_point)

    if options:
        move_order = (
            ci.MoveOrder(entity, ci.random.choice(options)) if options else None
        )
    return move_order, []


expose_entity(
    module_globals=globals(),
    preset_cls=Ghost,
    behavior_obj=ghost_ai,
    register_strategy=ci.CollectionOfBehaviors.register_strategy,
)
