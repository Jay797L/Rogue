"""Состояние загрузки сохранений."""

import json
import logging
from pathlib import Path

from domain.base.data.strings import STRINGS
from domain.game.state_machine.game_key import GameKey
from domain.game.state_machine.game_state import GameState

from .base_state import GameStateBase

logger = logging.getLogger(__name__)


class LoadGameState(GameStateBase):
    """Состояние выбора сохранения для загрузки."""

    def __init__(self, game):
        super().__init__(game)
        self.saves: list[tuple[Path, str]] = []
        self.selected_index = 0
        self.loading = False

    def _refresh_saves(self):
        """Обновляет список сохранений."""
        from data.managers.save_data import SaveManager

        save_manager = SaveManager(project_root=self.game.project_root)
        self.saves = save_manager.list_saves()

        if self.selected_index >= len(self.saves):
            self.selected_index = 0

    def _format_save_info(self, save_path: Path, timestamp: str) -> dict:
        """Форматирует информацию о сохранении для отображения."""
        try:
            with open(save_path, encoding="utf-8") as f:
                data = json.load(f)

            game_data = data.get("game_data", {})
            level_num = game_data.get("level_num", 1)

            if "T" in timestamp:
                date_part = timestamp.split("T", maxsplit=1)[0]
                time_part = timestamp.split("T")[1].split(".", maxsplit=1)[0]
                formatted_time = f"{date_part} {time_part}"
            else:
                formatted_time = timestamp

            is_auto = save_path.name == STRINGS.AUTO_SAVE_FILENAME
            save_type = "AUTO" if is_auto else "MANUAL"

            return {
                "level": level_num,
                "timestamp": formatted_time,
                "type": save_type,
                "is_auto": is_auto,
                "path": save_path,
            }
        except Exception as e:
            logger.error(f"Error reading save info: {e}")
            return {
                "level": "?",
                "timestamp": save_path.stem,
                "type": "UNKNOWN",
                "is_auto": False,
                "path": save_path,
            }

    def handle_input(self, action: GameKey) -> bool:
        """Обработка ввода в меню загрузки."""
        if self.loading:
            return True

        self._refresh_saves()

        if not self.saves:
            self.game.message = STRINGS.NO_SAVED_GAMES
            self.game.fsm.transition_to(GameState.MENU)
            return True

        if action in (GameKey.KEY_W, GameKey.KEY_K):
            self.selected_index = (self.selected_index - 1) % len(self.saves)
            return True
        elif action in (GameKey.KEY_S, GameKey.KEY_J):
            self.selected_index = (self.selected_index + 1) % len(self.saves)
            return True
        elif action == GameKey.SELECT:
            self.loading = True
            save_path = self.saves[self.selected_index][0]
            if self.game.load_game(save_path):
                self.game.fsm.transition_to(GameState.EXPLORING)
            else:
                self.game.message = STRINGS.LOAD_ERROR
                self.loading = False
            return True
        elif action in (GameKey.KEY_Q, GameKey.BACKSPACE):
            self.game.fsm.transition_to(GameState.MENU)
            return True

        return True

    def get_saves_info(self) -> list[dict]:
        """Возвращает список сохранений с информацией для рендерера."""
        return [self._format_save_info(path, ts) for path, ts in self.saves]

    def on_enter(self):
        """При входе в состояние загрузки."""
        self.selected_index = 0
        self.loading = False
        self._refresh_saves()
        self.game.message = STRINGS.SELECT_SAVE_TO_LOAD

    def on_exit(self):
        """При выходе из состояния загрузки."""
        self.loading = False

    def update(self) -> bool:
        """Обновление логики состояния."""
        return True
