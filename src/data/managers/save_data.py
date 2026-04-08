# data/save_data.py
"""Модуль для работы с сохранениями игры."""

import json
import logging
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from domain.base.backpack import Backpack
from domain.base.core.base_item import Item
from domain.base.data import STRINGS

# Принудительно импортируем item_presets для регистрации предметов
from domain.base.data.entities import Player

# Теперь можно импортировать get_item_by_name
from domain.base.data.register_item import get_item_by_name
from domain.base.utils.point import Point

logger = logging.getLogger(__name__)


@dataclass
class PlayerStateData:
    """Состояние игрока для сохранения."""

    point: dict[str, int]  # {y: int, x: int}
    hp: int
    max_hp: int
    strength: int
    dexterity: int
    scope: int
    backpack: dict[str, Any]  # сериализованный рюкзак
    name: str = "player"


@dataclass
class LevelStateData:
    """Состояние уровня для сохранения."""

    seed: int  # сид для генерации уровня
    level_num: int  # номер уровня
    player_state: PlayerStateData
    opened_doors: list[str] = field(default_factory=list)


@dataclass
class SaveData:
    """Полные данные сохранения."""

    save_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    version: str = "1.0"
    game_data: LevelStateData | None = None


class SaveManager:
    """Менеджер сохранений игры."""

    def __init__(self, project_root: Path | None = None):
        """Инициализация менеджера сохранений.

        Args:
            project_root: Корневая директория проекта (где находится main.py)
        """
        self.project_root = project_root or Path.cwd()
        self.SAVE_DIR = self.project_root / "saves"
        self.SAVE_DIR.mkdir(exist_ok=True)
        logger.info(f"Директория сохранений: {self.SAVE_DIR}")

    def serialize_backpack(self, backpack: Backpack) -> dict[str, Any]:
        """Сериализует рюкзак в словарь."""

        def serialize_item(item: Item) -> dict[str, Any]:
            return {
                "name": item.name,
                "category": item.category.value,
                "strength": item.strength,
                "attribute": item.attribute,
                "specification": item.specification,
            }

        return {
            "eat": [serialize_item(item) for item in backpack.eat],
            "elixirs": [serialize_item(item) for item in backpack.elixirs],
            "scrolls": [serialize_item(item) for item in backpack.scrolls],
            "weapon": [serialize_item(item) for item in backpack.weapon],
            "treasure": backpack.treasure,
            "max_capacity": backpack.max_capacity,
            "equipped_weapon_index": backpack.equipped_weapon_index,
        }

    def deserialize_backpack(self, data: dict[str, Any]) -> Backpack:
        """Восстанавливает рюкзак из словаря."""
        backpack = Backpack()
        backpack.treasure = data.get("treasure", 0)
        backpack.max_capacity = data.get("max_capacity", 9)
        backpack.equipped_weapon_index = data.get("equipped_weapon_index", 0)

        # Восстанавливаем предметы
        for category_name, items_data in [
            ("eat", backpack.eat),
            ("elixirs", backpack.elixirs),
            ("scrolls", backpack.scrolls),
            ("weapon", backpack.weapon),
        ]:
            for item_data in data.get(category_name, []):
                item_class = get_item_by_name(item_data["name"])
                if item_class:
                    item = item_class()
                    item.strength = item_data.get("strength", item.strength)
                    item.attribute = item_data.get("attribute", item.attribute)
                    if "specification" in item_data:
                        item.specification = item_data["specification"]
                    items_data.append(item)
                    logger.debug(f"Восстановлен предмет: {item.name}")
                else:
                    logger.warning(f"Предмет {item_data['name']} не найден в реестре")

        return backpack

    def serialize_player_state(self, player: Player) -> PlayerStateData:
        """Сериализует состояние игрока."""
        return PlayerStateData(
            point={"y": player.point.y, "x": player.point.x},
            hp=player.hp,
            max_hp=player.max_hp,
            strength=player.strength,
            dexterity=player.dexterity,
            scope=player.scope,
            backpack=self.serialize_backpack(player.backpack),
            name=player.name,
        )

    def deserialize_player_state(self, data: PlayerStateData, player: Player) -> None:
        """Восстанавливает состояние игрока."""
        player.point = Point(data.point["y"], data.point["x"])
        player.hp = data.hp
        player.max_hp = data.max_hp
        player.strength = data.strength
        player.dexterity = data.dexterity
        player.scope = data.scope
        player.backpack = self.deserialize_backpack(data.backpack)

    def save(
        self, seed: int, level_num: int, player: Player, is_auto: bool = False
    ) -> Path:
        """Сохраняет текущее состояние игры.

        Args:
            seed: Сид для генерации уровня
            level_num: Номер текущего уровня
            player: Игрок
            is_auto: Является ли сохранение автоматическим

        Returns:
            Path: Путь к файлу сохранения
        """
        player_state = self.serialize_player_state(player)
        level_state = LevelStateData(
            seed=seed,
            level_num=level_num,
            player_state=player_state,
        )
        save_data = SaveData(game_data=level_state)

        # Генерируем имя файла
        if is_auto:
            filename = STRINGS.AUTO_SAVE_FILENAME
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = STRINGS.SAVE_FILENAME_PATTERN.format(timestamp)

        filepath = self.SAVE_DIR / filename

        # Сохраняем в JSON
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(asdict(save_data), f, indent=2, ensure_ascii=False)

        logger.info(f"Игра сохранена в {filepath}")
        return filepath

    def get_latest_save(self) -> Path | None:
        """Возвращает путь к последнему сохранению (приоритет у автосохранения)."""
        saves = self.list_saves()
        if not saves:
            return None

        # Проверяем наличие автосохранения
        auto_save_path = self.SAVE_DIR / STRINGS.AUTO_SAVE_FILENAME
        if auto_save_path.exists():
            return auto_save_path

        # Иначе возвращаем последнее ручное сохранение
        return saves[0][0]

    def load(self, filepath: Path | str) -> SaveData | None:
        """Загружает сохранение из файла."""
        filepath = Path(filepath)
        if not filepath.exists():
            logger.error(f"Файл сохранения {filepath} не найден")
            return None

        try:
            with open(filepath, encoding="utf-8") as f:
                data = json.load(f)

            # Восстанавливаем структуру
            game_data = data.get("game_data")
            if game_data:
                game_data = LevelStateData(
                    seed=game_data["seed"],
                    level_num=game_data["level_num"],
                    player_state=PlayerStateData(**game_data["player_state"]),
                )

            return SaveData(
                save_id=data["save_id"],
                timestamp=data["timestamp"],
                version=data["version"],
                game_data=game_data,
            )
        except Exception as e:
            logger.exception(f"Ошибка загрузки сохранения: {e}")
            return None

    def list_saves(self) -> list[tuple[Path, str]]:
        """Возвращает список доступных сохранений.

        Returns:
            list[tuple[Path, str]]: Список (путь, метка времени)
        """
        saves = []
        pattern = STRINGS.SAVE_FILENAME_PATTERN.format("*")
        for filepath in sorted(self.SAVE_DIR.glob(pattern), reverse=True):
            try:
                with open(filepath, encoding="utf-8") as f:
                    data = json.load(f)
                timestamp = data.get("timestamp", filepath.stem)
                saves.append((filepath, timestamp))
            except Exception:
                saves.append((filepath, filepath.stem))
        return saves
