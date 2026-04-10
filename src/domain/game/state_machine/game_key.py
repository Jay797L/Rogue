from enum import Enum


class GameKey(Enum):
    """Enum representing keyboard controls for the game."""

    KEY_F = ("f", "а")

    KEY_W = ("w", "ц")
    KEY_S = ("s", "ы")
    KEY_A = ("a", "ф")
    KEY_D = ("d", "в")
    KEY_V = ("v", "м")

    KEY_H = ("h", "р")
    KEY_J = ("j", "о")
    KEY_K = ("k", "л")
    KEY_L = ("l", "д")
    KEY_E = ("e", "у")
    KEY_M = ("m", "ь")

    KEY_Q = ("q", "й", ":")
    SAVE_GAME = ("S", "Ы")
    INVENTORY = ("i", "ш")
    HELP = ("?", "/")
    REST = ("r", "к")

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
