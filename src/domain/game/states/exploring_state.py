"""Состояние исследования мира."""

from domain.base.data.strings import STRINGS
from domain.game.state_machine.game_key import GameKey
from domain.game.state_machine.game_state import GameState

from .base_state import GameStateBase


class ExploringState(GameStateBase):
    """Состояние исследования мира."""

    def handle_input(self, action: GameKey) -> bool:
        """Обработка ввода в режиме исследования."""
        if action in (
            GameKey.KEY_W,
            GameKey.KEY_S,
            GameKey.KEY_A,
            GameKey.KEY_D,
            GameKey.KEY_K,
            GameKey.KEY_J,
            GameKey.KEY_H,
            GameKey.KEY_L,
        ):
            return self.game.handle_move(action)
        if action == GameKey.INVENTORY:
            return self.game.handle_inventory_open(action)
        if action == GameKey.SAVE_GAME:
            return self.game.save_game()
        if action == GameKey.KEY_V:
            self.game.switch_vision_mode(True)
            self.game.fsm.transition_to(GameState.EXPLORING_3D)
            return True
        if action == GameKey.KEY_Q:
            self.game.save_game(is_auto=True)
            self.game.message = STRINGS.GAME_SAVED_RETURN
            self.game.fsm.transition_to(GameState.MENU)
            return True

        return True

    def on_enter(self):
        """При входе в режим исследования."""
        if self.game.is_3d_mode:
            self.game.switch_vision_mode(False)

    def on_exit(self):
        """При выходе из режима исследования."""

    def update(self) -> bool:
        """Обновление логики исследования (враги, эффекты и т.д.)."""
        if self.game and self.game.player.hp <= 0:
            self.game.game_over()
        return True
