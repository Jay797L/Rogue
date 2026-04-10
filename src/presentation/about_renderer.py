"""Рендерер экрана About с логотипом и прокручиваемым текстом."""

import curses
import logging

from presentation.ascii_anim import Animator, Art, TransformParams, Widget
from presentation.color_manager import ColorPreset, color_manager

logger = logging.getLogger(__name__)


class AboutRenderer:
    """Рендерер экрана About с логотипом и прокручиваемым текстом."""

    about_text = [
        "ROGUES 21",
        "by leerov and jay",
        "A Roguelike Adventure",
        "",
        "CONTROLS",
        "--------",
        "Movement (2D mode):",
        "  W/A/S/D or K/J/H/L - Move in 4 directions",
        "",
        "Movement (3D mode):",
        "  W/S - Move forward/backward",
        "  A/D - Rotate left/right",
        "  Q/E - Strafe left/right",
        "  V   - Switch between 2D/3D mode",
        "",
        "General:",
        "  I       - Open inventory",
        "  S       - Save game",
        "  Q       - Quit to menu / Exit game",
        "  Enter   - Select / Use item",
        "",
        "INVENTORY",
        "----------",
        "Categories: A - Food, S - Potions, D - Scrolls, F - Weapons",
        "Slots: 1-9 - Select item",
        "Enter - Use selected item",
        "Backspace - Drop item",
        "0 - Unequip weapon",
        "",
        "GAMEPLAY",
        "---------",
        "• Defeat enemies to gain treasure",
        "• Collect food, potions, and scrolls to heal and buff",
        "• Find keys to open locked doors",
        "• Survive all 21 levels to win!",
        "• Enemies become stronger on deeper levels",
        "• Elite and Boss enemies drop more treasure",
        "",
        "ENEMIES",
        "--------",
        "Zombie      - Basic undead enemy",
        "Ghost       - Passes through walls, hard to hit",
        "Ogr         - High damage, slow",
        "Snake Mage  - Can stun you",
        "Vampire     - Heals when attacking",
        "Mimik       - Disguised as an item, attacks when hit",
        "",
        "ITEMS",
        "------",
        "Food (f)      - Restores HP",
        "Potions (!)   - Temporary stat boosts or regeneration",
        "Scrolls (?)   - Permanent stat increases",
        "Weapons (/)   - Increase attack damage",
        "",
        "Good luck, adventurer!",
    ]

    def __init__(self, stdscr: curses.window):
        self.stdscr = stdscr
        self.scroll_offset = 0
        self.max_scroll = 0
        self.viewport_height = 0

        self.logo_art = Art.from_file(
            "logo.txt", color_hex=ColorPreset.LOGO_GREEN.value
        )
        self.logo_animator = Animator(
            base_params=TransformParams(scale_x=40, scale_y=60, skew=-50),
            circle_radius_x=5,
            circle_radius_y=1,
            speed=0.6,
            skew_amplitude=25,
        )
        self.logo_widget = None
        self.last_height = 0
        self.last_width = 0

    def _update_logo_position(self, height: int, width: int):
        """Обновляет позицию логотипа при изменении размера терминала."""
        if (
            self.last_height == height
            and self.last_width == width
            and self.logo_widget is not None
        ):
            return

        if self.logo_widget is None:
            self.logo_widget = Widget(
                art=self.logo_art,
                y=height // 6,
                x=width // 2,
                animator=self.logo_animator,
                color_hex=ColorPreset.LOGO_GREEN.value,
                bg_color_hex="transparent",
            )
        else:
            self.logo_widget.y = height // 6
            self.logo_widget.x = width // 2

        self.last_height = height
        self.last_width = width

    def scroll_up(self):
        """Прокрутка вверх."""
        if self.scroll_offset > 0:
            self.scroll_offset -= 1

    def scroll_down(self):
        """Прокрутка вниз."""
        if self.scroll_offset < self.max_scroll:
            self.scroll_offset += 1

    def render(self, current_time: float):
        """Отрисовывает экран About."""
        self.stdscr.clear()
        height, width = self.stdscr.getmaxyx()

        self._update_logo_position(height, width)

        if self.logo_widget:
            self.logo_widget.draw(self.stdscr, current_time)

        text_start_y = height // 3 + 2
        text_start_x = max(5, (width - 60) // 2)
        text_width = min(60, width - 10)
        self.viewport_height = max(0, height - text_start_y - 3)

        if self.viewport_height <= 0:
            # Terminal too small to show text area; only logo and prompt remain
            prompt_y = height - 2
            prompt = "↑/↓ or W/S or K/J - scroll, Q - back to menu"
            prompt_x = (width - len(prompt)) // 2
            if prompt_y >= 0 and prompt_x >= 0:
                prompt_color = color_manager.get_color_pair_from_preset(
                    ColorPreset.DIM_TEXT
                )
                self.stdscr.addstr(
                    prompt_y,
                    prompt_x,
                    prompt,
                    curses.A_DIM | curses.color_pair(prompt_color),
                )
            self.stdscr.refresh()
            return

        color_manager.get_color_pair_from_preset(ColorPreset.BORDER)
        try:
            self.stdscr.addstr(text_start_y - 1, text_start_x - 1, "+")
            self.stdscr.addstr(text_start_y - 1, text_start_x, "-" * (text_width + 2))
            self.stdscr.addstr(text_start_y - 1, text_start_x + text_width + 1, "+")

            for i in range(self.viewport_height):
                self.stdscr.addstr(text_start_y + i, text_start_x - 1, "|")
                self.stdscr.addstr(text_start_y + i, text_start_x + text_width + 1, "|")

            self.stdscr.addstr(
                text_start_y + self.viewport_height, text_start_x - 1, "+"
            )
            self.stdscr.addstr(
                text_start_y + self.viewport_height,
                text_start_x,
                "-" * (text_width + 2),
            )
            self.stdscr.addstr(
                text_start_y + self.viewport_height, text_start_x + text_width + 1, "+"
            )
        except curses.error:
            pass

        title = "ABOUT"
        title_x = text_start_x + (text_width + 2 - len(title)) // 2
        try:
            title_color = color_manager.get_color_pair_from_preset(ColorPreset.YELLOW)
            self.stdscr.addstr(
                text_start_y - 1,
                title_x,
                title,
                curses.A_BOLD | curses.color_pair(title_color),
            )
        except curses.error:
            pass

        self.max_scroll = max(0, len(self.about_text) - self.viewport_height)

        text_color = color_manager.get_color_pair_from_preset(ColorPreset.BRIGHT_TEXT)
        visible_lines = self.about_text[
            self.scroll_offset : self.scroll_offset + self.viewport_height
        ]

        for i, line in enumerate(visible_lines):
            y = text_start_y + i
            if y >= height - 1:
                break

            if len(line) > text_width:
                line = line[: text_width - 3] + "..."

            try:
                if line and line.isupper() and len(line) > 3:
                    self.stdscr.addstr(
                        y,
                        text_start_x,
                        line.ljust(text_width),
                        curses.A_BOLD | curses.color_pair(text_color),
                    )
                elif line.startswith("•"):
                    self.stdscr.addstr(
                        y,
                        text_start_x,
                        line.ljust(text_width),
                        curses.color_pair(text_color),
                    )
                else:
                    self.stdscr.addstr(
                        y,
                        text_start_x,
                        line.ljust(text_width),
                        curses.A_DIM | curses.color_pair(text_color),
                    )
            except curses.error:
                pass

        prompt_y = height - 2
        prompt = "↑/↓ or W/S or K/J - scroll, Q - back to menu"
        prompt_x = (width - len(prompt)) // 2
        if prompt_y >= 0 and prompt_x >= 0:
            prompt_color = color_manager.get_color_pair_from_preset(
                ColorPreset.DIM_TEXT
            )
            self.stdscr.addstr(
                prompt_y,
                prompt_x,
                prompt,
                curses.A_DIM | curses.color_pair(prompt_color),
            )

        if self.max_scroll > 0:
            scroll_percent = (
                self.scroll_offset / self.max_scroll if self.max_scroll > 0 else 0
            )
            indicator_height = max(1, int(self.viewport_height * 0.1))
            indicator_pos = int(
                scroll_percent * (self.viewport_height - indicator_height)
            )
            scroll_y = text_start_y + indicator_pos

            try:
                self.stdscr.addstr(scroll_y, text_start_x + text_width + 2, "█")
            except curses.error as e:
                logger.exception(e)

        self.stdscr.refresh()
