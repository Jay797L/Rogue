"""Settings state."""

from domain.game.state_machine.game_key import GameKey
from domain.game.state_machine.game_state import GameState
from presentation.settings_renderer import SettingsRenderer

from .base_state import GameStateBase


class SettingsState(GameStateBase):
    """Settings menu state."""

    def __init__(self, game):
        super().__init__(game)
        self.renderer = None
        self.music_enabled = True

    def handle_input(self, action: GameKey) -> bool:
        """Handle input in settings state."""
        if action == GameKey.KEY_M:
            self.music_enabled = not self.music_enabled
            if self.game.music_player:
                if self.music_enabled:
                    self.game.music_player.unpause()
                else:
                    self.game.music_player.pause()
            if self.game.settings_manager:
                self.game.settings_manager.set_music_enabled(self.music_enabled)
            if self.renderer:
                self.renderer.set_music_enabled(self.music_enabled)
                self.renderer.render()
            return True

        if action == GameKey.KEY_Q:
            self.game.fsm.transition_to(GameState.MENU)
            return True

        return True

    def on_enter(self):
        """Enter settings state."""
        game_view = self.game._game_view
        if game_view and game_view.stdscr:
            self.renderer = SettingsRenderer(game_view.stdscr)
            if self.game.settings_manager:
                self.music_enabled = self.game.settings_manager.get_music_enabled()
            elif self.game.music_player:
                self.music_enabled = self.game.music_player.is_playing
            else:
                self.music_enabled = True
            if self.game.music_player:
                if self.music_enabled and not self.game.music_player.is_playing:
                    self.game.music_player.unpause()
                elif not self.music_enabled and self.game.music_player.is_playing:
                    self.game.music_player.pause()
            self.renderer.set_music_enabled(self.music_enabled)
            self.renderer.render()
        else:
            self.renderer = None

    def on_exit(self):
        """Exit settings state."""
        self.renderer = None

    def update(self) -> bool:
        """Update settings state."""
        if self.renderer:
            self.renderer.render()
        return True
