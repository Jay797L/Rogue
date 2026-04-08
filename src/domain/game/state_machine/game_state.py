from enum import Enum


class GameState(Enum):
    """Represents the possible states of the game."""

    MENU = 0
    EXPLORING = 1
    INVENTORY = 2
    VICTORY = 3
    GAME_OVER = 4
    EXPLORING_3D = 5
    LOAD_GAME = 6
    SETTINGS = 8
    ABOUT = 7
