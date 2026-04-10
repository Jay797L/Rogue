import curses

from domain.base.core.base_game import BaseGame
from domain.base.data import STRINGS

from .ascii_anim import Animator, Art, TransformParams, Widget
from .color_manager import ColorPreset, color_manager


class GameOverRenderer:
    """Рендерер экрана Game Over, похожий на MenuRenderer."""

    def __init__(self, stdscr: curses.window):
        self.stdscr = stdscr
        self.frame = 0
        self.max_frames = 30
        self.is_victory = False
        self.game_over_art = None
        self.widget = None
        self.animator = None
        self.last_height = 0
        self.last_width = 0

    def _load_art(self, is_victory: bool):
        """Загружает соответствующий арт в зависимости от победы или смерти."""
        if is_victory:
            art_file = "win.txt"
            color = ColorPreset.GREEN.value
        else:
            art_file = "game_over.txt"
            color = ColorPreset.RED.value

        self.game_over_art = Art.from_file(art_file, color_hex=color)

        self.animator = Animator(
            base_params=TransformParams(scale_x=60, scale_y=60, skew=0),
            scale_x_amplitude=0,
            scale_y_amplitude=0,
            skew_amplitude=0,
            circle_radius_x=0,
            circle_radius_y=0,
            speed=2.0,
        )

        self.widget = Widget(
            art=self.game_over_art,
            y=0,
            x=0,
            selected_params=TransformParams(),
            animator=self.animator,
            color_hex=color,
            bg_color_hex="transparent",
        )

    def _update_widget_position(self, height: int, width: int) -> None:
        """Обновляет позицию виджета при изменении размера терминала."""
        if self.last_height == height and self.last_width == width:
            return

        self.widget.y = height // 4
        self.widget.x = width // 2

        self.last_height = height
        self.last_width = width

    def render(self, game: BaseGame) -> None:
        """Отрисовывает экран Game Over."""

        self.stdscr.clear()
        state = game.fsm.current_state_instance
        is_victory = getattr(state, "is_victory", False)

        if self.is_victory != is_victory or self.widget is None:
            self.is_victory = is_victory
            self._load_art(is_victory)

        height, width = self.stdscr.getmaxyx()
        self._update_widget_position(height, width)

        if self.widget:
            self.widget.draw(self.stdscr, self.frame / 10.0)

        # Use completed_run from state if available (finished run), otherwise current_run
        completed_run = getattr(state, "completed_run", None)
        if completed_run is not None:
            run_for_stats = completed_run
        else:
            run_for_stats = game.statistics.current_run

        if height >= 15 and width >= 40:
            self._render_statistics_with_run(run_for_stats, height, width)
            self._render_prompt(height, width)
        else:
            self._render_minimal_with_run(run_for_stats, height, width)

        self.stdscr.refresh()
        self.frame = (self.frame + 1) % self.max_frames

    def _render_statistics_with_run(self, stats, height: int, width: int) -> None:
        """Отображает статистику из переданного run."""

        title = "YOUR STATS"
        title_x = (width - len(title)) // 2
        title_y = height // 2 - 2

        if title_y >= 0 and title_x >= 0:
            title_color = color_manager.get_color_pair_from_preset(ColorPreset.YELLOW)
            self.stdscr.addstr(title_y, title_x, title, curses.color_pair(title_color))

        stats_lines = [
            ("Level reached", str(stats.max_level_reached)),
            ("Enemies killed", str(stats.enemies_killed)),
            ("Treasure", str(stats.total_treasure)),
            ("Food eaten", str(stats.food_eaten)),
            ("Elixirs drank", str(stats.elixirs_drank)),
            ("Scrolls read", str(stats.scrolls_read)),
            ("Cells moved", str(stats.cells_moved)),
        ]

        if stats.is_victory:
            stats_lines.append(("★ VICTORY! ★", "✓"))

        max_label_width = max(len(label) for label, _ in stats_lines)
        stats_start_y = title_y + 2
        text_color = color_manager.get_color_pair_from_preset(ColorPreset.BRIGHT_TEXT)

        for i, (label, value) in enumerate(stats_lines):
            y = stats_start_y + i
            if y >= height - 4:
                break

            label_x = (width - (max_label_width + 15)) // 2
            if label_x >= 0:
                self.stdscr.addstr(
                    y,
                    label_x,
                    label.ljust(max_label_width + 2),
                    curses.color_pair(text_color),
                )

            value_x = label_x + max_label_width + 4
            if value_x < width:
                if label == "★ VICTORY! ★":
                    victory_color = color_manager.get_color_pair_from_preset(
                        ColorPreset.GREEN
                    )
                    self.stdscr.addstr(
                        y,
                        value_x,
                        value,
                        curses.color_pair(victory_color),
                    )
                else:
                    self.stdscr.addstr(y, value_x, value, curses.color_pair(text_color))

    def _render_prompt(self, height: int, width: int) -> None:
        """Подсказка внизу экрана."""
        prompt = STRINGS.PRESS_Q_KEY_TO_RETURN_TO_MENU
        prompt_x = (width - len(prompt)) // 2
        prompt_y = height - 3

        if prompt_y >= 0 and prompt_x >= 0:
            prompt_color = color_manager.get_color_pair_from_preset(
                ColorPreset.DIM_TEXT
            )
            self.stdscr.addstr(
                prompt_y,
                prompt_x,
                prompt,
                curses.color_pair(prompt_color),
            )

    def _render_minimal_with_run(self, stats, height: int, width: int) -> None:
        """Упрощённая версия для маленьких экранов."""
        title = "GAME OVER"
        title_x = (width - len(title)) // 2
        title_y = max(0, height // 3)

        if title_x >= 0:
            death_color = color_manager.get_color_pair_from_preset(ColorPreset.RED)
            self.stdscr.addstr(title_y, title_x, title, curses.color_pair(death_color))

        stats_y = title_y + 2

        simple_stats = [
            f"Level: {stats.max_level_reached}",
            f"Kills: {stats.enemies_killed}",
            f"Treasure: {stats.total_treasure}",
        ]

        text_color = color_manager.get_color_pair_from_preset(ColorPreset.BRIGHT_TEXT)

        for i, line in enumerate(simple_stats):
            if stats_y + i < height:
                line_x = (width - len(line)) // 2
                if line_x >= 0:
                    self.stdscr.addstr(
                        stats_y + i, line_x, line, curses.color_pair(text_color)
                    )

        prompt = "Press any key"
        prompt_y = height - 2
        if prompt_y >= 0:
            prompt_x = (width - len(prompt)) // 2
            if prompt_x >= 0:
                prompt_color = color_manager.get_color_pair_from_preset(
                    ColorPreset.DIM_TEXT
                )
                self.stdscr.addstr(
                    prompt_y,
                    prompt_x,
                    prompt,
                    curses.color_pair(prompt_color),
                )
