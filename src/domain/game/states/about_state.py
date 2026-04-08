"""Состояние экрана About с логотипом и прокручиваемым текстом."""

import time

from domain.game.state_machine.game_key import GameKey
from domain.game.state_machine.game_state import GameState
from presentation.about_renderer import AboutRenderer

from .base_state import GameStateBase


class AboutState(GameStateBase):
    """Состояние экрана About с логотипом и прокручиваемым текстом."""

    def __init__(self, game):
        super().__init__(game)
        self.renderer = None
        self.start_time = 0.0

    def handle_input(self, action: GameKey) -> bool:
        """Обработка ввода в состоянии About."""

        if action in (GameKey.KEY_W, GameKey.KEY_K):
            if self.renderer:
                self.renderer.scroll_up()

                current_time = time.time() - getattr(
                    self.game._game_view, "start_time", 0
                )
                self.renderer.render(current_time)
            return True

        if action in (GameKey.KEY_S, GameKey.KEY_J):
            if self.renderer:
                self.renderer.scroll_down()

                current_time = time.time() - getattr(
                    self.game._game_view, "start_time", 0
                )
                self.renderer.render(current_time)
            return True

        if action == GameKey.KEY_Q:
            self.game.fsm.transition_to(GameState.MENU)
            return True

        return True

    def on_enter(self):
        """При входе в состояние About."""

        game_view = self.game._game_view
        if game_view and game_view.stdscr:
            self.renderer = AboutRenderer(game_view.stdscr)
            self.start_time = time.time() - getattr(game_view, "start_time", 0)

            self.renderer.render(self.start_time)
        else:
            self.renderer = None

    def on_exit(self):
        """При выходе из состояния About."""
        self.renderer = None

    def update(self) -> bool:
        """Обновление логики состояния - перерисовка."""

        if self.renderer:
            current_time = time.time() - getattr(self.game._game_view, "start_time", 0)
            self.renderer.render(current_time)
        return True
