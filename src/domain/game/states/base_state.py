"""Базовый класс для всех состояний игры."""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from domain.game.state_machine.game_key import GameKey

if TYPE_CHECKING:
    pass


class GameStateBase(ABC):
    """Базовый класс для состояния игры."""

    def __init__(self, game: "BaseGame"):
        self.game = game

    @abstractmethod
    def handle_input(self, action: GameKey) -> bool:
        """Обработка ввода в данном состоянии."""

    @abstractmethod
    def on_enter(self):
        """Вызывается при входе в состояние."""

    @abstractmethod
    def on_exit(self):
        """Вызывается при выходе из состояния."""

    def update(self) -> bool:
        """Обновление логики состояния (вызывается каждый кадр)."""
        return True
