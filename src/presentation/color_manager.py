from __future__ import annotations

import curses
from enum import Enum


class ColorPreset(Enum):
    """Предопределенные цвета для использования в приложении."""

    WHITE = "#ffffff"
    BLACK = "#000000"
    RED = "#ff0000"
    GREEN = "#00ff00"
    YELLOW = "#ffff00"
    BLUE = "#0000ff"
    MAGENTA = "#ff00ff"
    PERVANCHE = "#ccccff"

    GRAY = "#B3B3B3"
    DARK_GRAY = "#444444"
    LIGHT_GRAY = "#cccccc"
    ORANGE = "#ff8800"
    PURPLE = "#aa00ff"

    BORDER = "#88aaff"
    BORDER_DARK = "#4466aa"

    HP_GOOD = "#00ff00"
    HP_WARNING = "#ffff00"
    HP_CRITICAL = "#ff0000"

    LOGO_GREEN = "#37ff00"
    SELECTION = "#ffff00"
    DIM_TEXT = "#FFFFFF"
    BRIGHT_TEXT = "#ffffff"


class ColorManager:
    """Централизованное управление цветами."""

    _instance = None

    def __new__(cls: type[ColorManager]) -> "ColorManager":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.color_pairs = {}
        self.hex_to_index_cache = {}
        self.next_pair = 20
        self.basic_pairs = {}

        self.preset_cache = {}

    def init_basic_colors(self):
        """Инициализация базовых цветов (вызывается после curses.start_color())."""
        if not curses.has_colors():
            return

        basic_colors = {
            1: (curses.COLOR_WHITE, -1),
            2: (curses.COLOR_RED, -1),
            3: (curses.COLOR_GREEN, -1),
            4: (curses.COLOR_YELLOW, -1),
            5: (curses.COLOR_BLUE, -1),
            6: (curses.COLOR_CYAN, -1),
            7: (curses.COLOR_MAGENTA, -1),
        }
        for idx, (fg, bg) in basic_colors.items():
            curses.init_pair(idx, fg, bg)
            self.basic_pairs[idx] = (fg, bg)
        self.next_pair = 20

    @staticmethod
    def get_color(preset: ColorPreset) -> str:
        """Получить hex-код предопределенного цвета."""
        return preset.value

    def get_color_pair_from_preset(
        self, fg_preset: ColorPreset, bg_preset: ColorPreset | None = None
    ) -> int:
        """Получить цветовую пару из предопределенных цветов."""
        bg_hex = "transparent" if bg_preset is None else bg_preset.value
        return self.get_color_pair(fg_preset.value, bg_hex)

    @staticmethod
    def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
        hex_color = hex_color.lstrip("#")
        return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))

    @staticmethod
    def rgb_to_xterm256(r: int, g: int, b: int) -> int:
        if not r == g == b:
            r_idx = int(r / 51)
            g_idx = int(g / 51)
            b_idx = int(b / 51)
            return 16 + 36 * r_idx + 6 * g_idx + b_idx
        if r < 8:
            return 16
        if r > 248:
            return 231
        return 232 + int((r - 8) / 10)

    def get_color_index(self, hex_color: str) -> int:
        if hex_color in self.hex_to_index_cache:
            return self.hex_to_index_cache[hex_color]
        r, g, b = self.hex_to_rgb(hex_color)
        color_index = self.rgb_to_xterm256(r, g, b)
        self.hex_to_index_cache[hex_color] = color_index
        return color_index

    def get_color_pair(
        self, fg_hex: str = "#ffffff", bg_hex: str = "transparent"
    ) -> int:
        """Получить номер цветовой пары для указанных hex-цветов."""
        if bg_hex == "transparent":
            bg_hex = "-1"

        key = (fg_hex, bg_hex)
        if key not in self.color_pairs:
            fg_index = self.get_color_index(fg_hex)
            bg_index = -1 if bg_hex == "-1" else self.get_color_index(bg_hex)

            pair_num = self.next_pair
            while pair_num < curses.COLOR_PAIRS:
                if (
                    pair_num not in self.basic_pairs
                    and pair_num not in self.color_pairs.values()
                ):
                    break
                pair_num += 1
                if pair_num >= curses.COLOR_PAIRS:
                    pair_num = 20

            curses.init_pair(pair_num, fg_index, bg_index)
            self.color_pairs[key] = pair_num
            self.next_pair = pair_num + 1
            if self.next_pair >= curses.COLOR_PAIRS:
                self.next_pair = 20

        return self.color_pairs[key]

    def get_basic_pair(self, color_num: int) -> int:
        """Получить базовый цветовой номер (1-7). DEPRECATED."""
        if color_num in self.basic_pairs:
            return color_num
        return 1


color_manager = ColorManager()
