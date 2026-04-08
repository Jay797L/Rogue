"""Рендерер карточки статистики игрока с ASCII-артом."""

import curses

from domain.base.core.base_game import BaseGame
from presentation.color_manager import ColorPreset, color_manager


class PlayerStatsRenderer:
    """Рендерер карточки статистики игрока."""

    PLAYER_ART = [
        "   @   ",
        "  /|\\  ",
        "  / \\  ",
        "       ",
    ]

    def __init__(self, stdscr: curses.window):
        self.stdscr = stdscr
        self.card_width = 25
        self.card_height = 12

    def render(self, game: BaseGame, start_x: int, start_y: int) -> None:
        """Отрисовывает карточку статистики игрока."""
        height, width = self.stdscr.getmaxyx()

        if start_x + self.card_width > width or start_y + self.card_height > height:
            return

        color_manager.get_color_pair_from_preset(ColorPreset.BORDER)

        try:
            self.stdscr.addstr(
                start_y, start_x, "+" + "-" * (self.card_width - 2) + "+"
            )

            for i in range(1, self.card_height - 1):
                self.stdscr.addstr(start_y + i, start_x, "|")
                self.stdscr.addstr(start_y + i, start_x + self.card_width - 1, "|")

            self.stdscr.addstr(
                start_y + self.card_height - 1,
                start_x,
                "+" + "-" * (self.card_width - 2) + "+",
            )
        except curses.error:
            return

        title = "PLAYER STATS"
        title_x = start_x + (self.card_width - len(title)) // 2
        title_color = color_manager.get_color_pair_from_preset(ColorPreset.YELLOW)
        try:
            self.stdscr.addstr(
                start_y + 1,
                title_x,
                title,
                curses.A_BOLD | curses.color_pair(title_color),
            )
        except curses.error:
            pass

        art_start_y = start_y + 3
        art_start_x = start_x + (self.card_width - len(self.PLAYER_ART[0])) // 2

        art_color = color_manager.get_color_pair_from_preset(ColorPreset.GREEN)
        for i, line in enumerate(self.PLAYER_ART):
            if art_start_y + i < start_y + self.card_height - 1:
                try:
                    self.stdscr.addstr(
                        art_start_y + i,
                        art_start_x,
                        line,
                        curses.A_BOLD | curses.color_pair(art_color),
                    )
                except curses.error:
                    pass

        player = game.player
        stats = [
            ("HP", f"{player.hp}/{player.max_hp}"),
            ("STR", str(player.strength)),
            ("DEX", str(player.dexterity)),
            ("SCOPE", str(player.scope)),
            ("LEVEL", str(game.current_level_num)),
            ("TREASURE", f"${player.backpack.treasure}"),
            ("WEAPON", self._get_weapon_name(player)),
        ]

        stats_start_y = art_start_y + len(self.PLAYER_ART) + 1
        text_color = color_manager.get_color_pair_from_preset(ColorPreset.BRIGHT_TEXT)

        for i, (label, value) in enumerate(stats):
            y = stats_start_y + i
            if y < start_y + self.card_height - 2:
                label_str = f"{label}:"
                try:
                    self.stdscr.addstr(
                        y, start_x + 2, label_str, curses.color_pair(text_color)
                    )

                    value_x = start_x + 12

                    if label == "HP":
                        hp_percent = (
                            player.hp / player.max_hp if player.max_hp > 0 else 0
                        )
                        if hp_percent < 0.3:
                            hp_color = color_manager.get_color_pair_from_preset(
                                ColorPreset.RED
                            )
                        elif hp_percent < 0.6:
                            hp_color = color_manager.get_color_pair_from_preset(
                                ColorPreset.YELLOW
                            )
                        else:
                            hp_color = color_manager.get_color_pair_from_preset(
                                ColorPreset.GREEN
                            )
                        self.stdscr.addstr(
                            y,
                            value_x,
                            value,
                            curses.A_BOLD | curses.color_pair(hp_color),
                        )
                    else:
                        self.stdscr.addstr(
                            y, value_x, value, curses.color_pair(text_color)
                        )
                except curses.error:
                    pass

        try:
            sep_y = stats_start_y + len(stats) + 1
            if sep_y < start_y + self.card_height - 2:
                self.stdscr.addstr(sep_y, start_x + 1, "-" * (self.card_width - 2))
        except curses.error:
            pass

    def _get_weapon_name(self, player) -> str:
        """Возвращает название экипированного оружия."""
        if (
            hasattr(player.backpack, "equipped_weapon_index")
            and player.backpack.equipped_weapon_index > 0
        ):
            idx = player.backpack.equipped_weapon_index - 1
            if idx < len(player.backpack.weapon):
                return player.backpack.weapon[idx].name[:10]
        return "Fists"
