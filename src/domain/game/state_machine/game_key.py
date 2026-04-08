from enum import Enum


class GameKey(Enum):
    """Enum representing keyboard controls for the game."""

    KEY_F = "f"

    KEY_W = "w"
    KEY_S = "s"
    KEY_A = "a"
    KEY_D = "d"
    KEY_V = "v"

    KEY_H = "h"
    KEY_J = "j"
    KEY_K = "k"
    KEY_L = "l"
    KEY_E = "e"
    KEY_M = "m"

    KEY_Q = ("q", ":")
    SAVE_GAME = ("S",)
    INVENTORY = "i"
    HELP = ("?", "/")
    REST = "r"

    NUM_1 = ("1",)
    NUM_2 = ("2",)
    NUM_3 = ("3",)
    NUM_4 = ("4",)
    NUM_5 = ("5",)
    NUM_6 = ("6",)
    NUM_7 = ("7",)
    NUM_8 = ("8",)
    NUM_9 = ("9",)
    NUM_0 = ("0",)
    NOPE = str(-1)
    SELECT = ("\n", "\r")
    BACKSPACE = ("\b", r"\x7f")

    def matches(self, key: str) -> bool:
        """Check if the given key matches this action."""
        return key in self.value
