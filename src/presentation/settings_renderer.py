"""Settings renderer."""

import curses

from presentation.color_manager import ColorPreset, color_manager


class SettingsRenderer:
    """Renders the settings screen."""

    def __init__(self, stdscr: curses.window):
        self.stdscr = stdscr
        self.music_enabled = True

    def set_music_enabled(self, enabled: bool):
        """Set music enabled state."""
        self.music_enabled = enabled

    def render(self):
        """Render the settings screen."""
        self.stdscr.clear()
        height, width = self.stdscr.getmaxyx()

        title = "SETTINGS"
        title_x = (width - len(title)) // 2
        title_color = color_manager.get_color_pair_from_preset(ColorPreset.YELLOW)
        try:
            self.stdscr.addstr(
                2, title_x, title, curses.A_BOLD | curses.color_pair(title_color)
            )
        except curses.error:
            pass

        start_y = 5

        music_label = "Music:"
        music_status = "ON" if self.music_enabled else "OFF"
        music_status_color = (
            ColorPreset.GREEN if self.music_enabled else ColorPreset.RED
        )
        status_color = color_manager.get_color_pair_from_preset(music_status_color)

        try:
            self.stdscr.addstr(start_y, 5, music_label)
            self.stdscr.addstr(
                start_y,
                20,
                music_status,
                curses.A_BOLD | curses.color_pair(status_color),
            )
        except curses.error:
            pass

        hint_y = start_y + 3
        hint_text = "M - Toggle Music"
        hint_color = color_manager.get_color_pair_from_preset(ColorPreset.DIM_TEXT)
        try:
            self.stdscr.addstr(
                hint_y, 5, hint_text, curses.A_DIM | curses.color_pair(hint_color)
            )
        except curses.error:
            pass

        prompt_y = height - 3
        prompt_text = "Q - Back to menu"
        prompt_x = (width - len(prompt_text)) // 2
        if prompt_y >= 0 and prompt_x >= 0:
            prompt_color = color_manager.get_color_pair_from_preset(
                ColorPreset.DIM_TEXT
            )
            try:
                self.stdscr.addstr(
                    prompt_y,
                    prompt_x,
                    prompt_text,
                    curses.A_DIM | curses.color_pair(prompt_color),
                )
            except curses.error:
                pass

        self.stdscr.refresh()
