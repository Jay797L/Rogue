"""Состояние главного меню."""

from __future__ import annotations

import contextlib
import time
from typing import TYPE_CHECKING

from domain.base.data import STRINGS
from domain.game.state_machine.game_key import GameKey
from domain.game.state_machine.game_state import GameState

from .base_state import GameStateBase

if TYPE_CHECKING:
    from domain.game.core.game import Game


class MenuState(GameStateBase):
    def __init__(self, game: "Game"):
        super().__init__(game)
        self.menu_items = []
        self.menu_selection = 0
        self.show_stats = False
        self._update_menu_items()

    def _update_menu_items(self):
        """Динамически обновляет пункты меню в зависимости от наличия сохранения."""
        self.menu_items = [STRINGS.NEW_GAME]

        if self.game.has_saved_game():
            self.menu_items.append(STRINGS.CONTINUE)

        self.menu_items.extend(
            [
                STRINGS.LOAD_GAME,
                STRINGS.STATISTICS,
                STRINGS.SETTINGS,
                STRINGS.ABOUT,
                STRINGS.EXIT,
            ]
        )

        if self.menu_selection >= len(self.menu_items):
            self.menu_selection = 0

    def _reset_game_state(self):
        """Полностью сбрасывает состояние игры для новой игры."""
        from domain.base.backpack import Backpack
        from domain.base.data.entities.player import Player

        self.game.player = Player()
        self.game.player.backpack = Backpack()
        self.game.current_level_num = 1
        self.game.current_seed = int(time.time())
        self.game.opened_doors = []
        self.game.game_started = False
        self.game.statistics.reset_current_run()
        self.game._message = None

        self.game.reset_vision()
        self.game.is_3d_mode = False

        auto_save_path = (
            self.game.project_root
            / "data"
            / "repos"
            / "saves"
            / STRINGS.AUTO_SAVE_FILENAME
        )
        if auto_save_path.exists():
            with contextlib.suppress(Exception):
                auto_save_path.unlink()

    def _handle_select(self) -> bool:
        """Обработка выбора пункта меню."""
        selected = self.menu_items[self.menu_selection]

        if selected == STRINGS.NEW_GAME:
            self._reset_game_state()
            self.game.start_game()
            self.game.message = STRINGS.MESSAGE_GAME_IS_STARTED
            self.game.fsm.transition_to(GameState.EXPLORING)

        elif selected == STRINGS.CONTINUE:
            # Load latest save (autosave has priority)
            if self.game.load_last_save():
                self.game.fsm.transition_to(GameState.EXPLORING)
            else:
                self.game.message = STRINGS.LOAD_FAILED

        elif selected == STRINGS.LOAD_GAME:
            self.game.fsm.transition_to(GameState.LOAD_GAME)

        elif selected == STRINGS.STATISTICS:
            self.show_stats = True
            return True

        elif selected == STRINGS.ABOUT:
            self.game.fsm.transition_to(GameState.ABOUT)
            return True
        elif selected == STRINGS.STATISTICS:
            self.show_stats = True
            return True

        elif selected == STRINGS.SETTINGS:
            self.game.fsm.transition_to(GameState.SETTINGS)
            return True

        elif selected == STRINGS.ABOUT:
            self.game.fsm.transition_to(GameState.ABOUT)
            return True

        elif selected == STRINGS.EXIT:
            self.game.message = STRINGS.EXITING_GAME
            self.game.is_running = False
            return False

        return True

    def handle_input(self, action: GameKey) -> bool:
        """Обработка ввода в меню."""
        if self.show_stats:
            return self._handle_stats_input(action)

        self._update_menu_items()

        if action in (GameKey.KEY_W, GameKey.KEY_K):
            self.menu_selection = (self.menu_selection - 1) % len(self.menu_items)
            return True
        elif action in (GameKey.KEY_S, GameKey.KEY_J):
            self.menu_selection = (self.menu_selection + 1) % len(self.menu_items)
            return True
        elif action == GameKey.SELECT:
            return self._handle_select()
        elif action == GameKey.KEY_Q:
            self.game.message = STRINGS.EXITING_GAME
            self.game.is_running = False
            return False

        return True

    def _handle_stats_input(self, action: GameKey) -> bool:
        """Обработка ввода в режиме статистики."""
        if action in (GameKey.KEY_Q, GameKey.SELECT, GameKey.INVENTORY):
            self.show_stats = False
            return True
        return True

    def on_enter(self):
        """При входе в меню."""
        self.game.message = STRINGS.WELCOME_MESSAGE
        self.show_stats = False
        self._update_menu_items()

    def on_exit(self):
        """При выходе из меню."""

    def update(self) -> bool:
        """Обновление логики состояния."""
        return True
