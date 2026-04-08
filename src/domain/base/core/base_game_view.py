"""Базовый класс для всех представлений игры."""

import logging
from abc import ABC, abstractmethod

from domain.base.core.base_game import BaseGame
from domain.game.core.game import Game
from domain.game.state_machine.game_key import GameKey

logger = logging.getLogger(__name__)


class BaseGameView(ABC):
    """Абстрактный базовый класс для всех представлений игры."""

    def __init__(self, game: BaseGame):
        """Инициализация базового представления."""
        if game is None:
            self.game = Game()
            logger.warning("Создана новая игра по умолчанию (Game)")
        else:
            self.game = game
            logger.info(f"Используется переданная игра: {game.__class__.__name__}")
        logger.debug("BaseGameView инициализирован")

    def run(self):
        """Главный игровой цикл (шаблонный метод)."""
        logger.info("Запуск игрового цикла")
        self._before_game_loop()
        logger.debug("_before_game_loop выполнен")

        try:
            while self.game.is_running:
                self._render()
                action = self._get_input()
                if action is not None:
                    logger.debug(f"Получено действие: {action}")
                    should_continue = self.game.update(action)
                    logger.debug(
                        f"Результат обработки действия: should_continue={should_continue}"
                    )
                    if not should_continue:
                        logger.info("Игровой цикл завершён по запросу игры")
                        break
                else:
                    logger.debug("Нет действия (action = None)")
        except KeyboardInterrupt:
            logger.info("KeyboardInterrupt caught, shutting down...")
            self.game.is_running = False
        finally:
            self._after_game_loop()
            logger.debug("_after_game_loop выполнен")
            logger.info("Игровой цикл завершён")

    @staticmethod
    @abstractmethod
    def _before_game_loop():
        """Подготовка перед игровым циклом."""
        logger.debug("Вызов _before_game_loop (абстрактный метод)")

    @staticmethod
    def _after_game_loop():
        """Очистка после игрового цикла."""
        logger.debug("Вызов _after_game_loop (абстрактный метод)")

    @abstractmethod
    def _render():
        """Отрисовка игрового состояния."""
        logger.debug("Вызов _render (абстрактный метод)")

    @staticmethod
    def _get_input() -> GameKey:
        """Получение пользовательского ввода и преобразование в GameKey."""
        logger.debug("Вызов _get_input (абстрактный метод)")

    def get_action(key_code: int) -> GameKey:
        """Преобразует код клавиши в GameKey (общая логика)."""
        try:
            key_char = chr(key_code)
        except (ValueError, TypeError):
            logger.debug(f"Не удалось преобразовать код {key_code} в символ")
            return GameKey.NOPE

        for action in GameKey:
            if action.matches(key_char):
                logger.debug(
                    f"Клавиша '{key_char}' (код {key_code}) распознана как {action}"
                )
                return action

        logger.debug(f"Клавиша '{key_char}' (код {key_code}) не распознана")
        return GameKey.NOPE
