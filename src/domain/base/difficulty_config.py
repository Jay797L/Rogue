"""Конфигурация сложности игры."""

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class DifficultyConfig:
    """Загрузчик и менеджер конфигурации сложности."""

    _instance = None
    _config: dict[str, Any] = {}
    _config_path: Path | None = None

    def __new__(cls: type["DifficultyConfig"]) -> "DifficultyConfig":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._load_default_config()

    def _load_default_config(self) -> None:
        """Загружает конфигурацию по умолчанию."""
        self._config = {
            "treasure_rewards": {
                "base_treasure": 10,
                "elite_multiplier": 3,
                "boss_multiplier": 5,
                "level_scaling": 0.2,
            },
            "difficulty_curves": {
                "enemy_hp": "logarithmic",
                "enemy_damage": "linear",
                "enemy_count": "square_root",
                "item_quality": "logistic",
            },
            "base_values": {
                "enemy_hp": 50,
                "enemy_damage": 10,
                "enemies_per_room_min": 1,
                "enemies_per_room_max": 4,
                "items_per_room_min": 1,
                "items_per_room_max": 3,
            },
            "growth_rates": {
                "hp_growth": 0.15,
                "damage_growth": 0.12,
                "count_growth": 0.08,
                "map_scale_growth": 0.03,
            },
            "limits": {
                "max_hp_multiplier": 5.0,
                "max_damage_multiplier": 4.0,
                "max_count_multiplier": 3.0,
                "max_map_scale": 2.0,
                "max_elite_chance": 0.3,
                "max_boss_chance": 0.15,
            },
            "enemy_spawn_thresholds": {
                "zombie": 1,
                "ghost": 1,
                "ogr": 3,
                "snake_mage": 5,
                "vampire": 7,
                "mimik": 1,
            },
            "enemy_weights": {
                "zombie": 35,
                "ghost": 20,
                "ogr": 15,
                "snake_mage": 10,
                "vampire": 5,
                "mimik": 15,
            },
            "weight_modifiers": {
                "3": {"ogr": 10, "snake_mage": 5},
                "5": {"vampire": 15, "snake_mage": 10},
                "7": {"vampire": 20, "mimik": 10},
                "10": {"vampire": 25, "mimik": 20},
            },
            "elite_enemies": {
                "enabled": True,
                "start_level": 3,
                "base_chance": 0.05,
                "chance_growth": 0.01,
                "hp_multiplier": 1.5,
                "damage_multiplier": 1.3,
                "dexterity_multiplier": 1.2,
            },
            "mini_bosses": {
                "enabled": True,
                "start_level": 5,
                "base_chance": 0.02,
                "chance_growth": 0.005,
                "hp_multiplier": 2.5,
                "damage_multiplier": 2.0,
                "dexterity_multiplier": 1.5,
            },
            "player_power_weights": {
                "hp": 0.20,
                "strength": 0.35,
                "dexterity": 0.25,
                "scope": 0.10,
                "treasure": 0.10,
            },
            "max_stats": {
                "hp": 500,
                "strength": 500,
                "dexterity": 100,
                "scope": 30,
                "treasure": 10000,
            },
            "locked_doors": {
                "min_pairs": 1,
                "max_pairs": 3,
                "pairs_per_5_levels": 1,
            },
            "adaptive_difficulty": {
                "enabled": True,
                "player_power_influence": 0.5,
                "death_penalty": 0.1,
            },
        }

    def load_from_file(self, filepath: Path | str) -> bool:
        """Загружает конфигурацию из JSON файла."""
        filepath = Path(filepath)
        if not filepath.exists():
            logger.warning("Config file not found: {}", filepath)
            return False

        try:
            with open(filepath, encoding="utf-8") as f:
                user_config = json.load(f)
            self._update_nested_dict(self._config, user_config)
            self._config_path = filepath
            logger.info(f"Difficulty config loaded from {filepath}")
            return True
        except Exception as e:
            logger.error("Failed to load config: {}", e)
            return False

    def _update_nested_dict(self, target: dict, source: dict) -> None:
        """Рекурсивно обновляет словарь."""
        for key, value in source.items():
            if (
                key in target
                and isinstance(target[key], dict)
                and isinstance(value, dict)
            ):
                self._update_nested_dict(target[key], value)
            else:
                target[key] = value

    def save_to_file(self, filepath: Path | str) -> bool:
        """Сохраняет текущую конфигурацию в JSON файл."""
        filepath = Path(filepath)
        try:
            filepath.parent.mkdir(parents=True, exist_ok=True)
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(self._config, f, indent=2, ensure_ascii=False)
            logger.info("Config saved to {}", filepath)
            return True
        except Exception as e:
            logger.error("Failed to save config: {}", e)
            return False

    def get(self, key: str, default: Any | None = None) -> Any:
        """Получает значение из конфигурации по ключу."""
        keys = key.split(".")
        value = self._config
        for k in keys:
            if not isinstance(value, dict) or k not in value:
                return default
            value = value[k]
        return value

    def set(self, key: str, value: Any) -> None:
        """Устанавливает значение в конфигурации."""
        keys = key.split(".")
        target = self._config
        for k in keys[:-1]:
            if k not in target:
                target[k] = {}
            target = target[k]
        target[keys[-1]] = value

    def reload(self) -> bool:
        """Перезагружает конфигурацию из файла."""
        if self._config_path:
            return self.load_from_file(self._config_path)
        return False

    def get_elite_chance(self, level_num: int) -> float:
        """Возвращает шанс появления элитного врага."""
        elite_config = self.get("elite_enemies", {})
        if not elite_config.get("enabled", True):
            return 0.0

        start_level = elite_config.get("start_level", 3)
        if level_num < start_level:
            return 0.0

        base_chance = elite_config.get("base_chance", 0.05)
        growth = elite_config.get("chance_growth", 0.01)
        max_chance = self.get("limits.max_elite_chance", 0.3)

        chance = base_chance + (level_num - start_level) * growth
        return min(chance, max_chance)

    def get_boss_chance(self, level_num: int) -> float:
        """Возвращает шанс появления мини-босса."""
        boss_config = self.get("mini_bosses", {})
        if not boss_config.get("enabled", True):
            return 0.0

        start_level = boss_config.get("start_level", 5)
        if level_num < start_level:
            return 0.0

        base_chance = boss_config.get("base_chance", 0.02)
        growth = boss_config.get("chance_growth", 0.005)
        max_chance = self.get("limits.max_boss_chance", 0.15)

        chance = base_chance + (level_num - start_level) * growth
        return min(chance, max_chance)

    def get_map_scale(self, level_num: int) -> float:
        """Возвращает масштаб карты для уровня."""
        if level_num <= 1:
            return 1.0

        growth_rate = self.get("growth_rates.map_scale_growth", 0.03)
        max_scale = self.get("limits.max_map_scale", 2.0)

        scale = 1.0 + (level_num - 1) * growth_rate
        return min(scale, max_scale)


difficulty_config = DifficultyConfig()
