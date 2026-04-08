from domain.base.utils.directions import DOWN, LEFT, RIGHT, UP
from domain.base.utils.point import Point
from domain.game.state_machine.game_key import GameKey


def get_direction_from_key(key: GameKey) -> Point | None:
    """Convert GameKey to direction Point."""
    direction_map = {
        GameKey.KEY_W: UP,
        GameKey.KEY_S: DOWN,
        GameKey.KEY_A: LEFT,
        GameKey.KEY_D: RIGHT,
        GameKey.KEY_K: UP,
        GameKey.KEY_J: DOWN,
        GameKey.KEY_H: LEFT,
        GameKey.KEY_L: RIGHT,
    }

    return direction_map.get(key)
