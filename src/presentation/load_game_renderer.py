import curses

from domain.base.core.base_game import BaseGame
from domain.base.data import STRINGS

from .color_manager import ColorPreset, color_manager


class LoadGameRenderer:
    """Рендерер экрана загрузки сохранений."""

    def __init__(self, stdscr: curses.window):
        self.stdscr = stdscr

    def render(self, game: BaseGame):
        """Отрисовывает экран загрузки сохранений."""
        self.stdscr.clear()
        height, width = self.stdscr.getmaxyx()

        title = STRINGS.LOAD_GAME
        title_x = (width - len(title)) // 2
        title_color = color_manager.get_color_pair_from_preset(ColorPreset.YELLOW)
        self.stdscr.addstr(
            2, title_x, title, curses.A_BOLD | curses.color_pair(title_color)
        )

        state = game.fsm.current_state_instance
        saves_info = state.get_saves_info() if hasattr(state, "get_saves_info") else []

        if not saves_info:
            no_saves_msg = STRINGS.NO_SAVED_GAMES
            msg_x = (width - len(no_saves_msg)) // 2
            msg_y = height // 2
            self.stdscr.addstr(msg_y, msg_x, no_saves_msg)
        else:
            start_y = 5
            max_width = width - 20

            for i, save_info in enumerate(saves_info):
                y = start_y + i
                if y >= height - 5:
                    break

                save_type_display = "АВТО" if save_info["type"] == "AUTO" else "РУЧН"
                save_str = f"[{save_type_display}] Уровень {save_info['level']} - {save_info['timestamp']}"

                if len(save_str) > max_width:
                    save_str = save_str[: max_width - 3] + "..."

                if i == state.selected_index:
                    self.stdscr.attron(curses.A_REVERSE)
                    self.stdscr.addstr(y, 5, f"> {save_str}")
                    self.stdscr.attroff(curses.A_REVERSE)
                else:
                    text_color = color_manager.get_color_pair_from_preset(
                        ColorPreset.BRIGHT_TEXT
                    )
                    self.stdscr.attron(curses.color_pair(text_color))
                    self.stdscr.addstr(y, 5, f"  {save_str}")
                    self.stdscr.attroff(curses.color_pair(text_color))

        help_y = height - 3
        if help_y >= 0:
            help_text = STRINGS.HELP_LOAD_GAME
            help_x = (width - len(help_text)) // 2
            help_color = color_manager.get_color_pair_from_preset(ColorPreset.DIM_TEXT)
            self.stdscr.addstr(
                help_y, help_x, help_text, curses.A_DIM | curses.color_pair(help_color)
            )

        self.stdscr.refresh()
