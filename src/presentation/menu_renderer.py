import curses

from domain.base.core.base_game import BaseGame
from domain.base.data import STRINGS
from domain.game.states.menu_state import MenuState

from .ascii_anim import Animator, Art, TransformParams, Widget
from .color_manager import ColorPreset, color_manager


class MenuRenderer:
    def __init__(self, stdscr: curses.window):
        self.stdscr = stdscr
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
            return False

        if self.logo_widget is None:
            self.logo_widget = Widget(
                art=self.logo_art,
                y=height // 4,
                x=width // 2,
                animator=self.logo_animator,
                color_hex=ColorPreset.LOGO_GREEN.value,
                bg_color_hex="transparent",
            )
        else:
            self.logo_widget.y = height // 4
            self.logo_widget.x = width // 2

        self.last_height = height
        self.last_width = width
        return True

    def render(self, game: BaseGame, current_time: float):

        self.stdscr.clear()

        self.stdscr.attrset(0)
        self.stdscr.bkgd(" ", 0)
        color_manager.init_basic_colors()

        height, width = self.stdscr.getmaxyx()

        if self.logo_widget is None:
            self.logo_widget = Widget(
                art=self.logo_art,
                y=height // 4,
                x=width // 2,
                animator=self.logo_animator,
                color_hex=ColorPreset.LOGO_GREEN.value,
                bg_color_hex="transparent",
            )
        else:
            self.logo_widget.y = height // 4
            self.logo_widget.x = width // 2

        if self.logo_widget:
            self.stdscr.attrset(0)
            self.logo_widget.draw(self.stdscr, current_time)

        menu_start_y = height // 2
        if game.fsm.current_state.name != "MENU":
            self.stdscr.refresh()
            return

        state: MenuState = game.fsm.current_state_instance
        if not state.menu_items:
            self.stdscr.refresh()
            return

        max_item_len = max(len(item.value) for item in state.menu_items)

        for i, item in enumerate(state.menu_items):
            y = menu_start_y + i
            if y >= height - 1:
                continue

            if i == state.menu_selection:
                padded_item = item.value.center(max_item_len)
                formatted_item = STRINGS.MENU_SELECTION_FORMAT.format(padded_item)
                x = (width - len(formatted_item)) // 2
                if x >= 0:
                    self.stdscr.attron(curses.A_REVERSE)
                    self.stdscr.addstr(y, x, formatted_item)
                    self.stdscr.attroff(curses.A_REVERSE)
            else:
                padded_item = item.value.center(max_item_len)
                x = (width - len(padded_item)) // 2
                if x >= 0:
                    text_color = color_manager.get_color_pair_from_preset(
                        ColorPreset.BRIGHT_TEXT
                    )
                    self.stdscr.attron(curses.color_pair(text_color))
                    self.stdscr.addstr(y, x, padded_item)
                    self.stdscr.attroff(curses.color_pair(text_color))

        prompt = STRINGS.MAIN_MENU_PROMT
        prompt_x = (width - len(prompt)) // 2
        prompt_y = menu_start_y + len(state.menu_items) + 1
        if prompt_y < height and prompt_x >= 0:
            prompt_color = color_manager.get_color_pair_from_preset(
                ColorPreset.DIM_TEXT
            )
            self.stdscr.addstr(
                prompt_y,
                prompt_x,
                prompt,
                curses.A_DIM | curses.color_pair(prompt_color),
            )

        self.stdscr.attroff(curses.A_BOLD)
        self.stdscr.attroff(curses.A_REVERSE)
        self.stdscr.attroff(curses.A_UNDERLINE)
        self.stdscr.attroff(curses.A_DIM)

        self.stdscr.refresh()
