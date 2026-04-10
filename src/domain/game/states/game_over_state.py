import logging

from domain.base.data.strings import STRINGS
from domain.game.state_machine.game_key import GameKey
from domain.game.state_machine.game_state import GameState

from .base_state import GameStateBase


class GameOverState(GameStateBase):
    """Состояние конца игры."""

    def __init__(self, game):
        super().__init__(game)
        self.waiting_for_input = True
        self.is_victory = False
        self.completed_run = None

    def on_enter(self, is_victory: bool = False, completed_run=None):
        """При входе в состояние конца игры."""
        self.waiting_for_input = True
        self.is_victory = is_victory
        self.completed_run = completed_run

        if self.is_victory:
            self.game.message = STRINGS.VICTORY
        else:
            self.game.message = STRINGS.GAME_OVER_TITLE

        # finish_run is already called in BaseGame.game_over, do not call again
        self._delete_auto_save()

        if hasattr(self.game, "_game_view") and self.game._game_view:
            try:
                stdscr = getattr(self.game._game_view, "stdscr", None)
                if stdscr:
                    stdscr.clear()
                    stdscr.refresh()
            except Exception:
                pass

    def handle_input(self, action: GameKey) -> bool:
        """Обработка ввода при конце игры."""
        if not self.waiting_for_input:
            return True

        if action == GameKey.KEY_Q:
            self.waiting_for_input = False
            self.game.fsm.transition_to(GameState.MENU)
            return True

        return True

    def _delete_auto_save(self):
        """Удаляет файл автосохранения после завершения игры."""

        auto_save_path = (
            self.game.project_root
            / "data"
            / "repos"
            / "saves"
            / STRINGS.AUTO_SAVE_FILENAME
        )
        if auto_save_path.exists():
            auto_save_path.unlink()
            logging.info("Auto-save deleted after game over")

    def on_exit(self):
        """При выходе из состояния конца игры."""
        self.waiting_for_input = True
