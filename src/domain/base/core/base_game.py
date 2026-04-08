"""Базовый класс для всех игровых режимов."""

import time
from abc import abstractmethod
from pathlib import Path

from data.managers.save_data import SaveManager
from data.managers.statistics import StatisticsManager
from domain.base.backpack import Backpack
from domain.base.core.base_vision import BaseVision
from domain.base.core.item_category import ItemCategory
from domain.base.core.pixel import Pixel
from domain.base.data.cell_presets import LockedDoorCell
from domain.base.data.consts import CONST
from domain.base.data.entities.player import Player
from domain.base.data.strings import STRINGS
from domain.base.difficulty import difficulty_calculator
from domain.game.core.direction_mapping import get_direction_from_key
from domain.game.state_machine.fsm import FiniteStateMachine
from domain.game.state_machine.game_key import GameKey
from domain.game.state_machine.game_state import GameState
from domain.map.level_generation.level import Level
from domain.vision.vision_fog_of_war import FogOfWarVision
from domain.vision.vision_pseudo3d import Pseudo3DVision


class BaseGame:
    """Базовый класс для Game и Lab."""

    def __init__(self, vision_class=None, project_root: Path | None = None):
        self.is_running = True
        self.player = Player()
        self._message = None
        self.vision_class: BaseVision = vision_class
        self._vision_instance = None
        self.level: Level = None
        self._current_category: ItemCategory | None = None
        self.game_started = False
        self.get_direction_from_key = get_direction_from_key
        self.project_root = project_root or Path.cwd()
        self.opened_doors: list[str] = []
        self.fsm = FiniteStateMachine(self)
        self.player_direction = 0
        self.is_3d_mode = False
        self.current_level_num = 1
        self.current_seed: int | None = None
        self.statistics = StatisticsManager(project_root=project_root)
        self.screen_width = 70
        self.screen_height = 40
        self.music_player = None
        self.settings_manager = None
        self.music_player = None
        self.settings_manager = None
        self.screen_width = 70
        self.screen_height = 40
        self.music_player = None

        self._last_level_completed = 0

    def record_move(self):
        """Записывает перемещение."""
        self.statistics.record_cell_moved()

    def record_enemy_killed(self):
        """Записывает убийство врага."""
        self.statistics.record_enemy_killed()

    def record_treasure(self, amount: int):
        """Записывает получение сокровищ."""
        self.statistics.record_treasure(amount)

    def record_level_completed(self):
        """Записывает завершение уровня."""
        self.statistics.record_level_completed(self.current_level_num)
        if self.current_level_num >= CONST.MAX_LEVELS:
            self.statistics.record_victory()

    def finish_run(self):
        """Завершает текущее прохождение."""
        self.statistics.finish_run()

        self.player.backpack = Backpack()

    def load_game(self, save_path: Path | None = None) -> bool:
        """Загрузить игру."""
        save_manager = SaveManager(project_root=self.project_root)

        if save_path is None:
            save_path = save_manager.get_latest_save()
            if save_path is None:
                self.message = STRINGS.NO_SAVED_GAMES
                return False

        save_data = save_manager.load(save_path)
        if save_data is None or save_data.game_data is None:
            self.message = STRINGS.LOAD_ERROR
            return False

        self.current_seed = save_data.game_data.seed
        self.current_level_num = save_data.game_data.level_num
        self.opened_doors = save_data.game_data.opened_doors
        save_manager.deserialize_player_state(
            save_data.game_data.player_state, self.player
        )

        self.reset_vision()

        self._initialize_level(
            difficulty=self.current_level_num,
            seed=self.current_seed,
            opened_doors=self.opened_doors,
        )
        self.level.map_manager._game = self
        self.game_started = True
        self.message = STRINGS.GAME_LOADED.format(self.current_level_num)
        self._setup_vision()
        return True

    @property
    def message(self):
        tmp = self._message.value if hasattr(self._message, "value") else self._message
        self._message = None
        return tmp

    @message.setter
    def message(self, value: str):
        self._message = value

    def update(self, action: GameKey) -> bool:
        """Обработка действий – общая для всех режимов."""
        res = self.fsm.process_action(action=action)
        self.fsm.update()

        if self.game_started and self.fsm.current_state in (
            GameState.EXPLORING,
            GameState.EXPLORING_3D,
        ):
            self._auto_save()

        return res

    def _auto_save(self):
        """Автоматическое сохранение игры."""
        if self.level is not None and self.current_seed is not None:
            save_manager = SaveManager(project_root=self.project_root)
            save_manager.save(
                seed=self.current_seed,
                level_num=self.current_level_num,
                player=self.player,
                is_auto=True,
            )

    def save_game(self, is_auto: bool = False) -> bool:
        """Сохранить игру."""
        if self.level is None or self.current_seed is None:
            if not is_auto:
                self.message = STRINGS.SAVE_ERROR
            return False

        save_manager = SaveManager(project_root=self.project_root)
        filepath = save_manager.save(
            seed=self.current_seed,
            level_num=self.current_level_num,
            player=self.player,
            is_auto=is_auto,
        )
        if not is_auto:
            self.message = STRINGS.GAME_SAVED.format(filepath.name)
        return True

    def has_saved_game(self) -> bool:
        """Проверяет наличие сохранённой игры."""
        save_manager = SaveManager(project_root=self.project_root)
        saves = save_manager.list_saves()
        return len(saves) > 0

    def load_last_save(self) -> bool:
        """Загружает последнее сохранение."""
        save_manager = SaveManager(project_root=self.project_root)
        saves = save_manager.list_saves()
        if not saves:
            self.message = STRINGS.NO_SAVED_GAMES
            return False

        return self.load_game(saves[0][0])

    def handle_move(self, action: GameKey) -> bool:
        """Общая логика движения."""
        direction = self.get_direction_from_key(action)

        self.record_move()

        self.level.enemy_manager.player_desision(direction)
        self.level.enemy_manager.update(game=self)
        self.level.enemy_manager.effects_apply()
        self.level.enemy_manager.max_hp_check(self.player)
        if self.player.point == self.level.exit_point:
            self.next_level()
        return True

    def handle_inventory_open(self, action: GameKey) -> bool:
        """Открыть инвентарь."""
        self.fsm.transition_to(GameState.INVENTORY)
        return True

    def get_map(self) -> list[Pixel]:
        """Возвращает карту через установленный класс видения."""
        if self._vision_instance is None:
            raise NotImplementedError(
                "Subclasses must implement _setup_vision or override get_map"
            )
        return self._vision_instance()

    @property
    def get_cam(self) -> tuple[int, int]:
        if self._vision_instance is None:
            raise NotImplementedError(
                "Subclasses must implement _setup_vision or override get_map"
            )
        return self._vision_instance.get_cam

    def _setup_vision(self):

        if not self._2d_vision_instance:
            self._2d_vision_instance = FogOfWarVision(
                map_manager=self.level.map_manager, character_of_view=self.player
            )

            self._2d_vision_instance.take_all()

        if self.is_3d_mode and not self._3d_vision_instance:
            self._3d_vision_instance = Pseudo3DVision(
                map_manager=self.level.map_manager,
                character_of_view=self.player,
                direction=self.player_direction,
                minimap_vision=self._2d_vision_instance,
                screen_width=self.screen_width,
                screen_height=self.screen_height,
            )

        self._vision_instance = (
            self._3d_vision_instance if self.is_3d_mode else self._2d_vision_instance
        )
        self._vision_instance.character_of_view = self.player
        self._vision_instance.map_manager = self.level.map_manager

    def reset_vision(self):
        """Сбрасывает vision-объекты для пересоздания при смене уровня."""
        self._2d_vision_instance = None
        self._3d_vision_instance = None
        self._vision_instance = None

    def update_screen_size(self, width: int, height: int):
        """Обновляет размер экрана для 3D вида."""

        self.screen_width = width
        self.screen_height = height

        if self.is_3d_mode and self._3d_vision_instance is not None:
            if hasattr(self._3d_vision_instance, "update_screen_dimensions"):
                self._3d_vision_instance.update_screen_dimensions(width, height)

    def switch_vision_mode(self, enable_3d: bool):
        """Переключает между 2D и 3D режимами без полной реинициализации."""
        if enable_3d == self.is_3d_mode:
            return

        self.is_3d_mode = enable_3d

        if self.is_3d_mode:
            if self._3d_vision_instance is None:
                self._3d_vision_instance = Pseudo3DVision(
                    map_manager=self.level.map_manager,
                    character_of_view=self.player,
                    direction=self.player_direction,
                    minimap_vision=self._2d_vision_instance,
                    screen_width=self.screen_width,
                    screen_height=self.screen_height,
                )
            self._vision_instance = self._3d_vision_instance

            if hasattr(self._vision_instance, "set_direction"):
                self._vision_instance.set_direction(self.player_direction)
        else:
            if self._2d_vision_instance is None:
                self._2d_vision_instance = FogOfWarVision(
                    map_manager=self.level.map_manager, character_of_view=self.player
                )
                self._2d_vision_instance.take_all()
            self._vision_instance = self._2d_vision_instance

        self._vision_instance.character_of_view = self.player
        self._vision_instance.map_manager = self.level.map_manager

    @abstractmethod
    def _initialize_level(self):
        """Заполняет self.map_manager, устанавливает позицию игрока и врагов."""

    def start_game(self):
        """Запускает новую игру (должна быть уже сброшена)."""
        if not self.game_started:
            self._initialize_level()
            self._setup_vision()
            self.game_started = True

    def game_over(self, is_victory: bool = False):
        """Завершение игры.

        Args:
            is_victory: True если игрок победил, False если умер
        """
        if is_victory:
            self.message = STRINGS.VICTORY
        else:
            self.message = STRINGS.GAME_OVER
        self.finish_run()

        self.fsm.transition_to(GameState.GAME_OVER, is_victory=is_victory)

    def next_level(self):
        """Переход на следующий уровень с сохранением прогресса."""
        self.record_level_completed()

        self.current_level_num += 1

        if self.current_level_num > CONST.MAX_LEVELS:
            self.game_over(is_victory=True)
            return

        player_power = difficulty_calculator.calculate_player_power(self.player)
        next_scale = difficulty_calculator.get_map_scale(self.current_level_num)

        self.message = self.message = STRINGS.LEVEL_UP_MESSAGE.format(
            self.current_level_num,
            int((self.current_level_num - 1) * 8),
            int(player_power * 100),
            next_scale,
        )

        self.reset_vision()

        self._initialize_level(difficulty=self.current_level_num)

        self._setup_vision()

    def open_door(self, door_id: str) -> bool:
        if door_id in self.opened_doors:
            return False
        self.opened_doors.append(door_id)
        if self.level and self.level.map_manager:
            for point, cell in self.level.map_manager._content.items():
                if isinstance(cell, LockedDoorCell) and cell.door_id == door_id:
                    del self.level.map_manager[point]
                    self.message = STRINGS.DOOR_OPENED
                    return True
        return False

    def set_music_player(self, music_player):
        """Устанавливает музыкальный плеер."""
        self.music_player = music_player

    def set_music_player(self, music_player):
        """Устанавливает музыкальный плеер."""
        self.music_player = music_player

    def set_settings_manager(self, settings_manager):
        """Устанавливает менеджер настроек."""
        self.settings_manager = settings_manager

    def reset_game(self):
        """Полностью сбрасывает игру для нового старта."""

        self.player = Player()
        self.player.backpack = Backpack()

        self.current_level_num = 1
        self.current_seed = int(time.time())
        self.opened_doors = []
        self.game_started = False
        self._message = None

        self.statistics.reset_current_run()

        if hasattr(self, "fsm"):
            self.fsm.transition_to(GameState.MENU)
