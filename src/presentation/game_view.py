"""Curses-представление игры."""

import contextlib
import curses
import logging
import signal
import sys
import time
from collections import deque

from domain.base.core.base_game import BaseGame
from domain.base.core.base_game_view import BaseGameView
from domain.base.core.pixel import Pixel
from domain.base.data import STRINGS
from domain.game.state_machine.game_key import GameKey
from domain.game.state_machine.game_state import GameState
from presentation.game_over_renderer import GameOverRenderer
from presentation.inventory_renderer import InventoryRenderer
from presentation.load_game_renderer import LoadGameRenderer
from presentation.menu_renderer import MenuRenderer
from presentation.player_stats_renderer import PlayerStatsRenderer

from .color_manager import ColorPreset, color_manager

logger = logging.getLogger(__name__)


class CursesGameView(BaseGameView):
    def __init__(self, game: BaseGame):
        super().__init__(game)
        self.stdscr = curses.initscr()
        self.start_time = 0.0
        self.message_history = deque(maxlen=50)
        self.current_message = ""
        self.inventory_renderer = None
        self.menu_renderer = None
        self.game_over_renderer = None
        self.load_game_renderer = None
        self.player_stats_renderer = None
        self.message_area_height = 8
        self.stats_card_width = 25
        self.right_panel_x = 0
        self.resize_pending = False
        self.last_window_size = None

        game._game_view = self

    def _before_game_loop(self):
        curses.noecho()
        curses.cbreak()
        self.stdscr.keypad(True)
        curses.curs_set(0)
        self._init_colors()
        self.stdscr.nodelay(0)
        self.start_time = time.time()
        self.menu_renderer = MenuRenderer(self.stdscr)
        self.inventory_renderer = InventoryRenderer(self.stdscr)
        self.game_over_renderer = GameOverRenderer(self.stdscr)
        self.load_game_renderer = LoadGameRenderer(self.stdscr)
        self.player_stats_renderer = PlayerStatsRenderer(self.stdscr)
        self.original_sigint = signal.signal(signal.SIGINT, self._signal_handler)

        def handle_winch(signum, frame):
            self.resize_pending = True

            curses.endwin()
            curses.doupdate()

        try:
            self.original_winch = signal.signal(
                signal.SIGWINCH, self._handle_window_resize
            )
        except (AttributeError, OSError):
            # SIGWINCH not available - we'll poll on each frame
            self.original_winch = None
            logger.info("Window resize signal not available - using polling method")

    def _handle_window_resize(self, signum, frame):
        """Handle window resize signal (Unix only)."""
        self._check_window_resize()

    def _check_window_resize(self):
        """Check if window size changed and handle it."""
        try:
            current_size = (curses.LINES, curses.COLS)
            if self.last_window_size is None:
                self.last_window_size = current_size
                return
            if self.last_window_size != current_size:
                self.last_window_size = current_size
                # Force curses to reinitialize terminal after resize
                curses.endwin()
                curses.doupdate()
                self._on_window_resize()
        except curses.error:
            pass  # Curses not fully initialized yet

    def _on_window_resize(self):
        """Handle window resize event."""
        # Force curses to update its internal LINES/COLS after SIGWINCH
        try:
            curses.update_lines_cols()
        except AttributeError:
            # Fallback for older Python/curses implementations
            pass
        logger.info(f"Window resized to {curses.LINES}x{curses.COLS}")
        if not hasattr(self, "stdscr"):
            return
        try:
            # Update game screen dimensions immediately
            max_y, max_x = self.stdscr.getmaxyx()
            # For 3D mode, vision needs new dimensions
            if self.game.is_3d_mode and hasattr(self.game, "_3d_vision_instance"):
                self.game._3d_vision_instance.update_screen_dimensions(max_x, max_y)
            # Clear ray caster cache to avoid stale blocking data
            if hasattr(self.game, "level") and self.game.level and self.game.level.map_manager:
                if hasattr(self.game.level.map_manager, "ray_caster") and self.game.level.map_manager.ray_caster:
                    self.game.level.map_manager.ray_caster.clear_cache()
            # Mark resize as pending to trigger full redraw in next _render
            self.resize_pending = True
            # Invalidate vision cache for both 2D and 3D
            if hasattr(self.game, "_2d_vision_instance") and self.game._2d_vision_instance:
                if hasattr(self.game._2d_vision_instance, "_initialized"):
                    self.game._2d_vision_instance._initialized = False
                if hasattr(self.game._2d_vision_instance, "_wrapped") and hasattr(self.game._2d_vision_instance._wrapped, "_initialized"):
                    self.game._2d_vision_instance._wrapped._initialized = False
            if hasattr(self.game, "_3d_vision_instance") and self.game._3d_vision_instance:
                if hasattr(self.game._3d_vision_instance, "_initialized"):
                    self.game._3d_vision_instance._initialized = False
            # Clear screen to remove old artifacts
            self.stdscr.clear()
            self.stdscr.refresh()
        except (curses.error, AttributeError) as e:
            logger.debug(f"Error during window resize handling: {e}")

    def _signal_handler(self, signum, frame):
        """Обработчик Ctrl+C для корректного завершения."""
        logger.info("SIGINT received, shutting down gracefully...")
        self._cleanup_and_exit()

    def _cleanup_and_exit(self):
        """Очистка и выход из игры."""
        try:
            if self.stdscr is not None:
                curses.nocbreak()
                self.stdscr.keypad(False)
                curses.echo()
                curses.endwin()

            if self.original_sigint:
                signal.signal(signal.SIGINT, self.original_sigint)

            logger.info("Terminal restored successfully")
            sys.exit(0)
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
            sys.exit(1)

    def _after_game_loop(self):
        """Восстановление терминала."""

        if self.original_sigint:
            signal.signal(signal.SIGINT, self.original_sigint)
        if hasattr(self, "original_winch") and self.original_winch:
            signal.signal(signal.SIGWINCH, self.original_winch)

        if self.stdscr is not None:
            try:
                curses.nocbreak()
                self.stdscr.keypad(False)
                curses.echo()
            except Exception as e:
                logger.error(f"Ошибка curses: {e}")
            curses.endwin()

        if hasattr(self.game, "_game_view"):
            delattr(self.game, "_game_view")

    def _render(self):

        if self.resize_pending:
            self.resize_pending = False

            # Force clear and full refresh of terminal
            self.stdscr.clear()
            self.stdscr.refresh()
            # Reset cached dimensions for UI components
            if self.menu_renderer:
                self.menu_renderer.last_height = 0
                self.menu_renderer.last_width = 0
                self.menu_renderer.logo_widget = None
            if self.game_over_renderer:
                self.game_over_renderer.last_height = 0
                self.game_over_renderer.last_width = 0
                self.game_over_renderer.widget = None
            if hasattr(self, "about_renderer") and self.about_renderer:
                self.about_renderer.last_height = 0
                self.about_renderer.last_width = 0
                self.about_renderer.logo_widget = None
            # Invalidate vision cache for both 2D and 3D
            if hasattr(self.game, "_2d_vision_instance") and self.game._2d_vision_instance:
                if hasattr(self.game._2d_vision_instance, "_initialized"):
                    self.game._2d_vision_instance._initialized = False
                if hasattr(self.game._2d_vision_instance, "_wrapped") and hasattr(self.game._2d_vision_instance._wrapped, "_initialized"):
                    self.game._2d_vision_instance._wrapped._initialized = False
            if hasattr(self.game, "_3d_vision_instance") and self.game._3d_vision_instance:
                if hasattr(self.game._3d_vision_instance, "_initialized"):
                    self.game._3d_vision_instance._initialized = False
            # Clear ray caster cache again
            if hasattr(self.game, "level") and self.game.level and self.game.level.map_manager:
                if hasattr(self.game.level.map_manager, "ray_caster") and self.game.level.map_manager.ray_caster:
                    self.game.level.map_manager.ray_caster.clear_cache()
            # Also update game screen dimensions based on new terminal size
            max_y, max_x = self.stdscr.getmaxyx()
            self.game.update_screen_size(max_x, max_y)

        current_time = time.time() - self.start_time

        if self.game.fsm.current_state == GameState.MENU:
            if (
                hasattr(self.game.fsm.current_state_instance, "show_stats")
                and self.game.fsm.current_state_instance.show_stats
            ):
                self._render_statistics()
            else:
                self.menu_renderer.render(self.game, current_time)
        elif self.game.fsm.current_state == GameState.INVENTORY:
            self.stdscr.erase()
            self._draw_map_border()
            self._draw_message_border()
            self._render_status()
            self._render_map()
            self._render_messages()

            self.inventory_renderer.render(self.game)
            self.stdscr.refresh()
            return
        elif self.game.fsm.current_state == GameState.GAME_OVER:
            self.game_over_renderer.render(self.game)
        elif self.game.fsm.current_state == GameState.LOAD_GAME:
            self.load_game_renderer.render(self.game)
        elif (
            self.game.fsm.current_state == GameState.ABOUT
            or self.game.fsm.current_state == GameState.ABOUT
        ):
            state = self.game.fsm.current_state_instance
            if state.renderer:
                state.renderer.render(current_time)
            else:
                self.stdscr.erase()
                height, width = self.stdscr.getmaxyx()
                msg = "Loading about screen..."
                x = (width - len(msg)) // 2
                y = height // 2
                self.stdscr.addstr(y, x, msg)
                self.stdscr.refresh()
        elif self.game.fsm.current_state == GameState.SETTINGS:
            state = self.game.fsm.current_state_instance
            if state.renderer:
                state.renderer.render()
            else:
                self.stdscr.erase()
                height, width = self.stdscr.getmaxyx()
                msg = "Loading settings..."
                x = (width - len(msg)) // 2
                y = height // 2
                self.stdscr.addstr(y, x, msg)
                self.stdscr.refresh()
        elif self.game.fsm.current_state in (
            GameState.EXPLORING,
            GameState.EXPLORING_3D,
        ):
            self.stdscr.erase()
            if not self.game.game_started:
                height, width = self.stdscr.getmaxyx()
                msg = "Game not started. Press Q to return to menu."
                x = (width - len(msg)) // 2
                y = height // 2
                self.stdscr.addstr(y, x, msg)
                self.stdscr.refresh()
                return

            self._draw_map_border()
            self._draw_message_border()
            self._render_status()
            self._render_map()
            self._render_messages()
            self.stdscr.refresh()
        else:
            self.stdscr.erase()
            self.stdscr.refresh()

    def _get_input(self) -> GameKey:
        current_state = self.game.fsm.current_state

        if current_state in (GameState.MENU, GameState.LOAD_GAME):
            self.stdscr.nodelay(1)
            try:
                key = self.stdscr.get_wch()
            except KeyboardInterrupt:
                self._cleanup_and_exit()
                return GameKey.KEY_Q
            except curses.error:
                # Fallback to getch if get_wch fails
                try:
                    key_code = self.stdscr.getch()
                    if key_code == -1:
                        return GameKey.NOPE
                    key = key_code
                except:
                    return GameKey.NOPE

            curses.napms(30)
            if key == -1:
                curses.napms(30)
                return GameKey.NOPE
        else:
            self.stdscr.nodelay(False)
            try:
                key = self.stdscr.get_wch()
            except KeyboardInterrupt:
                self._cleanup_and_exit()
                return GameKey.KEY_Q
            except curses.error:
                try:
                    key_code = self.stdscr.getch()
                    key = key_code
                except:
                    return GameKey.NOPE

        # Обработка специальных клавиш
        if isinstance(key, int):
            if key == 3:  # Ctrl+C
                self._cleanup_and_exit()
                return GameKey.KEY_Q
            if key in (curses.KEY_ENTER, 10, 13):
                return GameKey.SELECT
            if key in (curses.KEY_BACKSPACE, 127):
                return GameKey.BACKSPACE
            if key == curses.KEY_UP:
                return GameKey.KEY_W
            if key == curses.KEY_DOWN:
                return GameKey.KEY_S
            if key == curses.KEY_LEFT:
                return GameKey.KEY_A
            if key == curses.KEY_RIGHT:
                return GameKey.KEY_D
            # Если это обычный код символа, преобразуем в символ
            try:
                key = chr(key)
            except:
                return GameKey.NOPE

        # key теперь строка (символ)
        return BaseGameView.get_action_from_char(key)

    def _render_statistics(self):
        """Отображает таблицу статистики."""
        self.stdscr.erase()
        height, width = self.stdscr.getmaxyx()

        title = STRINGS.STATS_TITLE
        title_x = (width - len(title)) // 2
        self.stdscr.addstr(1, title_x, title, curses.A_BOLD)

        top_runs = self.game.statistics.get_top_runs(10)

        if not top_runs:
            self.stdscr.addstr(3, 2, STRINGS.STATS_NO_DATA)
            self.stdscr.addstr(height - 2, 2, STRINGS.PRESS_Q_KEY_TO_RETURN_TO_MENU)
            self.stdscr.refresh()
            return

        headers = [
            STRINGS.STATS_HEADER_NUM,
            STRINGS.STATS_HEADER_TREASURE,
            STRINGS.STATS_HEADER_LEVEL,
            STRINGS.STATS_HEADER_KILLS,
            STRINGS.STATS_HEADER_FOOD,
            STRINGS.STATS_HEADER_ELIXIR,
            STRINGS.STATS_HEADER_SCROLLS,
            STRINGS.STATS_HEADER_VICTORY,
        ]
        header_x = 2
        for i, header in enumerate(headers):
            self.stdscr.addstr(3, header_x + i * 10, header[:10], curses.A_BOLD)

        for idx, run in enumerate(top_runs[:10]):
            y = 4 + idx
            if y >= height - 2:
                break

            victory_mark = STRINGS.STATS_VICTORY_MARK.value if run.is_victory else " "
            row_data = [
                f"{idx + 1:>2}",
                f"{run.total_treasure:>8}",
                f"{run.max_level_reached:>5}",
                f"{run.enemies_killed:>5}",
                f"{run.food_eaten:>4}",
                f"{run.elixirs_drank:>6}",
                f"{run.scrolls_read:>6}",
                f"{victory_mark:>7}",
            ]

            for i, data in enumerate(row_data):
                self.stdscr.addstr(y, header_x + i * 10, data)

        summary = self.game.statistics.get_stats_summary()
        summary_y = height - 4
        self.stdscr.addstr(
            summary_y,
            2,
            STRINGS.STATS_SUMMARY.format(
                summary["total_runs"], summary["best_treasure"], summary["best_level"]
            ),
        )

        self.stdscr.addstr(height - 2, 2, STRINGS.PRESS_Q_KEY_TO_RETURN_TO_MENU)
        self.stdscr.refresh()

    def _draw_map_border(self):
        """Рисует рамку вокруг игрового поля."""
        max_y, max_x = self.stdscr.getmaxyx()

        if max_y < 10 or max_x < 20:
            return

        stats_width = self.stats_card_width + 4
        self.right_panel_x = max_x - stats_width

        map_start_y = 2
        map_end_y = max_y - 2
        map_start_x = 1
        map_end_x = self.right_panel_x - 2

        if map_start_y - 1 < 0 or map_end_y + 1 >= max_y:
            return
        if map_start_x - 1 < 0 or map_end_x + 1 >= max_x:
            return

        border_color = color_manager.get_color_pair_from_preset(ColorPreset.BORDER)

        try:
            self.stdscr.addstr(map_start_y - 1, map_start_x - 1, "+")
            self.stdscr.addstr(
                map_start_y - 1, map_start_x, "-" * (map_end_x - map_start_x + 1)
            )
            self.stdscr.addstr(map_start_y - 1, map_end_x + 1, "+")
        except curses.error:
            pass

        for y in range(map_start_y, map_end_y + 1):
            try:
                self.stdscr.addstr(y, map_start_x - 1, "|")
                self.stdscr.addstr(y, map_end_x + 1, "|")
            except curses.error:
                pass

        try:
            self.stdscr.addstr(map_end_y + 1, map_start_x - 1, "+")
            self.stdscr.addstr(
                map_end_y + 1, map_start_x, "-" * (map_end_x - map_start_x + 1)
            )
            self.stdscr.addstr(map_end_y + 1, map_end_x + 1, "+")
        except curses.error:
            pass

        title = STRINGS.MAP_TITLE
        title_x = map_start_x + (map_end_x - map_start_x - len(title)) // 2
        try:
            if title_x >= 0:
                self.stdscr.addstr(
                    map_start_y - 1,
                    title_x,
                    title,
                    curses.A_BOLD | curses.color_pair(border_color),
                )
        except curses.error:
            pass

        save_hint = STRINGS.SAVE_HINT
        hint_x = map_start_x + (map_end_x - map_start_x - len(save_hint)) // 2
        hint_y = map_end_y + 2
        if hint_y < max_y:
            hint_color = color_manager.get_color_pair_from_preset(ColorPreset.DIM_TEXT)
            self.stdscr.addstr(
                hint_y,
                hint_x,
                save_hint,
                curses.A_DIM | curses.color_pair(hint_color),
            )

    def _draw_message_border(self):
        """Рисует рамку вокруг окна сообщений (справа, под карточкой статистики)."""
        max_y, max_x = self.stdscr.getmaxyx()

        if max_y < 10 or max_x < 20:
            return

        stats_width = self.stats_card_width + 4
        right_panel_x = max_x - stats_width

        stats_height = 12
        msg_start_y = 2 + stats_height + 1
        msg_end_y = max_y - 2
        msg_start_x = right_panel_x + 1
        msg_end_x = max_x - 2

        if msg_start_y > msg_end_y:
            return

        border_color = color_manager.get_color_pair_from_preset(ColorPreset.BORDER)

        try:
            self.stdscr.addstr(msg_start_y - 1, msg_start_x - 1, "+")
            self.stdscr.addstr(
                msg_start_y - 1, msg_start_x, "-" * (msg_end_x - msg_start_x + 1)
            )
            self.stdscr.addstr(msg_start_y - 1, msg_end_x + 1, "+")
        except curses.error:
            pass

        for y in range(msg_start_y, msg_end_y + 1):
            try:
                self.stdscr.addstr(y, msg_start_x - 1, "|")
                self.stdscr.addstr(y, msg_end_x + 1, "|")
            except curses.error:
                pass

        try:
            self.stdscr.addstr(msg_end_y + 1, msg_start_x - 1, "+")
            self.stdscr.addstr(
                msg_end_y + 1, msg_start_x, "-" * (msg_end_x - msg_start_x + 1)
            )
            self.stdscr.addstr(msg_end_y + 1, msg_end_x + 1, "+")
        except curses.error:
            pass

        title = STRINGS.MESSAGES_TITLE
        title_x = msg_start_x + (msg_end_x - msg_start_x - len(title)) // 2
        try:
            if title_x >= 0:
                self.stdscr.addstr(
                    msg_start_y - 1,
                    title_x,
                    title,
                    curses.A_BOLD | curses.color_pair(border_color),
                )
        except curses.error:
            pass

    def _get_terminal_size(self):
        """Возвращает размер терминала."""
        max_y, max_x = self.stdscr.getmaxyx()
        return max_x, max_y

    def _render_map(self):
        """Отрисовывает карту с туманом войны."""
        pixels: list[Pixel] = self.game.get_map()
        max_y, max_x = self.stdscr.getmaxyx()

        if max_y < 10 or max_x < 20:
            return

        stats_width = self.stats_card_width + 4
        right_panel_x = max_x - stats_width

        map_width = right_panel_x - 4
        map_height = max_y - 4
        self.game.update_screen_size(map_width, map_height)

        map_start_y = 2
        map_end_y = max_y - 2
        map_start_x = 2
        map_end_x = right_panel_x - 2

        if map_start_y > map_end_y or map_start_x > map_end_x:
            return

        map_height = map_end_y - map_start_y + 1
        map_width = map_end_x - map_start_x + 1

        cam_y, cam_x = self.game.get_cam
        half_h = map_height // 2
        half_w = map_width // 2
        min_y = cam_y - half_h
        min_x = cam_x - half_w

        self.stdscr.attroff(curses.A_BOLD)
        self.stdscr.attroff(curses.A_REVERSE)
        self.stdscr.attroff(curses.A_UNDERLINE)

        for y in range(map_start_y, map_end_y + 1):
            with contextlib.suppress(curses.error):
                self.stdscr.addstr(y, map_start_x, " " * map_width)

        for pixel in pixels:
            screen_y = pixel.y - min_y + map_start_y
            screen_x = pixel.x - min_x + map_start_x
            if (
                not map_start_y <= screen_y <= map_end_y
                or not map_start_x <= screen_x <= map_end_x
            ):
                continue

            if isinstance(pixel.color, str) and pixel.color.startswith("#"):
                color_pair = color_manager.get_color_pair(pixel.color, "transparent")
            else:
                color_map = {
                    1: ColorPreset.WHITE,
                    2: ColorPreset.RED,
                    3: ColorPreset.GREEN,
                    4: ColorPreset.YELLOW,
                    5: ColorPreset.BLUE,
                    6: ColorPreset.PERVANCHE,
                    7: ColorPreset.MAGENTA,
                }
                preset = color_map.get(int(pixel.color), ColorPreset.WHITE)
                color_pair = color_manager.get_color_pair_from_preset(preset)

            self.stdscr.attron(curses.color_pair(color_pair))
            with contextlib.suppress(curses.error):
                self.stdscr.addstr(screen_y, screen_x, pixel.content)
            self.stdscr.attroff(curses.color_pair(color_pair))

    def _render_status(self):
        """Отображает статус игрока: карточка статистики справа вверху."""
        max_y, max_x = self.stdscr.getmaxyx()

        if self.player_stats_renderer and self.game.fsm.current_state in (
            GameState.EXPLORING,
            GameState.EXPLORING_3D,
        ):
            stats_width = self.stats_card_width + 4
            stats_x = max_x - stats_width + 1
            stats_y = 2
            self.player_stats_renderer.render(self.game, stats_x, stats_y)

    @staticmethod
    def _wrap_message(text: str, width: int) -> list[str]:
        """Разбивает длинное сообщение на несколько строк по ширине."""
        if width <= 0:
            return [text]

        if len(text) <= width:
            return [text]

        lines = []
        prefix = ""
        remaining = text
        if text.startswith("> "):
            prefix = "> "
            remaining = text[2:]
        while len(remaining) > width - len(prefix):
            break_pos = width - len(prefix)
            last_space = remaining.rfind(" ", 0, break_pos)
            if last_space > 0:
                lines.append(prefix + remaining[:last_space])
                prefix = "  "
                remaining = remaining[last_space + 1 :]
            else:
                lines.append(prefix + remaining[:break_pos])
                prefix = "  "
                remaining = remaining[break_pos:]

        if remaining or not lines:
            lines.append(prefix + remaining)

        return lines

    def _render_messages(self):
        """Отображает игровые сообщения с историей и переносом длинных строк."""
        message = self.game.message
        if message is not None:
            self.current_message = message
            self.message_history.appendleft(f"> {message}")

        max_y, max_x = self.stdscr.getmaxyx()

        if max_y < 10 or max_x < 20:
            return

        stats_width = self.stats_card_width + 4
        right_panel_x = max_x - stats_width

        stats_height = 12
        msg_start_y = 2 + stats_height + 2
        msg_end_y = max_y - 2
        msg_start_x = right_panel_x + 2
        msg_end_x = max_x - 2

        if msg_start_y > msg_end_y:
            return

        msg_height = msg_end_y - msg_start_y + 1
        msg_width = msg_end_x - msg_start_x + 1

        if msg_width <= 0:
            return

        for y in range(msg_start_y, msg_end_y + 1):
            with contextlib.suppress(curses.error):
                self.stdscr.addstr(y, msg_start_x, " " * msg_width)

        wrapped_messages = []
        for msg in self.message_history:
            wrapped_lines = self._wrap_message(msg, msg_width)
            wrapped_messages.extend(wrapped_lines)

        messages_to_show = wrapped_messages[:msg_height]

        for idx, msg in enumerate(messages_to_show):
            if idx >= msg_height:
                break

            msg_lower = msg.lower()
            is_death = "game over" in msg_lower or "вы умерли" in msg_lower
            is_victory = (
                "victory" in msg_lower
                or "победа" in msg_lower
                or "прошли все" in msg_lower
            )

            try:
                if is_death:
                    death_color = color_manager.get_color_pair_from_preset(
                        ColorPreset.RED
                    )
                    self.stdscr.addstr(
                        msg_start_y + idx,
                        msg_start_x,
                        msg[:msg_width],
                        curses.A_BOLD | curses.color_pair(death_color),
                    )
                elif is_victory:
                    victory_color = color_manager.get_color_pair_from_preset(
                        ColorPreset.GREEN
                    )
                    self.stdscr.addstr(
                        msg_start_y + idx,
                        msg_start_x,
                        msg[:msg_width],
                        curses.A_BOLD | curses.color_pair(victory_color),
                    )
                else:
                    msg_color = color_manager.get_color_pair_from_preset(
                        ColorPreset.DIM_TEXT
                    )
                    self.stdscr.addstr(
                        msg_start_y + idx,
                        msg_start_x,
                        msg[:msg_width],
                        curses.A_DIM | curses.color_pair(msg_color),
                    )
            except curses.error:
                pass

    @staticmethod
    def _init_colors():
        """Инициализация цветов через единый менеджер."""
        if not curses.has_colors():
            return
        curses.start_color()
        curses.use_default_colors()
        color_manager.init_basic_colors()
